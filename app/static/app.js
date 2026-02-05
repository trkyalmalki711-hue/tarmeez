let lang = "en";

const TEXT = {
  en: {
    title: "CPT & ICD-10 Academy",
    cpt: "CPT Search",
    icd: "ICD-10 Search",
    cpt_ph: "Search CPT...",
    icd_ph: "Search ICD-10..."
  },
  ar: {
    title: "أكاديمية CPT و ICD-10",
    cpt: "البحث في CPT",
    icd: "البحث في ICD-10",
    cpt_ph: "ابحث عن كود CPT...",
    icd_ph: "ابحث عن كود ICD-10..."
  }
};

function setLang(l) {
  lang = l;
  document.documentElement.lang = l;
  document.body.dir = l === "ar" ? "rtl" : "ltr";

  document.getElementById("title").innerText = TEXT[l].title;
  document.getElementById("cpt-title").innerText = TEXT[l].cpt;
  document.getElementById("icd-title").innerText = TEXT[l].icd;
  document.getElementById("cpt-input").placeholder = TEXT[l].cpt_ph;
  document.getElementById("icd-input").placeholder = TEXT[l].icd_ph;
}

async function searchCPT() {
  const q = document.getElementById("cpt-input").value;
  if (!q) return;

  const res = await fetch(`/search/cpt?q=${q}`);
  const data = await res.json();

  const ul = document.getElementById("cpt-results");
  ul.innerHTML = "";
  data.results.forEach(r => {
    ul.innerHTML += `<li><b>${r.code}</b> - ${r.description}</li>`;
  });
}

async function searchICD() {
  const q = document.getElementById("icd-input").value;
  if (!q) return;

  const res = await fetch(`/search/icd10?q=${q}`);
  const data = await res.json();

  const ul = document.getElementById("icd-results");
  ul.innerHTML = "";
  data.results.forEach(r => {
    ul.innerHTML += `<li><b>${r.code}</b> - ${r.description}</li>`;
  });
}

// default language
setLang("en");
