from pathlib import Path
import re

ROOT = Path.cwd()

def must(p: Path):
    if not p.exists():
        raise SystemExit(f" ملف ناقص: {p}")
    return p

# ---------- Files ----------
header = must(ROOT / "app" / "templates" / "partials" / "header.html")
footer = must(ROOT / "app" / "templates" / "partials" / "footer.html")

dictionary = must(ROOT / "app" / "templates" / "dictionary.html")
quiz_home  = must(ROOT / "app" / "templates" / "quiz_home.html")
quiz_run   = must(ROOT / "app" / "templates" / "quiz_run.html")
cases_home = must(ROOT / "app" / "templates" / "cases_home.html")
cases_run  = must(ROOT / "app" / "templates" / "cases_run.html")

app_js     = must(ROOT / "app" / "static" / "app.js")
quiz_js    = must(ROOT / "app" / "static" / "app_quiz.js")
cases_js   = must(ROOT / "app" / "static" / "app_cases.js")

# ---------- 1) app.js: add support for data-no-i18n + dispatch lang event ----------
js = app_js.read_text(encoding="utf-8")

# add skip for data-no-i18n in applyI18n
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

# dispatch a custom event after language apply so pages/JS can react
if "tarmeez:lang" not in js:
    js = js.replace(
        "applyI18n();     // translate content",
        "applyI18n();     // translate content\n    window.dispatchEvent(new CustomEvent('tarmeez:lang', { detail: { lang: getLang() } }));"
    )

app_js.write_text(js, encoding="utf-8")

# ---------- 2) header.html (translate everything except program name) ----------
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
    <header class="nav card">
      <div class="brand">
        <div class="logo" aria-hidden="true"></div>
        <div class="brandText">
          <!-- اسم البرنامج ثابت: لا يترجم -->
          <div class="brandTitle" data-no-i18n="1">ترميز | Tarmeez</div>
          <div class="brandSub"
               data-en="CPT & ICD-10 Academy"
               data-ar="أكاديمية CPT و ICD-10">CPT & ICD-10 Academy</div>
        </div>
      </div>

      <nav class="navlinks" aria-label="Primary">
        <a class="pill" href="/" data-en="Home" data-ar="الرئيسية">Home</a>
        <a class="pill" href="/dictionary" data-en="Dictionary" data-ar="القاموس">Dictionary</a>
        <a class="pill" href="/quiz" data-en="Quiz" data-ar="الكويز">Quiz</a>
        <a class="pill" href="/cases" data-en="Cases" data-ar="الحالات">Cases</a>
        <a class="pill" href="/notes" data-en="Notes" data-ar="ملاحظات">Notes</a>
        <a class="pill" href="/about" data-en="About" data-ar="عن البرنامج">About</a>
        <a class="pill" href="/account" data-en="Account" data-ar="الحساب">Account</a>
        <a class="pill" href="/login" data-en="Login" data-ar="تسجيل الدخول">Login</a>
      </nav>

      <div class="rightTools">
        <div class="langToggle" aria-label="Language">
          <button class="btn btnGhost" data-lang-btn="en" onclick="Tarmeez.setLang('en')">English</button>
          <button class="btn btnGhost" data-lang-btn="ar" onclick="Tarmeez.setLang('ar')">العربية</button>
        </div>
      </div>
    </header>
"""
header.write_text(header_new, encoding="utf-8")

# ---------- 3) footer.html translateable ----------
footer_new = """    <div class="footer">
       <span id="yr"></span>
      <span data-no-i18n="1">Tarmeez</span>
      <span style="opacity:.7"></span>
      <span data-en="Built with FastAPI" data-ar="مبني باستخدام FastAPI">Built with FastAPI</span>
    </div>
  </div>

  <script>
    document.getElementById("yr").textContent = new Date().getFullYear();
  </script>

  <script src="/static/app.js"></script>
