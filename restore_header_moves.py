from pathlib import Path
import re

ROOT = Path.cwd()
css = ROOT / "app" / "static" / "styles.css"
if not css.exists():
    raise SystemExit(" ما لقيت app/static/styles.css")

txt = css.read_text(encoding="utf-8", errors="ignore")

# احذف كل بلوكات "تثبيت الهيدر/البراند" اللي أضفناها سابقًا
patterns = [
    r"/\*\s*TARMEZ-HEADER-LOCK\s*\*/.*?(?=\n/\*|\Z)",
    r"/\*\s*TARMEZ-HEADER-PIN\s*\*/.*?(?=\n/\*|\Z)",
    r"/\*\s*TARMEZ-HEADER-PIN-V2\s*\*/.*?(?=\n/\*|\Z)",
    r"/\*\s*TARMEZ-HEADER-ABS-PIN\s*\*/.*?(?=\n/\*|\Z)",
    r"/\*\s*TARMEZ-FINAL-PIN\s*\*/.*?(?=\n/\*|\Z)",
    r"/\*\s*TARMEZ-BRAND-ORDER-LOCK\s*\*/.*?(?=\n/\*|\Z)",
]

for pat in patterns:
    txt = re.sub(pat, "", txt, flags=re.DOTALL | re.IGNORECASE)

# نظّف فراغات زيادة
txt = re.sub(r"\n{3,}", "\n\n", txt).strip() + "\n"

css.write_text(txt, encoding="utf-8")
print(" تم: شلت كل تثبيتات الهيدر/البراند. الحين الهيدر يتحرك وينعكس طبيعي مع RTL/LTR.")
print(" سو Hard Refresh: Ctrl+Shift+R بعد تشغيل السيرفر.")
