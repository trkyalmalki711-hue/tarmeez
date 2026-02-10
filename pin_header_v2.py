from pathlib import Path

ROOT = Path.cwd()
css = ROOT / "app" / "static" / "styles.css"
if not css.exists():
    raise SystemExit(" ما لقيت app/static/styles.css")

txt = css.read_text(encoding="utf-8", errors="ignore")

MARK = "/* TARMEZ-HEADER-PIN-V2 */"
if MARK not in txt:
    txt += """

/* TARMEZ-HEADER-PIN-V2 */
/* يثبت مكان البراند (اسم البرنامج) وما يخليه ينقلب مع RTL */
header.nav.card{
  direction:ltr !important;          /* ثبت اتجاه الهيدر */
  flex-direction:row !important;     /* لا تقلب صفوف */
  justify-content:space-between !important;
  align-items:center !important;
}

/* ثبّت ترتيب عناصر الهيدر مهما تغيّر dir للصفحة */
header.nav.card .brand{ order:0 !important; flex:0 0 auto !important; }
header.nav.card .navlinks{ order:1 !important; flex:1 1 auto !important; display:flex !important; justify-content:center !important; gap:10px !important; }
header.nav.card .rightTools{ order:2 !important; flex:0 0 auto !important; display:flex !important; justify-content:flex-end !important; }

/* اسم البرنامج نفسه لا ينقلب */
header.nav.card .brandTitle{
  direction:ltr !important;
  unicode-bidi:isolate !important;
  white-space:nowrap !important;
}

/* وقت العربي: خلي نص القوائم RTL بدون ما يقلب أماكنها */
html[dir="rtl"] header.nav.card .navlinks{
  direction:rtl !important;
}
"""
    css.write_text(txt, encoding="utf-8")
    print(" تم: تثبيت الهيدر نهائيًا (الاسم ما يتحرك).")
else:
    print("ℹ موجود مسبقًا: TARMEZ-HEADER-PIN-V2")
