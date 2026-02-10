# app/api.py
from __future__ import annotations

from pathlib import Path
import json

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ----------------------------
# Imports from your project
# ----------------------------
# Loaders
try:
    from app.load_data import load_cpt, load_icd10
except ImportError:
    # fallback names (if your function names differ)
    try:
        from app.load_data import load_cpt, load_icd
        load_icd10 = load_icd  # alias
    except ImportError as e:
        raise ImportError(
            "Could not import loaders. Make sure app/load_data.py has load_cpt and load_icd10 (or load_icd)."
        ) from e

# Quiz builder
from app.quiz import build_quiz

# Search
try:
    from app.search import free_search
except ImportError as e:
    raise ImportError(
        "Could not import free_search. Make sure app/search.py defines free_search."
    ) from e


# ----------------------------
# App setup
# ----------------------------
app = FastAPI(title="Tarmeez", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent  # .../app
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR.parent / "data"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ✅ هذا اللي كان ناقص عندك وسبب 404 للستايل
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Tree data files (for dictionary tree view)
CPT_JSON = DATA_DIR / "cpt.json"
ICD_JSON = DATA_DIR / "icd10.json"


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
    if kind in ("icd", "icd10"):
        if ICD_DF is None:
            raise HTTPException(status_code=500, detail="ICD data not loaded")
        return ICD_DF, "icd"
    raise HTTPException(status_code=400, detail="kind must be 'cpt' or 'icd' (or 'icd10')")


# ----------------------------
# Basic status
# ----------------------------
@app.get("/status", response_class=JSONResponse)
def status():
    return {
        "status": "ok",
        "cpt_rows": 0 if CPT_DF is None else int(getattr(CPT_DF, "shape", [0])[0]),
        "icd_rows": 0 if ICD_DF is None else int(getattr(ICD_DF, "shape", [0])[0]),
        "has_cpt_tree": CPT_JSON.exists(),
        "has_icd_tree": ICD_JSON.exists(),
    }


# ----------------------------
# Home
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Tarmeez"})


# ----------------------------
# Pages (HTML)
# ----------------------------
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


@app.get("/cases", response_class=HTMLResponse)
def cases_home(request: Request):
    return templates.TemplateResponse("cases_home.html", {"request": request, "title": "Cases"})


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


# ----------------------------
# TREE APIs (for your new dictionary tree UI)
# ----------------------------
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


# ----------------------------
# Search APIs (keep for other pages)
# ----------------------------
@app.get("/search/cpt", response_class=JSONResponse)
def search_cpt(q: str = Query("", min_length=0), limit: int = 50):
    if CPT_DF is None:
        raise HTTPException(status_code=500, detail="CPT data not loaded")
    # free_search must accept (df, q, limit=..., kind=...)
    return {"query": q, "results": free_search(CPT_DF, q, limit=limit, kind="cpt")}


@app.get("/search/icd", response_class=JSONResponse)
def search_icd(q: str = Query("", min_length=0), limit: int = 50):
    if ICD_DF is None:
        raise HTTPException(status_code=500, detail="ICD data not loaded")
    return {"query": q, "results": free_search(ICD_DF, q, limit=limit, kind="icd")}


# ----------------------------
# Quiz JSON API
# ----------------------------
@app.get("/api/quiz/{kind}", response_class=JSONResponse)
def api_quiz(kind: str, n: int = 10):
    df, k = _get_df(kind)
    return build_quiz(df, k, n=n)
