from pathlib import Path
import csv
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ICD_CSV = DATA_DIR / "icd_custom.csv"
ICD_JSON = DATA_DIR / "icd_custom.json"

REQUIRED = ("code", "description")

def convert():
    if not ICD_CSV.exists():
        raise FileNotFoundError(f"Missing: {ICD_CSV}")

    rows = []
    bad = 0

    with open(ICD_CSV, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("icd_custom.csv has no header row")

        # تأكد الهيدر فيه المطلوب
        fields = [c.strip() for c in reader.fieldnames]
        fieldset = set(fields)
        for k in REQUIRED:
            if k not in fieldset:
                raise ValueError(f"icd_custom.csv missing required column: {k}")

        for r in reader:
            try:
                code = (r.get("code") or "").strip()
                desc = (r.get("description") or "").strip()
                keywords = (r.get("keywords") or "").strip()

                if not code or not desc:
                    continue

                if not keywords:
                    keywords = desc.lower()

                rows.append({
                    "code": code,
                    "description": desc,
                    "keywords": keywords.lower(),
                })
            except Exception:
                bad += 1
                continue

    # remove duplicates
    seen = set()
    uniq = []
    for item in rows:
        k = (item["code"], item["description"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(item)

    ICD_JSON.write_text(json.dumps(uniq, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {len(uniq)} rows -> {ICD_JSON}")
    print(f"[INFO] bad_rows={bad}")

if __name__ == "__main__":
    convert()
