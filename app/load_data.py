from pathlib import Path
import pandas as pd
import csv
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# CPT
CPT_JSON = DATA_DIR / "cpt.json"
CPT_CSV = DATA_DIR / "cpt.csv"

# ICD
ICD_JSON = DATA_DIR / "icd10.json"
ICD_CSV = DATA_DIR / "icd10.csv"


# ===================== CPT =====================
def load_cpt():
    # --- JSON (أساسي) ---
    if CPT_JSON.exists():
        try:
            data = json.loads(CPT_JSON.read_text(encoding="utf-8"))
            rows = []

            for cat in data:
                category = cat.get("category")
                for sec in cat.get("sections", []):
                    section = sec.get("section")
                    range_ = sec.get("range")
                    for c in sec.get("codes", []):
                        rows.append({
                            "category": category,
                            "section": section,
                            "range": range_,
                            "code": c.get("code"),
                            "description": c.get("description"),
                            "keywords": c.get("keywords", "").lower(),
                        })

            df = pd.DataFrame(rows)
            if df.empty:
                raise ValueError("cpt.json loaded 0 rows")

            print(f"[CPT] loaded from JSON rows={len(df)}")
            return df

        except Exception as e:
            print("[CPT] JSON failed, fallback to CSV:", e)

    # --- CSV (احتياطي) ---
    if not CPT_CSV.exists():
        raise FileNotFoundError("Missing CPT data")

    df = pd.read_csv(CPT_CSV, dtype=str).fillna("")
    df["keywords"] = df["keywords"].str.lower()

    print(f"[CPT] loaded from CSV rows={len(df)}")
    return df


# ===================== ICD =====================
def load_icd10():
    # --- JSON (أساسي شجري) ---
    if ICD_JSON.exists():
        try:
            data = json.loads(ICD_JSON.read_text(encoding="utf-8"))
            rows = []

            for ch in data:
                chapter = ch.get("chapter")
                for block in ch.get("blocks", []):
                    block_name = block.get("block")
                    for c in block.get("codes", []):
                        rows.append({
                            "chapter": chapter,
                            "block": block_name,
                            "code": c.get("code"),
                            "description": c.get("description"),
                            "keywords": c.get("keywords", "").lower(),
                        })

            df = pd.DataFrame(rows)
            if df.empty:
                raise ValueError("icd10.json loaded 0 rows")

            print(f"[ICD] loaded from JSON rows={len(df)}")
            return df

        except Exception as e:
            print("[ICD] JSON failed, fallback to CSV:", e)

    # --- CSV (احتياطي) ---
    if not ICD_CSV.exists():
        raise FileNotFoundError("Missing ICD data")

    df = pd.read_csv(ICD_CSV, dtype=str).fillna("")
    df["keywords"] = df["keywords"].str.lower()

    print(f"[ICD] loaded from CSV rows={len(df)}")
    return df
