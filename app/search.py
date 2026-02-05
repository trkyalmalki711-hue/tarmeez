# app/search.py
from __future__ import annotations

import re
from typing import Dict, Any, List
import pandas as pd


def _clean(s: str) -> str:
    return (s or "").strip().lower()


def _is_code_like(q: str) -> bool:
    q = (q or "").strip()
    return bool(re.match(r"^[A-Za-z]?\d[\dA-Za-z\.]{1,10}$", q))


def free_search(df: pd.DataFrame, q: str, limit: int = 20, kind: str = "cpt") -> List[Dict[str, Any]]:
    """
    df requires: code, description
    optional: keywords, section/chapter/domain
    """
    q_raw = (q or "").strip()
    qn = _clean(q_raw)
    if not qn or df is None or df.empty:
        return []

    # ensure text columns
    work = df.copy()
    for col in ["code", "description"]:
        if col not in work.columns:
            return []

    # optional columns
    has_keywords = "keywords" in work.columns
    has_section = "section" in work.columns
    has_chapter = "chapter" in work.columns
    has_domain = "domain" in work.columns

    # build searchable field
    desc = work["description"].astype(str).str.lower()
    code = work["code"].astype(str).str.lower()

    if has_keywords:
        kw = work["keywords"].astype(str).str.lower()
        hay = code + " " + desc + " " + kw
    else:
        hay = code + " " + desc

    # scoring
    #  - exact code match highest
    #  - code startswith next
    #  - substring match next
    #  - word overlap next (simple)
    is_code = _is_code_like(q_raw)

    scores = pd.Series(0, index=work.index, dtype="int")

    if is_code:
        qcode = qn.lower()
        scores += (code == qcode) * 100
        scores += code.str.startswith(qcode) * 40
        scores += code.str.contains(re.escape(qcode), na=False) * 10

    # text match
    scores += hay.str.contains(re.escape(qn), na=False) * 8

    # token overlap (lightweight)
    tokens = [t for t in re.split(r"\s+", qn) if len(t) >= 3]
    for t in tokens[:6]:
        scores += hay.str.contains(re.escape(t), na=False) * 2

    # pick top
    top = work.loc[scores.sort_values(ascending=False).head(limit).index].copy()
    top_scores = scores.loc[top.index].tolist()

    results: List[Dict[str, Any]] = []
    for i, (_, row) in enumerate(top.iterrows()):
        meta = {}
        if kind == "cpt" and has_section:
            meta["section"] = "" if pd.isna(row.get("section")) else str(row.get("section"))
        if kind == "icd":
            if has_chapter:
                meta["chapter"] = "" if pd.isna(row.get("chapter")) else str(row.get("chapter"))
            if has_domain:
                meta["domain"] = "" if pd.isna(row.get("domain")) else str(row.get("domain"))

        results.append({
            "code": "" if pd.isna(row["code"]) else str(row["code"]),
            "description": "" if pd.isna(row["description"]) else str(row["description"]),
            "score": int(top_scores[i]) if i < len(top_scores) else 0,
            "meta": meta
        })

    # remove zero-score junk
    results = [r for r in results if r["score"] > 0]
    return results
