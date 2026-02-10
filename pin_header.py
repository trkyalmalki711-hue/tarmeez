from pathlib import Path

ROOT = Path.cwd()
css = ROOT / "app" / "static" / "styles.css"
if not css.exists():
    raise SystemExit(" ما لقيت app/static/styles.css")

txt = css.read_text(encoding="utf-8", errors="ignore")

MARK = "/* TARMEZ-HEADER-PIN */"
if MARK not in txt:
    txt += """

/* TARMEZ-HEADER-PIN */
/* الهدف: اسم البرنامج (البراند) يظل ثابت بمكانه حتى مع RTL */
.tarmeezHeader{
  direction:ltr !important;          /* يثبت ترتيب عناصر الهيدر */
  flex-direction:row !important;
  justify-content:space-between !important;
  align-items:center !important;
}

/* البراند دائمًا يسار */
.tarmeezBrand{
  order:0 !important;
  flex:0 0 auto !important;
}

/* نص اسم البرنامج ثابت وما ينقلب */
.tarmeezBrandTitle{
  direction:ltr !important;
  unicode-bidi:isolate !important;
  white-space:nowrap !important;
  min-width:180px !important;
}

/* القوائم بالوسط ومكانها ثابت */
.tarmeezNavlinks{
  order:1 !important;
  flex:1 1 auto !important;
  display:flex !important;
  justify-content:center !important;
  gap:10px !important;
}

/* لما تكون الصفحة RTL خلّي نص القوائم RTL بدون ما يقلب مكانها */
html[dir="rtl"] .tarmeezNavlinks{
  direction:rtl !important;
}

/* أدوات اللغة دائمًا يمين */
.tarmeezRightTools{
  order:2 !important;
  flex:0 0 auto !important;
  display:flex !important;
  justify-content:flex-end !important;
  min-width:170px !important;
}
"""

    css.write_text(txt, encoding="utf-8")
    print(" ثبتنا الهيدر: الاسم صار ثابت وما يتحرك مع الترجمة.")
else:
    print("ℹ موجود مسبقًا: TARMEZ-HEADER-PIN")

