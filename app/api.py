# app/api.py
from __future__ import annotations

from pathlib import Path
import json

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.load_data import load_cpt, load_icd10
from app.quiz import build_quiz
from app.search import free_search
from app.ai_simple import generate_ai_questions


app = FastAPI(title="Tarmeez", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent  # .../app
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR.parent / "data"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

CPT_JSON = DATA_DIR / "cpt.json"
ICD_JSON = DATA_DIR / "icd10.json"


# Load data once
try:
    CPT_DF = load_cpt()
except Exception as e:
    CPT_DF = None
    print("[CPT] load failed:", e)

try:
    ICD_DF = load_icd10()
except Exception as e:
    ICD_DF = None
    print("[ICD] load failed:", e)


def _get_df(kind: str):
    kind = (kind or "").lower()
    if kind == "cpt":
        if CPT_DF is None:
            raise HTTPException(status_code=500, detail="CPT data not loaded")
        return CPT_DF, "cpt"
    if kind in ("icd", "icd10"):
        if ICD_DF is None:
            raise HTTPException(status_code=500, detail="ICD data not loaded")
        return ICD_DF, "icd"
    raise HTTPException(status_code=400, detail="kind must be 'cpt' or 'icd' (or 'icd10')")


@app.get("/status", response_class=JSONResponse)
def status():
    return {
        "status": "ok",
        "cpt_rows": 0 if CPT_DF is None else int(CPT_DF.shape[0]),
        "icd_rows": 0 if ICD_DF is None else int(ICD_DF.shape[0]),
        "has_cpt_tree": CPT_JSON.exists(),
        "has_icd_tree": ICD_JSON.exists(),
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Tarmeez"})


@app.get("/cpt", response_class=HTMLResponse)
def cpt_page(request: Request):
    return templates.TemplateResponse("cpt.html", {"request": request, "title": "CPT Search"})


@app.get("/icd10", response_class=HTMLResponse)
def icd_page(request: Request):
    return templates.TemplateResponse("icd10.html", {"request": request, "title": "ICD-10 Search"})


@app.get("/dictionary", response_class=HTMLResponse)
def dictionary_page(request: Request):
    return templates.TemplateResponse("dictionary.html", {"request": request, "title": "Dictionary"})


@app.get("/quiz", response_class=HTMLResponse)
def quiz_home(request: Request):
    return templates.TemplateResponse("quiz_home.html", {"request": request, "title": "Quiz"})


@app.get("/quiz/run/{kind}", response_class=HTMLResponse)
def quiz_run(request: Request, kind: str, n: int = 10, ui_lang: str = "en"):
    kind = (kind or "").lower()
    if kind == "icd10":
        kind = "icd"
    if kind not in ("cpt", "icd"):
        kind = "cpt"

    return templates.TemplateResponse(
        "quiz_run.html",
        {
            "request": request,
            "title": f"{kind.upper()} Quiz",
            "kind": kind,
            "kind_upper": ("ICD (Diagnosis)" if kind == "icd" else "CPT"),
            "n": n,
            "ui_lang": ui_lang,
        },
    )


@app.get("/cases", response_class=HTMLResponse)
def cases_home(request: Request):
    return templates.TemplateResponse(
        "cases_home.html",
        {"request": request, "title": "Cases"},
    )


@app.get("/cases/run/{kind}", response_class=HTMLResponse)
def cases_run(request: Request, kind: str, n: int = 10, ui_lang: str = "en"):
    kind = (kind or "").lower()
    if kind == "icd10":
        kind = "icd"
    if kind not in ("cpt", "icd"):
        kind = "cpt"

    return templates.TemplateResponse(
        "cases_run.html",
        {
            "request": request,
            "title": f"{kind.upper()} Cases",
            "kind": kind,
            "kind_upper": ("ICD (Diagnosis)" if kind == "icd" else "CPT"),
            "n": n,
            "ui_lang": ui_lang,
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": "About"})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})


@app.get("/account", response_class=HTMLResponse)
def account_page(request: Request):
    return templates.TemplateResponse("account.html", {"request": request, "title": "Account"})


@app.get("/notes", response_class=HTMLResponse)
def notes_page(request: Request):
    return templates.TemplateResponse("notes.html", {"request": request, "title": "Notes"})


# ---------------- TREE (Dictionary UI) ----------------
@app.get("/tree/cpt", response_class=JSONResponse)
def tree_cpt():
    if not CPT_JSON.exists():
        return []
    return json.loads(CPT_JSON.read_text(encoding="utf-8"))


@app.get("/tree/icd", response_class=JSONResponse)
def tree_icd():
    if not ICD_JSON.exists():
        return []
    return json.loads(ICD_JSON.read_text(encoding="utf-8"))


# ---------------- DETAILS (Option 1) ----------------
@app.get("/api/code/{kind}/{code}", response_class=JSONResponse)
def code_details(kind: str, code: str):
    df, k = _get_df(kind)
    code = (code or "").strip()

    hit = df[df["code"].astype(str) == code]
    if hit.empty:
        raise HTTPException(status_code=404, detail="Code not found")

    r = hit.iloc[0].to_dict()

    if k == "icd":
        return {
            "kind": "icd",
            "code": r.get("code", ""),
            "description": r.get("description", ""),
            "meta": {
                "chapter_no": r.get("chapter_no", ""),
                "chapter": r.get("chapter", ""),
                "classification": r.get("classification", ""),
                "block_no": r.get("block_no", ""),
                "block": r.get("block", ""),
                "range": r.get("range", ""),
            },
        }

    return {
        "kind": "cpt",
        "code": r.get("code", ""),
        "description": r.get("description", ""),
        "meta": {
            "category_no": r.get("category_no", ""),
            "category": r.get("category", ""),
            "section_no": r.get("section_no", ""),
            "section": r.get("section", ""),
            "range": r.get("range", ""),
        },
    }


# ---------------- Classic Quiz API ----------------
@app.get("/api/quiz/{kind}", response_class=JSONResponse)
def api_quiz(kind: str, n: int = 10, difficulty: str = "medium"):
    df, k = _get_df(kind)
    return build_quiz(df, k, n=n, difficulty=difficulty)


# ---------------- AI Quiz & Cases (Option 4) ----------------
@app.get("/api/ai/quiz/{kind}", response_class=JSONResponse)
def api_ai_quiz(
    kind: str,
    n: int = 10,
    chapter: str = "",
    block: str = "",
    category: str = "",
    section: str = "",
    range: str = "",
):
    df, k = _get_df(kind)
    filters = {
        "chapter": chapter,
        "block": block,
        "category": category,
        "section": section,
        "range": range,
    }
    return generate_ai_questions(df, k, n=n, mode="quiz", filters=filters)


@app.get("/api/ai/cases/{kind}", response_class=JSONResponse)
def api_ai_cases(
    kind: str,
    n: int = 10,
    chapter: str = "",
    block: str = "",
    category: str = "",
    section: str = "",
    range: str = "",
):
    df, k = _get_df(kind)
    filters = {
        "chapter": chapter,
        "block": block,
        "category": category,
        "section": section,
        "range": range,
    }
    return generate_ai_questions(df, k, n=n, mode="case", filters=filters)


# ---------------- Search APIs (keep) ----------------
@app.get("/search/cpt", response_class=JSONResponse)
def search_cpt(q: str = Query("", min_length=0), limit: int = 10):
    if CPT_DF is None:
        raise HTTPException(status_code=500, detail="CPT data not loaded")
    return {"query": q, "results": free_search(CPT_DF, q, limit=limit, kind="cpt")}


@app.get("/search/icd", response_class=JSONResponse)
def search_icd(q: str = Query("", min_length=0), limit: int = 10):
    if ICD_DF is None:
        raise HTTPException(status_code=500, detail="ICD data not loaded")
    return {"query": q, "results": free_search(ICD_DF, q, limit=limit, kind="icd")}

@app.get("/quiz/run/{kind}", response_class=HTMLResponse)
def quiz_run(request: Request, kind: str, n: int = 10, difficulty: str = "medium"):
    return templates.TemplateResponse(
        "quiz_run.html",
        {
            "request": request,
            "title": "Quiz",
            "kind": kind,
            "n": n,
            "difficulty": difficulty,
        },
    )


@app.get("/cases/run/{kind}", response_class=HTMLResponse)
def cases_run(request: Request, kind: str, n: int = 10):
    return templates.TemplateResponse(
        "cases_run.html",
        {
            "request": request,
            "title": "Cases",
            "kind": kind,
            "n": n,
        },
    )