</body>
</html>
"""
footer.write_text(footer_new, encoding="utf-8")

# ---------- 4) Patch templates: Dictionary / Quiz / Cases ----------
def repl_file(path: Path, replacements: list[tuple[str,str]]):
    s = path.read_text(encoding="utf-8")
    for a,b in replacements:
        s = s.replace(a,b)
    path.write_text(s, encoding="utf-8")

# dictionary.html
repl_file(dictionary, [
    ("<h3>Dictionary</h3>",
     '<h3 data-en="Dictionary" data-ar="القاموس">Dictionary</h3>'),
    ("<div class=\"small\">Browse & search CPT / ICD with expandable lists</div>",
     '<div class="small" data-en="Browse & search CPT / ICD with expandable lists" data-ar="تصفح وابحث في CPT / ICD بقوائم قابلة للفتح">Browse & search CPT / ICD with expandable lists</div>'),
    ("<button id=\"btn-cpt\" class=\"btn btnPrimary\" onclick=\"setKind('cpt')\">CPT</button>",
     '<button id="btn-cpt" class="btn btnPrimary" onclick="setKind(\'cpt\')" data-no-i18n="1">CPT</button>'),
    ("<button id=\"btn-icd\" class=\"btn btnGhost\" onclick=\"setKind('icd')\">ICD</button>",
     '<button id="btn-icd" class="btn btnGhost" onclick="setKind(\'icd\')" data-no-i18n="1">ICD</button>'),
    ("placeholder=\"Search code or description...\"",
     'data-ph-en="Search code or description..." data-ph-ar="ابحث بالكود أو الوصف..." placeholder="Search code or description..."'),
    ("<option value=\"\">All Categories</option>",
     '<option value="" data-en="All Categories" data-ar="كل التصنيفات">All Categories</option>'),
    ("<option value=\"\">All Sections</option>",
     '<option value="" data-en="All Sections" data-ar="كل الأقسام">All Sections</option>'),
    ("<option value=\"\">All Ranges</option>",
     '<option value="" data-en="All Ranges" data-ar="كل النطاقات">All Ranges</option>'),
    ("<option value=\"\">All Chapters</option>",
     '<option value="" data-en="All Chapters" data-ar="كل الفصول">All Chapters</option>'),
    ("<option value=\"\">All Blocks</option>",
     '<option value="" data-en="All Blocks" data-ar="كل المجموعات">All Blocks</option>'),
    ("<button class=\"btn btnGhost\" onclick=\"resetFilters()\">Reset</button>",
     '<button class="btn btnGhost" onclick="resetFilters()" data-en="Reset" data-ar="إعادة ضبط">Reset</button>'),
])

# quiz_home.html
repl_file(quiz_home, [
    ("<h3>Quiz</h3>", '<h3 data-en="Quiz" data-ar="الكويز">Quiz</h3>'),
    ("<div class=\"small\">Choose difficulty and number of questions</div>",
     '<div class="small" data-en="Choose difficulty and number of questions" data-ar="اختر الصعوبة وعدد الأسئلة">Choose difficulty and number of questions</div>'),
    ("<strong>CPT Quiz</strong>", '<strong data-en="CPT Quiz" data-ar="كويز CPT">CPT Quiz</strong>'),
    ("<div class=\"small\">Interactive quiz from CPT data</div>",
     '<div class="small" data-en="Interactive quiz from CPT data" data-ar="كويز تفاعلي من بيانات CPT">Interactive quiz from CPT data</div>'),
    ("<strong>ICD Quiz</strong>", '<strong data-en="ICD Quiz" data-ar="كويز ICD">ICD Quiz</strong>'),
    ("<div class=\"small\">Interactive quiz from ICD-10 data</div>",
     '<div class="small" data-en="Interactive quiz from ICD-10 data" data-ar="كويز تفاعلي من بيانات ICD-10">Interactive quiz from ICD-10 data</div>'),
    ("<div class=\"small\" style=\"margin-bottom:6px\">Difficulty</div>",
     '<div class="small" style="margin-bottom:6px" data-en="Difficulty" data-ar="الصعوبة">Difficulty</div>'),
    ("<div class=\"small\" style=\"margin-bottom:6px\">Number of Questions</div>",
     '<div class="small" style="margin-bottom:6px" data-en="Number of Questions" data-ar="عدد الأسئلة">Number of Questions</div>'),
    ("<option value=\"easy\">Easy</option>",
     '<option value="easy" data-en="Easy" data-ar="سهل">Easy</option>'),
    ("<option value=\"medium\" selected>Medium</option>",
     '<option value="medium" selected data-en="Medium" data-ar="متوسط">Medium</option>'),
    ("<option value=\"hard\">Hard</option>",
     '<option value="hard" data-en="Hard" data-ar="صعب">Hard</option>'),
    ("Start CPT Quiz", '<span data-en="Start CPT Quiz" data-ar="ابدأ كويز CPT">Start CPT Quiz</span>'),
    ("Start ICD Quiz", '<span data-en="Start ICD Quiz" data-ar="ابدأ كويز ICD">Start ICD Quiz</span>'),
])

# quiz_run.html
repl_file(quiz_run, [
    ("<h3>Quiz</h3>", '<h3 data-en="Quiz" data-ar="الكويز">Quiz</h3>'),
    ("<div class=\"small\">Answer the questions below</div>",
     '<div class="small" data-en="Answer the questions below" data-ar="جاوب على الأسئلة التالية">Answer the questions below</div>'),
    ("<span>Difficulty:</span>", '<span data-en="Difficulty:" data-ar="الصعوبة:">Difficulty:</span>'),
    ("Questions:", '<span data-en="Questions:" data-ar="الأسئلة:">Questions:</span>'),
    ("Loading questions", '<span data-en="Loading questions" data-ar="جاري تحميل الأسئلة">Loading questions</span>'),
    ("Previous", '<span data-en="Previous" data-ar="السابق">Previous</span>'),
    ("Next", '<span data-en="Next" data-ar="التالي">Next</span>'),
    ("Submit", '<span data-en="Submit" data-ar="تسليم">Submit</span>'),
    ("Reload", '<span data-en="Reload" data-ar="إعادة تحميل">Reload</span>'),
])

# cases_home.html
repl_file(cases_home, [
    ("<h3>Cases</h3>", '<h3 data-en="Cases" data-ar="الحالات">Cases</h3>'),
    ("<div class=\"small\">Choose number of cases and start</div>",
     '<div class="small" data-en="Choose number of cases and start" data-ar="اختر عدد الحالات وابدأ">Choose number of cases and start</div>'),
    ("<strong>CPT Cases</strong>", '<strong data-en="CPT Cases" data-ar="حالات CPT">CPT Cases</strong>'),
    ("<div class=\"small\">Scenario questions from CPT data</div>",
     '<div class="small" data-en="Scenario questions from CPT data" data-ar="أسئلة سيناريو من بيانات CPT">Scenario questions from CPT data</div>'),
    ("<strong>ICD Cases</strong>", '<strong data-en="ICD Cases" data-ar="حالات ICD">ICD Cases</strong>'),
    ("<div class=\"small\">Scenario questions from ICD-10 data</div>",
     '<div class="small" data-en="Scenario questions from ICD-10 data" data-ar="أسئلة سيناريو من بيانات ICD-10">Scenario questions from ICD-10 data</div>'),
    ("<div class=\"small\" style=\"margin-bottom:6px\">Number of Cases</div>",
     '<div class="small" style="margin-bottom:6px" data-en="Number of Cases" data-ar="عدد الحالات">Number of Cases</div>'),
    ("Start CPT Cases", '<span data-en="Start CPT Cases" data-ar="ابدأ حالات CPT">Start CPT Cases</span>'),
    ("Start ICD Cases", '<span data-en="Start ICD Cases" data-ar="ابدأ حالات ICD">Start ICD Cases</span>'),
])

# cases_run.html
repl_file(cases_run, [
    ("<h3>Cases</h3>", '<h3 data-en="Cases" data-ar="الحالات">Cases</h3>'),
    ("<div class=\"small\">Choose the most appropriate code</div>",
     '<div class="small" data-en="Choose the most appropriate code" data-ar="اختر الكود الأنسب">Choose the most appropriate code</div>'),
    ("<span>Questions:</span>", '<span data-en="Questions:" data-ar="الأسئلة:">Questions:</span>'),
    ("Loading cases", '<span data-en="Loading cases" data-ar="جاري تحميل الحالات">Loading cases</span>'),
    ("Previous", '<span data-en="Previous" data-ar="السابق">Previous</span>'),
    ("Next", '<span data-en="Next" data-ar="التالي">Next</span>'),
    ("Submit", '<span data-en="Submit" data-ar="تسليم">Submit</span>'),
    ("Reload", '<span data-en="Reload" data-ar="إعادة تحميل">Reload</span>'),
])

# ---------- 5) Patch JS for Quiz/Cases dynamic strings ----------
def patch_js(path: Path, kind: str):
    s = path.read_text(encoding="utf-8")
    if "function t(" in s:
        path.write_text(s, encoding="utf-8")
        return

    helper = r"""
  function getLang(){
    try{
      return (window.Tarmeez && Tarmeez.getLang) ? Tarmeez.getLang() : ((localStorage.getItem("tarmeez_lang")||"en")==="ar"?"ar":"en");
    }catch(e){ return "en"; }
  }
  function t(en, ar){ return getLang()==="ar" ? ar : en; }
  function onLangChange(fn){
    window.addEventListener("tarmeez:lang", fn);
    window.addEventListener("storage", (e)=>{ if(e.key==="tarmeez_lang") fn(); });
  }
