from pathlib import Path

ROOT = Path.cwd()
css = ROOT / "app" / "static" / "styles.css"
if not css.exists():
    raise SystemExit(" ما لقيت app/static/styles.css")

txt = css.read_text(encoding="utf-8", errors="ignore")

MARK = "/* TARMEZ-HEADER-ABS-PIN */"
if MARK not in txt:
    txt += """

/* TARMEZ-HEADER-ABS-PIN */
/* حل قاطع: تثبيت مواقع الهيدر بالـabsolute (الاسم ثابت مهما كان RTL/LTR) */
header.nav.card{
  position:relative !important;
  min-height:72px !important;
  padding-left:300px !important;   /* مساحة للبراند يسار */
  padding-right:220px !important;  /* مساحة للأدوات يمين */
}

/* البراند ثابت يسار */
header.nav.card .brand{
  position:absolute !important;
  left:18px !important;
  top:50% !important;
  transform:translateY(-50%) !important;
  margin:0 !important;
  flex:0 0 auto !important;
  direction:ltr !important;
}

/* اسم البرنامج نفسه لا ينقلب ولا يلتف */
header.nav.card .brandTitle{
  white-space:nowrap !important;
  unicode-bidi:isolate !important;
  direction:ltr !important;
}

/* الروابط بالنص */
header.nav.card .navlinks{
  position:relative !important;
  display:flex !important;
  justify-content:center !important;
  align-items:center !important;
  flex-wrap:wrap !important;
  gap:10px !important;
}

/* الأدوات ثابت يمين */
header.nav.card .rightTools{
  position:absolute !important;
  right:18px !important;
  top:50% !important;
  transform:translateY(-50%) !important;
  display:flex !important;
  justify-content:flex-end !important;
  align-items:center !important;
}

/* وقت العربي: نخلي نص الروابط RTL بدون ما نغير أماكن العناصر */
html[dir="rtl"] header.nav.card .navlinks{
  direction:rtl !important;
}
"""
    css.write_text(txt, encoding="utf-8")
    print(" تم: تثبيت الهيدر بشكل قاطع (الاسم ما يتحرك نهائياً).")
else:
    print("ℹ موجود مسبقًا: TARMEZ-HEADER-ABS-PIN")
