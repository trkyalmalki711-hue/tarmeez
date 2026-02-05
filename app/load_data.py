from pathlib import Path
import pandas as pd
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CPT_FILE = DATA_DIR / "cpt.csv"
ICD_FILE = DATA_DIR / "icd10.csv"


def load_cpt():
    """
    CPT robust loader for messy CSV:
    - handles double quotes "" inside fields
    - handles lines ending with ';'
    - handles rows that come in as a single wrapped field
    - merges extra commas into description
    """
    if not CPT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {CPT_FILE}")

    rows = []
    bad = 0

    with open(CPT_FILE, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        _header = next(reader, None)  # skip header

        for r in reader:
            if not r:
                continue

            # بعض السجلات تنقرأ كحقل واحد (بسبب اقتباس ملخبط)
            if len(r) == 1:
                s = r[0].strip()

                # شيل ; في نهاية السطر لو موجود
                if s.endswith(";"):
                    s = s[:-1]

                # فك التغليف الخارجي لو موجود
                if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                    s = s[1:-1]

                # رجّع الاقتباسات المزدوجة "" إلى "
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
            # لو الوصف فيه فواصل زيادة، نجمعها كلها
            desc = ",".join(r[1:]).strip()

            # كثير أسطر CPT تنتهي بـ ; بدل ما تكون جزء من الوصف
            desc = desc.rstrip(";").strip()

            if not code or not desc:
                continue

            rows.append({
                "code": code,
                "description": desc,
                "section": "",
                "keywords": desc.lower()
            })

    df = pd.DataFrame(rows).drop_duplicates(subset=["code", "description"])
    print(f"[CPT] loaded rows={len(df)} | bad_rows={bad} | file={CPT_FILE}")

    if df.empty:
        raise ValueError("CPT loaded 0 rows")

    return df[["code", "description", "section", "keywords"]]


def load_icd10():
    """
    ICD-10 loader for your wrapped-row CSV.
    Columns:
    Id,Code,CodeWithSeparator,ShortDescription,LongDescription,HippaCovered,Deleted
    Many rows may come as a single quoted field -> we parse twice when needed.
    """
    if not ICD_FILE.exists():
        raise FileNotFoundError(f"Missing file: {ICD_FILE}")

    rows = []
    bad = 0

    with open(ICD_FILE, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        _header = next(reader, None)  # skip header

        for r in reader:
            if not r:
                continue

            # case: whole record in one field
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
                # merge extras into LongDescription (index 4)
                r = r[:4] + [",".join(r[4:-2])] + r[-2:]

            _id, code, code_sep, short_desc, long_desc, hipaa, deleted = r

            code_sep = (code_sep or "").strip()
            long_desc = (long_desc or "").strip()
            short_desc = (short_desc or "").strip()

            # للتعليم: لا نستبعد Deleted
            if not code_sep or not long_desc:
                continue

            rows.append({
                "code": code_sep,
                "description": long_desc,
                "keywords": short_desc.lower()
            })

    df = pd.DataFrame(rows).drop_duplicates(subset=["code", "description"])
    print(f"[ICD] loaded rows={len(df)} | bad_rows={bad} | file={ICD_FILE}")

    if df.empty:
        raise ValueError("ICD loaded 0 rows")

    return df
