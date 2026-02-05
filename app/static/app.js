/* ======================================================
   Tarmeez App.js
   Handles:
   - Language (AR / EN)
   - Active navigation
   - Basic UI fixes
====================================================== */

/* -----------------------
   TRANSLATIONS
----------------------- */
const translations = {
  en: {
    home: "Home",
    dictionary: "Dictionary",
    quiz: "Quiz",
    cases: "Cases",
    notes: "Notes",
    about: "About",
    login: "Login",
    welcome: "Welcome to Tarmeez"
  },
  ar: {
    home: "الرئيسية",
    dictionary: "القاموس",
    quiz: "الكويز",
    cases: "الحالات",
    notes: "الملاحظات",
    about: "حول",
    login: "تسجيل الدخول",
    welcome: "مرحبًا بك في ترميز"
  }
};

/* -----------------------
   LANGUAGE HANDLER
----------------------- */
function setLanguage(lang) {
  localStorage.setItem("tarmeez_lang", lang);
  document.documentElement.lang = lang;
  document.body.dir = lang === "ar" ? "rtl" : "ltr";

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });
}

function initLanguage() {
  const savedLang = localStorage.getItem("tarmeez_lang") || "en";
  setLanguage(savedLang);
}

/* -----------------------
   ACTIVE NAV LINK
----------------------- */
function setActiveNav() {
  const currentPath = window.location.pathname;
  const links = document.querySelectorAll("#main-nav a");

  links.forEach(link => {
    link.classList.remove("active");
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
}

/* -----------------------
   FIX BLUE LINKS (SAFETY)
----------------------- */
function fixLinksColor() {
  document.querySelectorAll("a").forEach(a => {
    a.style.color = "inherit";
    a.style.textDecoration = "none";
  });
}

/* -----------------------
   INIT
----------------------- */
document.addEventListener("DOMContentLoaded", () => {
  initLanguage();
  setActiveNav();
  fixLinksColor();

  // Language buttons
  const btnEn = document.getElementById("lang-en");
  const btnAr = document.getElementById("lang-ar");

  if (btnEn) btnEn.addEventListener("click", () => setLanguage("en"));
  if (btnAr) btnAr.addEventListener("click", () => setLanguage("ar"));
});
