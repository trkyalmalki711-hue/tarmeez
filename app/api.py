# app/api.py
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ----------------------------
# Imports from your project
# ----------------------------
# Loaders (your load_data.py may have different function names)
try:
    from app.load_data import load_cpt, load_icd10
except ImportError:
    # fallback names (just in case your function names differ)
    try:
        from app.load_data import load_cpt, load_icd
        load_icd10 = load_icd  # alias
    except ImportError as e:
        raise ImportError(
            "Could not import loaders. Make sure app/load_data.py has load_cpt and load_icd10 (or load_icd)."
        ) from e

# Quiz builder
from app.quiz import build_quiz

# Search (free search)
try:
    from app.search import free_search
except ImportError as e:
    raise ImportError(
        "Could not import free_search. Make sure app/search.py defines free_search(df, q, limit, kind)."
    ) from e


# ----------------------------
# App setup
# ----------------------------
app = FastAPI(title="Tarmeez", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent  # .../app
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ----------------------------
# Load data once at startup
# ----------------------------
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


# ----------------------------
# Helpers
# ----------------------------
def _get_df(kind: str):
    kind = (kind or "").lower()
    if kind == "cpt":
        if CPT_DF is None:
            raise HTTPException(status_code=500, detail="CPT data not loaded")
        return CPT_DF, "cpt"
    if kind == "icd":
        if ICD_DF is None:
            raise HTTPException(status_code=500, detail="ICD data not loaded")
        return ICD_DF, "icd"
    raise HTTPException(status_code=400, detail="kind must be 'cpt' or 'icd'")


# ----------------------------
# Basic status
# ----------------------------
@app.get("/status")
def status():
    return {
        "status": "ok",
        "cpt_rows": 0 if CPT_DF is None else int(getattr(CPT_DF, "shape", [0])[0]),
        "icd_rows": 0 if ICD_DF is None else int(getattr(ICD_DF, "shape", [0])[0]),
    }


# ----------------------------
# Home / Simple pages
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Tarmeez"
,
        },
    )


# ----------------------------
# QUIZ (HTML pages)
# ----------------------------
app.get("/quiz", response_class=HTMLResponse)
def quiz_page(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request, "title": "Quiz"})


@app.get("/quiz/run/{kind}", response_class=HTMLResponse)
def quiz_run(request: Request, kind: str, n: int = 10, ui_lang: str = "en"):
    kind = (kind or "").lower()
    if kind not in ("cpt", "icd"):
        kind = "cpt"

    return templates.TemplateResponse(
        "quiz_run.html",
        {
            "request": request,
            "title": f"{kind.upper()} Quiz",
            "kind": kind,
            # لا تكتب ICD-10 لو ملفك مو ICD-10 فعلاً — خله عام
            "kind_upper": ("ICD (Diagnosis)" if kind == "icd" else "CPT"),
            "n": n,
            "ui_lang": ui_lang,
        },
    )


# ----------------------------
# QUIZ (JSON API) - the correct API
# ----------------------------
@app.get("/api/quiz/{kind}")
def api_quiz(kind: str, n: int = 10):
    df, k = _get_df(kind)
    return build_quiz(df, k, n=n)


# Backward-compat API (optional):
# If you were using /quiz/cpt as JSON before, keep this too:
@app.get("/quiz/{kind}")
def legacy_quiz_api(kind: str, n: int = 10):
    df, k = _get_df(kind)
    return build_quiz(df, k, n=n)


# ----------------------------
# Dictionary / Free search APIs (JSON)
# ----------------------------
@app.get("/cpt", response_class=HTMLResponse)
def cpt_page(request: Request):
    return templates.TemplateResponse("cpt.html", {"request": request, "title": "CPT Search"})


@app.get("/icd10", response_class=HTMLResponse)
def icd_page(request: Request):
    return templates.TemplateResponse("icd10.html", {"request": request, "title": "ICD-10 Search"})



# ----------------------------
# Simple search endpoints (optional aliases)
# ----------------------------
@app.get("/search/cpt")
def search_cpt(q: str = Query(..., min_length=1), limit: int = 10):
    if CPT_DF is None:
        raise HTTPException(status_code=500, detail="CPT data not loaded")
    return {"query": q, "results": free_search(CPT_DF, q, limit=limit, kind="cpt")}


@app.get("/search/icd")
def search_icd(q: str = Query(..., min_length=1), limit: int = 10):
    if ICD_DF is None:
        raise HTTPException(status_code=500, detail="ICD data not loaded")
    return {"query": q, "results": free_search(ICD_DF, q, limit=limit, kind="icd")}

@app.get("/dictionary", response_class=HTMLResponse)
def dictionary_page(request: Request):
    return templates.TemplateResponse("dictionary.html", {"request": request, "title": "Dictionary"})

@app.get("/quiz/cpt", response_class=HTMLResponse)
def quiz_cpt(request: Request):
    return templates.TemplateResponse("quiz_cpt.html", {"request": request, "title": "CPT Quiz"})

@app.get("/quiz/icd10", response_class=HTMLResponse)
def quiz_icd10(request: Request):
    return templates.TemplateResponse("quiz_icd10.html", {"request": request, "title": "ICD-10 Quiz"})

@app.get("/cases", response_class=HTMLResponse)
def cases_home(request: Request):
    return templates.TemplateResponse("cases_home.html", {"request": request, "title": "Cases"})

@app.get("/cases/cpt", response_class=HTMLResponse)
def cases_cpt(request: Request):
    return templates.TemplateResponse("cases_cpt.html", {"request": request, "title": "CPT Cases"})

@app.get("/cases/icd10", response_class=HTMLResponse)
def cases_icd10(request: Request):
    return templates.TemplateResponse("cases_icd10.html", {"request": request, "title": "ICD-10 Cases"})

@app.get("/cases/mixed", response_class=HTMLResponse)
def cases_mixed(request: Request):
    return templates.TemplateResponse("cases_mixed.html", {"request": request, "title": "Mixed Cases"})