"""
    # insert helper near top inside DOMContentLoaded
    s = s.replace('document.addEventListener("DOMContentLoaded", async () => {',
                  'document.addEventListener("DOMContentLoaded", async () => {' + helper)

    if kind == "cases":
        s = s.replace("`Case ${index + 1} / ${total}`", "t(`Case ${index + 1} / ${total}`, `الحالة ${index + 1} / ${total}`)")
        s = s.replace("No cases available.", "t('No cases available.','لا توجد حالات متاحة.')")
        s = s.replace("<strong>Case ${index + 1}</strong>", "<strong>${t(`Case ${index + 1}`, `الحالة ${index + 1}`)}</strong>")
        s = s.replace("Loading cases", "${t('Loading cases','جاري تحميل الحالات')}")
        s = s.replace("Cases API error:", "${t('Cases API error:','خطأ في API الحالات:')}")
        s = s.replace("Correct answer", "t('Correct answer','الإجابة الصحيحة')")
        s = s.replace("Your choice", "t('Your choice','اختيارك')")
        s = s.replace("`<strong>${correct}</strong> / ${total} correct`", "`<strong>${correct}</strong> / ${total} ${t('correct','صحيح')}`")
        # re-apply render labels when language changes
        if "onLangChange" in s and "onLangChange(() =>" not in s:
            s = s.replace("await loadCases();", "onLangChange(()=>{ renderOne(); setButtons(); });\n  await loadCases();")

    if kind == "quiz":
        s = s.replace("`Question ${index + 1} / ${total}`", "t(`Question ${index + 1} / ${total}`, `السؤال ${index + 1} / ${total}`)")
        s = s.replace("No questions available.", "t('No questions available.','لا توجد أسئلة متاحة.')")
        s = s.replace("<strong>Question ${index + 1}</strong>", "<strong>${t(`Question ${index + 1}`, `السؤال ${index + 1}`)}</strong>")
        s = s.replace("Loading questions", "${t('Loading questions','جاري تحميل الأسئلة')}")
        s = s.replace("Quiz API error:", "${t('Quiz API error:','خطأ في API الكويز:')}")
        s = s.replace("Correct answer", "t('Correct answer','الإجابة الصحيحة')")
        s = s.replace("Your choice", "t('Your choice','اختيارك')")
        s = s.replace("`<strong>${correct}</strong> / ${total} correct`", "`<strong>${correct}</strong> / ${total} ${t('correct','صحيح')}`")
        if "onLangChange" in s and "onLangChange(() =>" not in s:
            s = s.replace("await loadQuiz();", "onLangChange(()=>{ renderOne(); setButtons(); });\n  await loadQuiz();")

    path.write_text(s, encoding="utf-8")

patch_js(cases_js, "cases")
patch_js(quiz_js, "quiz")

print(" تم تفعيل الترجمة للقاموس + الهيدر + الكويز + الحالات (مع استثناء اسم Tarmeez).")
print(" شغّل السيرفر وجرب زر العربية/English.")
