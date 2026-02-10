from pathlib import Path
import re

ROOT = Path.cwd()
header = ROOT / "app" / "templates" / "partials" / "header.html"
css    = ROOT / "app" / "static" / "styles.css"
app_js = ROOT / "app" / "static" / "app.js"

for p in (header, css, app_js):
    if not p.exists():
        raise SystemExit(f" ملف ناقص: {p}")

# 1) Fix brand title markup to 2 spans so it never flips order
h = header.read_text(encoding="utf-8", errors="ignore")

# Replace any existing brandTitle line (single text) with stable 2-span version
# Works whether brandTitle has data-no-i18n or not.
h2 = re.sub(
    r'<div\s+class="brandTitle[^"]*"(?:[^>]*)>.*?</div>',
    '<div class="brandTitle" data-no-i18n="1">'
    '<span class="brand-ar">ترميز</span>'
    '<span class="brand-sep"> | </span>'
    '<span class="brand-en">Tarmeez</span>'
    '</div>',
    h,
    flags=re.DOTALL
)

# If not found, do a fallback insert before brandSub
if h2 == h and "brandSub" in h:
    h2 = h.replace(
        '<div class="brandSub',
        '<div class="brandTitle" data-no-i18n="1">'
        '<span class="brand-ar">ترميز</span>'
        '<span class="brand-sep"> | </span>'
        '<span class="brand-en">Tarmeez</span>'
        '</div>\n          <div class="brandSub'
    )

header.write_text(h2, encoding="utf-8")

# 2) Ensure i18n never touches brand (already via data-no-i18n), but enforce skip if missing
js = app_js.read_text(encoding="utf-8", errors="ignore")
if "data-no-i18n" not in js:
    js = re.sub(
        r'(querySelectorAll\("\[data-en\]\[data-ar\]"\)\.forEach\(\(el\)\s*=>\s*\{\n)',
        r'\1    if (el.hasAttribute("data-no-i18n")) return;\n',
        js
    )
    js = re.sub(
        r'(querySelectorAll\("\[data-ph-en\]\[data-ph-ar\]"\)\.forEach\(\(el\)\s*=>\s*\{\n)',
        r'\1    if (el.hasAttribute("data-no-i18n")) return;\n',
        js
    )
app_js.write_text(js, encoding="utf-8")

# 3) Add CSS that forces the brandTitle order to NEVER flip, regardless of RTL/LTR
c = css.read_text(encoding="utf-8", errors="ignore")
MARK = "/* TARMEZ-BRAND-ORDER-LOCK */"
if MARK not in c:
    c += """

/* TARMEZ-BRAND-ORDER-LOCK */
/* الهدف: (ترميز | Tarmeez) يظل بنفس الترتيب دائمًا ولا ينعكس مع RTL */
.brandTitle{
  display:inline-flex !important;
  align-items:center !important;
  gap:6px !important;
  white-space:nowrap !important;

  direction:ltr !important;          /* يثبت ترتيب العناصر كما هو بالـHTML */
  unicode-bidi:isolate !important;
  flex-direction:row !important;
}

.brandTitle .brand-ar{
  direction:rtl !important;          /* العربي يقرأ صح */
  unicode-bidi:isolate !important;
}

.brandTitle .brand-en{
  direction:ltr !important;          /* الإنجليزي يقرأ صح */
  unicode-bidi:isolate !important;
}

.brandTitle .brand-sep{
  opacity:.85 !important;
}
"""
    css.write_text(c, encoding="utf-8")

print(" تم: ترتيب اسم البراند ثابت (ترميز | Tarmeez) وما ينعكس مع الترجمة.")
print(" سو Hard Refresh: Ctrl+Shift+R بعد تشغيل السيرفر.")
