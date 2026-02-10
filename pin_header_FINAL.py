from pathlib import Path

ROOT = Path.cwd()
css = ROOT / "app" / "static" / "styles.css"
if not css.exists():
    raise SystemExit(" ما لقيت app/static/styles.css")

txt = css.read_text(encoding="utf-8", errors="ignore")

MARK = "/* TARMEZ-FINAL-PIN */"
if MARK not in txt:
    txt += """

/* TARMEZ-FINAL-PIN */
/* يمسك الهيدر الحقيقي عندك (.nav.card) ويمنع قلبه يمين/يسار مع RTL */
html[dir="rtl"] .nav.card,
html[dir="ltr"] .nav.card,
.nav.card{
  direction:ltr !important;          /* ثبّت اتجاه الهيدر نفسه */
  flex-direction:row !important;     /* الغِ row-reverse نهائيًا */
  justify-content:space-between !important;
  align-items:center !important;
}

/* ثبّت ترتيب العناصر داخل الهيدر */
.nav.card .brand{
  order:0 !important;
  flex:0 0 auto !important;
  margin-left:0 !important;
  margin-right:0 !important;
  direction:ltr !important;
}

.nav.card .navlinks{
  order:1 !important;
  flex:1 1 auto !important;
  display:flex !important;
  justify-content:center !important;
  align-items:center !important;
  gap:10px !important;
}

/* خلِّ نص الروابط عربي بدون ما يقلب أماكنها */
html[dir="rtl"] .nav.card .navlinks{
  direction:rtl !important;
}

.nav.card .rightTools{
  order:2 !important;
  flex:0 0 auto !important;
  display:flex !important;
  justify-content:flex-end !important;
  align-items:center !important;
}

/* اسم البرنامج ثابت + ما يلف */
.nav.card .brandTitle{
  white-space:nowrap !important;
  unicode-bidi:isolate !important;
  direction:ltr !important;
}
"""
    css.write_text(txt, encoding="utf-8")
    print(" تم: ثبتنا الهيدر على .nav.card (الاسم ما عاد ينقلب مع العربي).")
else:
    print("ℹ موجود مسبقًا: TARMEZ-FINAL-PIN")
