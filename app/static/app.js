/* Tarmeez - Global UI + Language + Translations
   - Uses localStorage key: tarmeez_lang ("en" | "ar")
   - Applies dir/lang
   - Translates elements with data-en/data-ar
   - Translates placeholders with data-ph-en/data-ph-ar
*/

(function () {
  const KEY = "tarmeez_lang";

  function getLang() {
    const v = (localStorage.getItem(KEY) || "en").toLowerCase();
    return v === "ar" ? "ar" : "en";
  }

  function setLang(lang) {
    const v = (lang || "en").toLowerCase() === "ar" ? "ar" : "en";
    localStorage.setItem(KEY, v);
    applyLang();     // apply immediately
    applyI18n();     // translate content
  }

  function applyLang() {
    const lang = getLang();
    document.documentElement.lang = lang;
    document.body.dir = lang === "ar" ? "rtl" : "ltr";
    document.body.setAttribute("data-lang", lang);

    // Optional: highlight lang buttons if they exist
    const btnEn = document.querySelector('[data-lang-btn="en"]');
    const btnAr = document.querySelector('[data-lang-btn="ar"]');
    if (btnEn && btnAr) {
      btnEn.classList.toggle("btnPrimary", lang === "en");
      btnAr.classList.toggle("btnPrimary", lang === "ar");
      btnEn.classList.toggle("btnGhost", lang !== "en");
      btnAr.classList.toggle("btnGhost", lang !== "ar");
    }
  }

  function applyI18n() {
    const lang = getLang();

    // Translate text content
    document.querySelectorAll("[data-en][data-ar]").forEach((el) => {
      el.textContent = lang === "ar" ? el.dataset.ar : el.dataset.en;
    });

    // Translate placeholders
    document.querySelectorAll("[data-ph-en][data-ph-ar]").forEach((el) => {
      el.setAttribute("placeholder", lang === "ar" ? el.dataset.phAr : el.dataset.phEn);
    });

    // Translate title if provided
    const titleEl = document.querySelector("title[data-en][data-ar]");
    if (titleEl) {
      titleEl.textContent = lang === "ar" ? titleEl.dataset.ar : titleEl.dataset.en;
    }

    // Welcome text (optional)
    const welcome = document.getElementById("welcomeText");
    if (welcome) {
      welcome.textContent =
        lang === "ar"
          ? "ياهلا! خلّنا نسهّل عليك CPT و ICD-10 🔎"
          : "Welcome! Let’s make CPT & ICD-10 easy 🔎";
    }
  }

  // Expose to window so header buttons can call it
  window.Tarmeez = window.Tarmeez || {};
  window.Tarmeez.setLang = setLang;
  window.Tarmeez.getLang = getLang;
  window.Tarmeez.applyI18n = applyI18n;

  // Backward compatibility if your header calls setLang('ar')
  window.setLang = setLang;

  // Init on load
  function init() {
    applyLang();
    applyI18n();

    // If language changes from another tab
    window.addEventListener("storage", (e) => {
      if (e.key === KEY) {
        applyLang();
        applyI18n();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
