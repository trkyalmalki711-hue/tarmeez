from pathlib import Path
import re

ROOT = Path.cwd()
header = ROOT / "app" / "templates" / "partials" / "header.html"
css    = ROOT / "app" / "static" / "styles.css"

for p in (header, css):
    if not p.exists():
        raise SystemExit(f" ملف ناقص: {p}")

# 1) عدّل البراند إلى سبانين بالترتيب المطلوب: English (left) | Arabic (right)
h = header.read_text(encoding="utf-8", errors="ignore")

# استبدال أي brandTitle موجود (سواء كان نص واحد أو سبانات قديمة) بنسخة ثابتة
h2 = re.sub(
    r'<div\s+class="brandTitle[^"]*"(?:[^>]*)>.*?</div>',
    '<div class="brandTitle tarmeezBrandTitle" data-no-i18n="1">'
    '<span class="brand-en">Tarmeez</span>'
    '<span class="brand-sep"> | </span>'
    '<span class="brand-ar">ترميز</span>'
    '</div>',
    h,
    flags=re.DOTALL
)

# إذا ما لقى brandTitle لأي سبب، ندخله قبل brandSub
if h2 == h and "brandSub" in h:
    h2 = h.replace(
        '<div class="brandSub',
        '<div class="brandTitle tarmeezBrandTitle" data-no-i18n="1">'
        '<span class="brand-en">Tarmeez</span>'
        '<span class="brand-sep"> | </span>'
        '<span class="brand-ar">ترميز</span>'
        '</div>\n          <div class="brandSub'
    )

header.write_text(h2, encoding="utf-8")

# 2) CSS يضمن: الإنجليزي يسار + العربي يمين (بدون انعكاس غريب)
c = css.read_text(encoding="utf-8", errors="ignore")
MARK = "/* TARMEZ-BRAND-EN-LEFT-AR-RIGHT */"

if MARK not in c:
    c += """

/* TARMEZ-BRAND-EN-LEFT-AR-RIGHT */
/* الهدف: Tarmeez يسار + ترميز يمين داخل نفس العنوان */
.tarmeezBrandTitle, .brandTitle.tarmeezBrandTitle{
  display:inline-flex !important;
  align-items:center !important;
  gap:6px !important;
  white-space:nowrap !important;
  direction:ltr !important;          /* يثبت ترتيب العناصر كما هو بالـHTML */
  unicode-bidi:isolate !important;
}

.tarmeezBrandTitle .brand-en{
  direction:ltr !important;
  unicode-bidi:isolate !important;
}

.tarmeezBrandTitle .brand-ar{
  direction:rtl !important;
  unicode-bidi:isolate !important;
}

.tarmeezBrandTitle .brand-sep{
  opacity:.85 !important;
}
"""
    css.write_text(c, encoding="utf-8")

print(" تم: صار الإنجليزي يسار (Tarmeez) والعربي يمين (ترميز).")
print(" سو Hard Refresh: Ctrl+Shift+R")
