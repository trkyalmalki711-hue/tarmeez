from pathlib import Path
import re

ROOT = Path.cwd()

header = ROOT / "app" / "templates" / "partials" / "header.html"
app_js = ROOT / "app" / "static" / "app.js"
css = ROOT / "app" / "static" / "styles.css"

for p in (header, app_js, css):
    if not p.exists():
        raise SystemExit(f" ملف ناقص: {p}")

# 1) OVERWRITE header.html (nav translated + app name fixed & excluded)
header_new = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title or "ترميز | Tarmeez" }}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="/static/styles.css">
</head>

<body>
  <div class="bg"></div>

  <div class="container">
    <header class="nav card tarmeezHeader">
      <div class="brand tarmeezBrand">
        <div class="logo" aria-hidden="true"></div>
        <div class="brandText">
          <!-- اسم البرنامج ثابت + مستثنى من الترجمة -->
          <div class="brandTitle tarmeezBrandTitle" data-no-i18n="1">ترميز | Tarmeez</div>

          <div class="brandSub"
               data-en="CPT & ICD-10 Academy"
               data-ar="أكاديمية CPT و ICD-10">CPT & ICD-10 Academy</div>
        </div>
      </div>

      <nav class="navlinks tarmeezNavlinks" aria-label="Primary">
        <a class="pill" href="/" data-en="Home" data-ar="الرئيسية">Home</a>
        <a class="pill" href="/dictionary" data-en="Dictionary" data-ar="القاموس">Dictionary</a>
        <a class="pill" href="/quiz" data-en="Quiz" data-ar="الكويز">Quiz</a>
        <a class="pill" href="/cases" data-en="Cases" data-ar="الحالات">Cases</a>
        <a class="pill" href="/notes" data-en="Notes" data-ar="ملاحظات">Notes</a>
        <a class="pill" href="/about" data-en="About" data-ar="عن البرنامج">About</a>
        <a class="pill" href="/account" data-en="Account" data-ar="الحساب">Account</a>
        <a class="pill" href="/login" data-en="Login" data-ar="تسجيل الدخول">Login</a>
      </nav>

      <div class="rightTools tarmeezRightTools">
        <div class="langToggle" aria-label="Language">
          <button class="btn btnGhost" data-lang-btn="en" onclick="Tarmeez.setLang('en')">English</button>
          <button class="btn btnGhost" data-lang-btn="ar" onclick="Tarmeez.setLang('ar')">العربية</button>
        </div>
      </div>
    </header>
"""
header.write_text(header_new, encoding="utf-8")

# 2) PATCH app.js: ensure applyI18n exists + skips data-no-i18n + always runs on DOMContentLoaded
js = app_js.read_text(encoding="utf-8", errors="ignore")

# If applyI18n exists, make sure it skips data-no-i18n for text and placeholders
if "function applyI18n" in js and "data-no-i18n" not in js:
    js = re.sub(
        r'(document\.querySelectorAll\("\[data-en\]\[data-ar\]"\)\.forEach\(\(el\)\s*=>\s*\{\n)',
        r'\1    if (el.hasAttribute("data-no-i18n")) return;\n',
        js
    )
    js = re.sub(
        r'(document\.querySelectorAll\("\[data-ph-en\]\[data-ph-ar\]"\)\.forEach\(\(el\)\s*=>\s*\{\n)',
        r'\1    if (el.hasAttribute("data-no-i18n")) return;\n',
        js
    )

# If applyI18n missing completely, inject minimal i18n core (safe, namespaced)
if "window.Tarmeez" not in js or "applyI18n" not in js:
    js += r"""

// --- TARMEez i18n core (injected) ---
window.Tarmeez = window.Tarmeez || {};
Tarmeez.getLang = function(){
  try{
    const v = (localStorage.getItem("tarmeez_lang") || "en").toLowerCase();
    return v === "ar" ? "ar" : "en";
  }catch(e){ return "en"; }
};

Tarmeez.setLang = function(lang){
  const v = (lang || "en").toLowerCase() === "ar" ? "ar" : "en";
  try{ localStorage.setItem("tarmeez_lang", v); }catch(e){}
  Tarmeez.applyI18n();
};

Tarmeez.applyI18n = function(){
  const lang = Tarmeez.getLang();

  // Direction: keep app stable, but switch dir for reading only
  document.documentElement.dir = (lang === "ar") ? "rtl" : "ltr";
  document.documentElement.lang = (lang === "ar") ? "ar" : "en";

  document.querySelectorAll("[data-en][data-ar]").forEach(el=>{
    if (el.hasAttribute("data-no-i18n")) return;
    el.textContent = (lang === "ar") ? el.dataset.ar : el.dataset.en;
  });

  document.querySelectorAll("[data-ph-en][data-ph-ar]").forEach(el=>{
    if (el.hasAttribute("data-no-i18n")) return;
    el.placeholder = (lang === "ar") ? el.dataset.phAr : el.dataset.phEn;
  });
};

document.addEventListener("DOMContentLoaded", () => {
  Tarmeez.applyI18n();
});
"""
else:
    # Ensure it runs on load even if core already existed
    if "Tarmeez.applyI18n();" not in js:
        js += "\ndocument.addEventListener('DOMContentLoaded', () => { try{ Tarmeez.applyI18n(); }catch(e){} });\n"

app_js.write_text(js, encoding="utf-8")

# 3) PATCH styles.css: lock header layout so brand title doesn't move with RTL/LTR
css_txt = css.read_text(encoding="utf-8", errors="ignore")

LOCK_MARK = "/* TARMEZ-HEADER-LOCK */"
if LOCK_MARK not in css_txt:
    css_txt += """

/* TARMEZ-HEADER-LOCK */
.tarmeezHeader{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}
.tarmeezBrand{
  flex:0 0 auto;
  min-width:260px;           /* يمنع الاهتزاز عند تبديل اللغة */
}
.tarmeezBrandTitle{
  white-space:nowrap;        /* الاسم ثابت */
  display:inline-block;
  min-width:180px;           /* يمنع تغيّر العرض */
}
.tarmeezNavlinks{
  flex:1 1 auto;
}
.tarmeezRightTools{
  flex:0 0 auto;
  min-width:170px;
  display:flex;
  justify-content:flex-end;
}
"""
css.write_text(css_txt, encoding="utf-8")

print(" تم: الهيدر يترجم بالكامل + اسم البرنامج مستثنى وثابت وما يتحرك.")
print(" الآن سو Hard Refresh: Ctrl+Shift+R بعد تشغيل السيرفر.")
