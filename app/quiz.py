# app/quiz.py
from __future__ import annotations

import random
import pandas as pd


def _difficulty_filter(df: pd.DataFrame, difficulty: str) -> pd.DataFrame:
    """
    Simple difficulty logic:
    - easy   : short descriptions, common codes
    - medium : normal descriptions
    - hard   : long descriptions
    """
    difficulty = (difficulty or "medium").lower()

    if "description" not in df.columns:
        return df

    if difficulty == "easy":
        return df[df["description"].str.len() <= 60]
    if difficulty == "hard":
        return df[df["description"].str.len() >= 120]

    return df  # medium


def build_quiz(
    df: pd.DataFrame,
    kind: str,
    n: int = 10,
    difficulty: str = "medium",
) -> dict:
    """
    Standard quiz generator (NO MIX)
    """
    n = max(5, min(50, int(n)))
    difficulty = (difficulty or "medium").lower()

    work = df.copy()
    work = _difficulty_filter(work, difficulty)

    if work.empty:
        work = df.copy()

    work = work.sample(min(len(work), n), random_state=None)

    all_codes = df["code"].astype(str).tolist()
    questions = []

    for _, r in work.iterrows():
        code = str(r.get("code", "")).strip()
        desc = str(r.get("description", "")).strip()
        if not code or not desc:
            continue

        distractors = [c for c in all_codes if c != code]
        if len(distractors) < 3:
            continue

        options = random.sample(distractors, 3) + [code]
        random.shuffle(options)

        questions.append({
            "prompt": desc,
            "options": options,
            "answer": code
        })

    return {
        "kind": kind,
        "difficulty": difficulty,
        "count": len(questions),
        "questions": questions
    }
