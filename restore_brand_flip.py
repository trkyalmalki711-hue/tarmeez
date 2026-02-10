from pathlib import Path
import re

ROOT = Path.cwd()
header = ROOT / "app" / "templates" / "partials" / "header.html"
css    = ROOT / "app" / "static" / "styles.css"

for p in (header, css):
    if not p.exists():
        raise SystemExit(f" ملف ناقص: {p}")

# 1) Restore brandTitle to simple text (reversible)
h = header.read_text(encoding="utf-8", errors="ignore")

# Replace the 2-span locked version back to plain text
h2 = re.sub(
    r'<div class="brandTitle"[^>]*>\s*<span class="brand-ar">ترميز</span>\s*<span class="brand-sep">\s*\|\s*</span>\s*<span class="brand-en">Tarmeez</span>\s*</div>',
    '<div class="brandTitle">ترميز | Tarmeez</div>',
    h,
    flags=re.DOTALL
)

# Remove data-no-i18n if it exists on brandTitle
h2 = re.sub(r'(<div class="brandTitle")\s+data-no-i18n="1"', r'\1', h2)

header.write_text(h2, encoding="utf-8")

# 2) Remove the CSS lock block if present
c = css.read_text(encoding="utf-8", errors="ignore")
c2 = re.sub(r'\n/\* TARMEZ-BRAND-ORDER-LOCK \*/.*?(?=\n/\*|\Z)', '\n', c, flags=re.DOTALL)

css.write_text(c2, encoding="utf-8")

print(" تم: رجّعت البراند للوضع الطبيعي (ينعكس مع RTL/LTR).")
print(" سو Hard Refresh: Ctrl+Shift+R بعد تشغيل السيرفر.")
