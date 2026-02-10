# app/load_data.py
from __future__ import annotations

from pathlib import Path
import csv
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CPT_FILE = DATA_DIR / "cpt.csv"
ICD_FILE = DATA_DIR / "icd10.csv"


def _read_csv_safe(path: Path) -> pd.DataFrame:
    # robust pandas read
    try:
        return pd.read_csv(path, encoding="utf-8", engine="python")
    except Exception:
        return pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip")


def load_cpt() -> pd.DataFrame:
    if not CPT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {CPT_FILE}")

    df = _read_csv_safe(CPT_FILE)

    # NEW FORMAT (preferred): category/section/range/code/description/keywords
    cols = {c.lower().strip(): c for c in df.columns}
    if "code" in cols and "description" in cols:
        # normalize column names
        df = df.rename(columns={cols["code"]: "code", cols["description"]: "description"})
        if "keywords" in cols:
            df = df.rename(columns={cols["keywords"]: "keywords"})
        else:
            df["keywords"] = df["description"].astype(str).str.lower()

        # optional meta
        for k in ["category", "category_no", "section", "section_no", "range"]:
            if k in cols:
                df = df.rename(columns={cols[k]: k})
            else:
                df[k] = ""

        df["code"] = df["code"].astype(str).str.strip()
        df["description"] = df["description"].astype(str).str.strip()

        df = df.dropna(subset=["code", "description"]).drop_duplicates(subset=["code", "description"])
        print(f"[CPT] loaded rows={len(df)} | file={CPT_FILE}")

        return df[
            ["code", "description", "keywords", "category", "category_no", "section", "section_no", "range"]
        ]

    # OLD FALLBACK (your earlier messy file)
    rows = []
    bad = 0
    with open(CPT_FILE, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        _header = next(reader, None)
        for r in reader:
            if not r:
                continue
            if len(r) == 1:
                s = r[0].strip()
                if s.endswith(";"):
                    s = s[:-1]
                if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                    s = s[1:-1]
                s = s.replace('""', '"')
                try:
                    r = next(csv.reader([s], delimiter=",", quotechar='"'))
                except Exception:
                    bad += 1
                    continue
            if len(r) < 2:
                bad += 1
                continue
            code = (r[0] or "").strip()
            desc = ",".join(r[1:]).strip().rstrip(";").strip()
            if not code or not desc:
                continue
            rows.append({"code": code, "description": desc, "keywords": desc.lower()})

    df = pd.DataFrame(rows).drop_duplicates(subset=["code", "description"])
    df["category"] = ""
    df["category_no"] = ""
    df["section"] = ""
    df["section_no"] = ""
    df["range"] = ""

    print(f"[CPT] loaded rows={len(df)} | bad_rows={bad} | file={CPT_FILE}")
    return df[["code", "description", "keywords", "category", "category_no", "section", "section_no", "range"]]


def load_icd10() -> pd.DataFrame:
    if not ICD_FILE.exists():
        raise FileNotFoundError(f"Missing file: {ICD_FILE}")

    df = _read_csv_safe(ICD_FILE)
    cols = {c.lower().strip(): c for c in df.columns}

    # NEW FORMAT (preferred): chapter/chapter_no/classification/block/block_no/range/code/description/keywords
    if "code" in cols and "description" in cols:
        df = df.rename(columns={cols["code"]: "code", cols["description"]: "description"})
        if "keywords" in cols:
            df = df.rename(columns={cols["keywords"]: "keywords"})
        else:
            df["keywords"] = df["description"].astype(str).str.lower()

        for k in ["chapter", "chapter_no", "classification", "block", "block_no", "range"]:
            if k in cols:
                df = df.rename(columns={cols[k]: k})
            else:
                df[k] = ""

        df["code"] = df["code"].astype(str).str.strip()
        df["description"] = df["description"].astype(str).str.strip()

        df = df.dropna(subset=["code", "description"]).drop_duplicates(subset=["code", "description"])
        print(f"[ICD] loaded rows={len(df)} | file={ICD_FILE}")

        return df[
            ["code", "description", "keywords", "chapter", "chapter_no", "classification", "block", "block_no", "range"]
        ]

    # OLD FALLBACK
    rows = []
    bad = 0
    with open(ICD_FILE, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        _header = next(reader, None)
        for r in reader:
            if not r:
                continue
            if len(r) == 1:
                s = r[0].strip()
                if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                    s = s[1:-1]
                s = s.replace('""', '"')
                try:
                    r = next(csv.reader([s], delimiter=",", quotechar='"'))
                except Exception:
                    bad += 1
                    continue
            if len(r) < 7:
                bad += 1
                continue
            if len(r) > 7:
                r = r[:4] + [",".join(r[4:-2])] + r[-2:]
            _id, code, code_sep, short_desc, long_desc, hipaa, deleted = r
            code_sep = (code_sep or "").strip()
            long_desc = (long_desc or "").strip()
            short_desc = (short_desc or "").strip()
            if not code_sep or not long_desc:
                continue
            rows.append({"code": code_sep, "description": long_desc, "keywords": short_desc.lower()})

    df = pd.DataFrame(rows).drop_duplicates(subset=["code", "description"])
    df["chapter"] = ""
    df["chapter_no"] = ""
    df["classification"] = ""
    df["block"] = ""
    df["block_no"] = ""
    df["range"] = ""

    print(f"[ICD] loaded rows={len(df)} | bad_rows={bad} | file={ICD_FILE}")
    return df[
        ["code", "description", "keywords", "chapter", "chapter_no", "classification", "block", "block_no", "range"]
    ]
