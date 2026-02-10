from pathlib import Path
import csv
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CPT_CSV = DATA_DIR / "cpt.csv"
CPT_JSON = DATA_DIR / "cpt.json"


def cpt_section(code: str) -> str:
    c = (code or "").strip().upper()

    if re.match(r"^\d{4}T$", c):
        return "Category III (Temporary Codes)"
    if re.match(r"^\d{4}F$", c):
        return "Category II (Performance Measures)"
    if not re.match(r"^\d{5}$", c):
        return "Other"

    n = int(c)

    if 1 <= n <= 6999:
        return "Anesthesia (00100–01999)"
    if 10000 <= n <= 19999:
        return "Surgery: Integumentary (10000–19999)"
    if 20000 <= n <= 29999:
        return "Surgery: Musculoskeletal (20000–29999)"
    if 30000 <= n <= 39999:
        return "Surgery: Respiratory/Cardiovascular (30000–39999)"
    if 40000 <= n <= 49999:
        return "Surgery: Digestive/Urinary/Genital (40000–49999)"
    if 50000 <= n <= 59999:
        return "Surgery: Nervous System/Eye/Ear (50000–59999)"
    if 60000 <= n <= 69999:
        return "Surgery: Endocrine (60000–69999)"
    if 70000 <= n <= 79999:
        return "Radiology (70000–79999)"
    if 80000 <= n <= 89999:
        return "Pathology & Laboratory (80000–89999)"
    if 90000 <= n <= 99999:
        if 99200 <= n <= 99499 or 99000 <= n <= 99099:
            return "Evaluation & Management (E/M)"
        return "Medicine (90000–99999)"

    return "Other"


def convert():
    if not CPT_CSV.exists():
        raise FileNotFoundError("cpt.csv not found")

    rows = []
    bad = 0

    with open(CPT_CSV, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        _header = next(reader, None)

        for r in reader:
            if not r:
                continue

            if len(r) == 1:
                s = r[0].strip()
                if s.endswith(";"):
                    s = s[:-1]
                if s.startswith('"') and s.endswith('"'):
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

            rows.append({
                "code": code,
                "description": desc,
                "section": cpt_section(code),
                "keywords": desc.lower()
            })

    # إزالة التكرار
    seen = set()
    uniq = []
    for r in rows:
        k = (r["code"], r["description"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)

    CPT_JSON.write_text(
        json.dumps(uniq, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[OK] CPT JSON created: {len(uniq)} rows")
    print(f"[INFO] Bad rows skipped: {bad}")


if __name__ == "__main__":
    convert()
