# app/quiz.py
from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional

import pandas as pd


# ---- Regex rules ----
# CPT: 5 digits OR Category III ending with T (e.g., 0065T)
_CPT_RE = re.compile(r"^(?:\d{5}|\d{4}T|\d{5}T|\d{4}[A-Z]|\d{5}[A-Z])$")

# ICD-10: A00, A00.0, E11.9, Z99.89, etc.
_ICD10_RE = re.compile(r"^[A-Z][0-9]{2}(?:\.[0-9A-Z]{1,4})?$")

# ICD-9: 250, 250.00, 9984, 998.4 etc (loose)
_ICD9_RE = re.compile(r"^(?:\d{3}(?:\.\d{1,2})?|\d{4,5})$")


def _detect_icd_flavor(code_series: pd.Series) -> str:
    """
    Detect if ICD codes look like ICD-10 (letters) or ICD-9 (numeric).
    """
    sample = code_series.dropna().astype(str).head(300).tolist()
    has_letters = any(any(ch.isalpha() for ch in s) for s in sample)
    return "icd10" if has_letters else "icd9"


def _pick_description_column(df: pd.DataFrame) -> str:
    """
    Pick the best description column name.
    """
    cols = set(df.columns)
    if "description" in cols:
        return "description"
    for alt in ("label", "definition", "ShortDescription", "LongDescription", "shortdescription", "longdescription"):
        if alt in cols:
            return alt
    # last resort: first non-code column
    non = [c for c in df.columns if c != "code"]
    return non[0] if non else "code"


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure dataframe has at least: code, description
    Keep optional columns if present: section/chapter/domain
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["code", "description"])

    out = df.copy()

    if "code" not in out.columns:
        raise ValueError("quiz.py: DataFrame missing required column: 'code'")

    desc_col = _pick_description_column(out)

    # build normalized frame
    keep_cols = ["code", desc_col]
    for optional in ("section", "chapter", "domain"):
        if optional in out.columns:
            keep_cols.append(optional)

    out = out[keep_cols].copy()
    out = out.rename(columns={desc_col: "description"})

    # clean
    out["code"] = out["code"].astype(str).str.strip()
    out["description"] = out["description"].astype(str).str.strip()

    # drop empties
    out = out[(out["code"] != "") & (out["description"] != "")]
    out = out.reset_index(drop=True)

    return out


def _filter_by_kind(work: pd.DataFrame, kind: str) -> tuple[pd.DataFrame, str]:
    """
    Filter codes to avoid mixing CPT vs ICD.
    Returns (filtered_df, icd_flavor)
    """
    kind = (kind or "").lower()
    icd_flavor = "icd10"

    if kind == "cpt":
        work = work[work["code"].str.match(_CPT_RE, na=False)].copy()
        return work.reset_index(drop=True), icd_flavor

    # icd
    icd_flavor = _detect_icd_flavor(work["code"])
    if icd_flavor == "icd10":
        work = work[work["code"].str.match(_ICD10_RE, na=False)].copy()
    else:
        work = work[work["code"].str.match(_ICD9_RE, na=False)].copy()

    return work.reset_index(drop=True), icd_flavor


def _difficulty(kind: str, code: str, desc: str, icd_flavor: str) -> str:
    """
    Free heuristic difficulty (no AI).
    """
    kind = (kind or "").lower()
    code = str(code)
    desc = str(desc)

    score = 0
    # longer desc => harder
    score += min(len(desc) // 35, 3)
    # complexity words
    if any(w in desc.lower() for w in ["with", "without", "complication", "unspecified", "status", "due to", "associated"]):
        score += 1
    # punctuation
    if any(ch in desc for ch in [",", "(", ")", ";", ":"]):
        score += 1
    # more specific ICD-10 often has dot
    if kind == "icd" and icd_flavor == "icd10" and "." in code:
        score += 1

    if score <= 1:
        return "easy"
    if score == 2:
        return "medium"
    return "hard"


def _hint(kind: str, code: str, row: Dict[str, Any], icd_flavor: str) -> str:
    """
    Hint text shown in UI.
    """
    kind = (kind or "").lower()
    code = str(code).strip()

    if kind == "cpt":
        prefix = code[:2] if len(code) >= 2 else code
        section = str(row.get("section") or "").strip()
        if section:
            return f"💡 Starts with {prefix} • Section: {section}"
        return f"💡 Starts with {prefix}"

    # icd
    if icd_flavor == "icd10":
        prefix = code[:3] if len(code) >= 3 else code
    else:
        prefix = code.split(".")[0]

    chapter = str(row.get("chapter") or row.get("domain") or "").strip()
    if chapter:
        return f"💡 Starts with {prefix} • Chapter: {chapter}"
    return f"💡 Starts with {prefix}"


def _pick_wrong_codes(work: pd.DataFrame, answer_code: str, k: int = 3) -> List[str]:
    """
    Sample wrong options from the same dataset.
    """
    answer_code = str(answer_code).strip()
    pool = work["code"].astype(str).str.strip()
    pool = pool[pool != answer_code].dropna().unique().tolist()

    if not pool:
        return []
    if len(pool) <= k:
        return random.sample(pool, len(pool))
    return random.sample(pool, k)


def build_quiz(df: pd.DataFrame, kind: str, n: int = 10) -> Dict[str, Any]:
    """
    Main function used by API.
    Returns:
      {"type": "cpt"/"icd", "questions": [{"prompt","options","answer","hint","difficulty"}...]}
    """
    kind = (kind or "").lower()
    if kind not in ("cpt", "icd"):
        kind = "cpt"

    if df is None or df.empty:
        return {"type": kind, "questions": []}

    # normalize n
    try:
        n = int(n)
    except Exception:
        n = 10
    n = max(5, min(50, n))

    work = _normalize_df(df)
    work, icd_flavor = _filter_by_kind(work, kind)

    if work.empty:
        return {"type": kind, "questions": []}

    sample_n = min(n, len(work))
    idxs = random.sample(range(len(work)), sample_n)

    questions: List[Dict[str, Any]] = []

    for idx in idxs:
        code = work.at[idx, "code"]
        desc = work.at[idx, "description"]

        code = "" if pd.isna(code) else str(code).strip()
        desc = "" if pd.isna(desc) else str(desc).strip()
        if not code or not desc:
            continue

        wrong = _pick_wrong_codes(work, code, k=3)
        options = wrong + [code]
        random.shuffle(options)

        row_dict: Dict[str, Any] = {}
        for col in ("section", "chapter", "domain"):
            if col in work.columns:
                v = work.at[idx, col]
                row_dict[col] = "" if pd.isna(v) else str(v).strip()

        questions.append(
            {
                "prompt": desc,
                "options": options,
                "answer": code,
                "hint": _hint(kind, code, row_dict, icd_flavor),
                "difficulty": _difficulty(kind, code, desc, icd_flavor),
            }
        )

    return {"type": kind, "questions": questions}


# ---- Backward compatibility ----
# لو عندك api.py أو ملف ثاني يستورد الدالة القديمة، نخليه يشتغل وما يكسر المشروع
def _make_mcq_from_df(df: pd.DataFrame, kind: str = "cpt", n: int = 10) -> Dict[str, Any]:
    return build_quiz(df, kind=kind, n=n)
