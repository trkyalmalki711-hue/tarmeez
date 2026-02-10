from pathlib import Path
import re

ROOT = Path.cwd()

app_js = ROOT / "app" / "static" / "app.js"
header = ROOT / "app" / "templates" / "partials" / "header.html"

if not app_js.exists():
    raise SystemExit(" ما لقيت app/static/app.js  تأكد إنك داخل مجلد Tarmeez الصحيح")

# 1) خلّي الترجمة تتجاهل أي عنصر عليه data-no-i18n
js = app_js.read_text(encoding="utf-8")

# إضافة شرط skip داخل applyI18n (لو مو موجود)
if "data-no-i18n" not in js:
    js = re.sub(
        r'(document\.querySelectorAll\("\[data-en\]\[data-ar\]"\)\.forEach\(\(el\)\s*=>\s*\{\n)',
        r'\1      if (el.hasAttribute("data-no-i18n")) return;\n',
        js
    )
    js = re.sub(
        r'(document\.querySelectorAll\("\[data-ph-en\]\[data-ph-ar\]"\)\.forEach\(\(el\)\s*=>\s*\{\n)',
        r'\1      if (el.hasAttribute("data-no-i18n")) return;\n',
        js
    )

app_js.write_text(js, encoding="utf-8")

# 2) ثبّت اسم البرنامج: ضيف data-no-i18n على عنوان الاسم (ترميز | Tarmeez)
if header.exists():
    h = header.read_text(encoding="utf-8")

    # لو فيه brandTitle خله no-i18n
    h2 = re.sub(
        r'(<div\s+class="brandTitle")(>)',
        r'\1 data-no-i18n="1"\2',
        h
    )

    # لو ما فيه brandTitle، على الأقل خلي أي نص "ترميز | Tarmeez" محمي
    if h2 == h:
        h2 = h.replace("ترميز | Tarmeez", '<span data-no-i18n="1">ترميز | Tarmeez</span>')

    header.write_text(h2, encoding="utf-8")

print(" تم: زر الترجمة يشتغل على كل شيء، واسم البرنامج مستثنى (ثابت).")
print(" شغّل السيرفر وجرب زر العربية/English.")
