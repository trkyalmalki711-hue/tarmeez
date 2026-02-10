# app/ai_simple.py
from __future__ import annotations

import random
import re
from typing import Dict, Any, List, Optional

import pandas as pd


def _clean(s: str) -> str:
    return (s or "").strip()


def _is_cpt(code: str) -> bool:
    c = (code or "").strip().upper()
    return bool(re.match(r"^(?:\d{5}|\d{4}T|\d{4}F)$", c))


def _pick_distractors(df: pd.DataFrame, correct_code: str, k: int = 3) -> List[str]:
    # Pick distractors from nearby codes if possible, otherwise random
    codes = df["code"].astype(str).tolist()
    correct_code = str(correct_code)

    if correct_code in codes and len(codes) > k + 1:
        i = codes.index(correct_code)
        window = codes[max(0, i - 250): min(len(codes), i + 250)]
        window = [c for c in window if c != correct_code]
        if len(window) >= k:
            return random.sample(window, k)

    pool = [c for c in codes if c != correct_code]
    if len(pool) < k:
        return pool
    return random.sample(pool, k)


def _make_prompt(kind: str, row: Dict[str, Any], mode: str = "quiz") -> str:
    code = row.get("code", "")
    desc = row.get("description", "")

    kind = (kind or "").lower()
    if mode == "case":
        # scenario-ish, still simple and deterministic
        if kind == "icd":
            return f"Case: Choose the most appropriate ICD-10 code for this diagnosis:\n\n{desc}"
        return f"Case: Choose the most appropriate CPT code for this procedure:\n\n{desc}"

    # classic quiz prompt
    if kind == "icd":
        return f"Which ICD-10 code matches this description?\n\n{desc}"
    return f"Which CPT code matches this description?\n\n{desc}"


def generate_ai_questions(
    df: pd.DataFrame,
    kind: str,
    n: int = 10,
    mode: str = "quiz",
    filters: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    AI-simple generator:
    - Uses your data only
    - Builds MCQ with distractors
    - Adds hint using hierarchy meta if available
    """
    kind = (kind or "").lower()
    mode = (mode or "quiz").lower()
    n = int(max(5, min(50, n)))

    filters = filters or {}

    work = df.copy()

    # apply filters if columns exist
    if kind == "icd":
        ch = _clean(filters.get("chapter", ""))
        bl = _clean(filters.get("block", ""))
        if ch and "chapter" in work.columns:
            work = work[work["chapter"].astype(str) == ch]
        if bl and "block" in work.columns:
            work = work[work["block"].astype(str) == bl]

    if kind == "cpt":
        cat = _clean(filters.get("category", ""))
        sec = _clean(filters.get("section", ""))
        rng = _clean(filters.get("range", ""))
        if cat and "category" in work.columns:
            work = work[work["category"].astype(str) == cat]
        if sec and "section" in work.columns:
            work = work[work["section"].astype(str) == sec]
        if rng and "range" in work.columns:
            work = work[work["range"].astype(str) == rng]

    if work.empty:
        work = df.copy()

    # sample rows
    work = work.sample(min(len(work), max(n * 3, n)), random_state=None)

    questions: List[Dict[str, Any]] = []
    used = set()

    for _, r in work.iterrows():
        code = str(r.get("code", "")).strip()
        desc = str(r.get("description", "")).strip()
        if not code or not desc:
            continue
        if (kind == "cpt") and not _is_cpt(code):
            # keep CPT list clean
            continue
        if code in used:
            continue
        used.add(code)

        distractors = _pick_distractors(df, code, k=3)
        options = [code] + distractors
        random.shuffle(options)

        # Hint from hierarchy if possible
        hint = ""
        if kind == "icd":
            ch = r.get("chapter", "")
            bl = r.get("block", "")
            if ch or bl:
                hint = f"Hint: Chapter = {ch} | Block = {bl}"
        else:
            cat = r.get("category", "")
            sec = r.get("section", "")
            rng = r.get("range", "")
            if cat or sec or rng:
                hint = f"Hint: {cat} | {sec} {('(' + rng + ')') if rng else ''}"

        questions.append(
            {
                "prompt": _make_prompt(kind, {"code": code, "description": desc}, mode=mode),
                "options": options,
                "answer": code,
                "hint": hint,
                "meta": {
                    "code": code,
                    "kind": kind,
                    "mode": mode,
                },
            }
        )

        if len(questions) >= n:
            break

    return {"kind": kind, "mode": mode, "questions": questions}
