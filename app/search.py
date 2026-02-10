from __future__ import annotations

from typing import Dict, List, Any, Optional
import pandas as pd


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _apply_filters(df: pd.DataFrame, filters: Dict[str, str]) -> pd.DataFrame:
    out = df
    for k, v in (filters or {}).items():
        if v is None or str(v).strip() == "":
            continue
        if k not in out.columns:
            continue
        out = out[out[k].astype(str) == str(v)]
    return out


def free_search(
    df: pd.DataFrame,
    q: str,
    code_col: str = "code",
    desc_col: str = "description",
    keywords_col: str = "keywords",
    meta_cols: Optional[List[str]] = None,
    filters: Optional[Dict[str, str]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []

    qn = _norm(q)
    meta_cols = meta_cols or []

    # 1) فلترة قبل البحث
    filtered = _apply_filters(df, filters or {})

    # 2) إذا ما فيه q، نرجّع أول نتائج بعد الفلترة
    if qn == "":
        filtered = filtered.head(limit)
        results = []
        for _, row in filtered.iterrows():
            meta = {}
            for c in meta_cols:
                if c in filtered.columns:
                    meta[c] = row.get(c, "")
            results.append(
                {
                    "code": str(row.get(code_col, "")).strip(),
                    "description": str(row.get(desc_col, "")).strip(),
                    "meta": meta,
                }
            )
        return results

    # 3) بحث contains على code/description/keywords
    code_s = filtered[code_col].astype(str).str.lower()
    desc_s = filtered[desc_col].astype(str).str.lower()
    key_s = filtered[keywords_col].astype(str).str.lower() if keywords_col in filtered.columns else desc_s

    mask = (
        code_s.str.contains(qn, na=False)
        | desc_s.str.contains(qn, na=False)
        | key_s.str.contains(qn, na=False)
    )

    matched = filtered[mask].copy()

    # ترتيب بسيط: الكود يبدأ بـ q ثم الوصف يحتوي q
    starts = matched[code_col].astype(str).str.lower().str.startswith(qn)
    in_desc = matched[desc_col].astype(str).str.lower().str.contains(qn, na=False)

    matched["_rank"] = 0
    matched.loc[in_desc, "_rank"] = 1
    matched.loc[starts, "_rank"] = 2

    matched = matched.sort_values(by=["_rank", code_col], ascending=[False, True]).head(limit)

    results = []
    for _, row in matched.iterrows():
        meta = {}
        for c in meta_cols:
            if c in matched.columns:
                meta[c] = row.get(c, "")
        results.append(
            {
                "code": str(row.get(code_col, "")).strip(),
                "description": str(row.get(desc_col, "")).strip(),
                "meta": meta,
            }
        )
    return results


def get_unique_list(df: pd.DataFrame, col: str) -> List[str]:
    if df is None or df.empty or col not in df.columns:
        return []
    vals = (
        df[col]
        .astype(str)
        .map(lambda x: x.strip())
        .loc[lambda s: s != ""]
        .drop_duplicates()
        .tolist()
    )
    vals.sort()
    return vals


def build_cpt_filters(df: pd.DataFrame) -> Dict[str, List[str]]:
    return {
        "categories": get_unique_list(df, "category"),
        "sections": get_unique_list(df, "section"),
        "ranges": get_unique_list(df, "range"),
    }


def build_icd_filters(df: pd.DataFrame) -> Dict[str, List[str]]:
    return {
        "chapters": get_unique_list(df, "chapter"),
        "blocks": get_unique_list(df, "block"),
    }
