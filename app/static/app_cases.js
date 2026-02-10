// app/static/app_cases.js
document.addEventListener("DOMContentLoaded", async () => {
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

  const cfg = document.getElementById("casesConfig");
  const root = document.getElementById("casesRoot");

  const btnPrev = document.getElementById("prevCases");
  const btnNext = document.getElementById("nextCases");
  const btnSubmit = document.getElementById("submitCases");
  const btnReload = document.getElementById("reloadCases");

  const progress = document.getElementById("casesProgress");
  const result = document.getElementById("casesResult");

  if (!cfg || !root) return;

  let kind = (cfg.dataset.kind || "cpt").toLowerCase();
  if (kind === "icd10") kind = "icd";

  let n = Number(cfg.dataset.n || 10);
  n = Math.max(5, Math.min(50, n));

  let data = null;
  let index = 0;
  let graded = false;
  const picks = {};

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[c]));

  function setButtons() {
    const total = data?.questions?.length || 0;
    if (progress) progress.textContent = total ? t(`Case ${index + 1} / ${total}`, `الحالة ${index + 1} / ${total}`) : "";
    if (btnPrev) btnPrev.disabled = (index <= 0);
    if (btnNext) btnNext.disabled = (index >= total - 1);
  }

  function renderOne() {
    const qs = data?.questions || [];
    const total = qs.length;
    if (!total) {
      root.innerHTML = `<div class="small">t('No cases available.','لا توجد حالات متاحة.')</div>`;
      return;
    }

    const q = qs[index];
    const chosen = picks[index];

    root.innerHTML = `
      <div class="card section" style="margin-bottom:12px; padding:14px; background:rgba(0,0,0,0.14);">
        <div style="display:flex; justify-content:space-between; gap:12px; align-items:center">
          <strong>${t(`Case ${index + 1}`, `الحالة ${index + 1}`)}</strong>
          <span class="small">${esc(kind.toUpperCase())}</span>
        </div>

        <div class="small" style="margin-top:10px">${esc(q.prompt)}</div>

        <div style="margin-top:14px">
          ${(q.options || []).map(opt => {
            const isPicked = (chosen === opt);
            const bg = isPicked ? "rgba(255,255,255,0.06)" : "transparent";
            const ol = isPicked ? "1px solid rgba(255,255,255,0.18)" : "1px solid rgba(255,255,255,0.06)";
            return `
              <div data-choice-row style="padding:10px 12px; border-radius:12px; cursor:pointer; margin-bottom:10px; background:${bg}; outline:${ol};">
                <label style="display:flex; align-items:center; gap:10px; cursor:pointer; margin:0">
                  <input type="radio" name="c_one" value="${esc(opt)}" ${isPicked ? "checked" : ""}>
                  <span class="small">${esc(opt)}</span>
                </label>
                <div class="small" data-feedback style="display:none; margin-top:6px"></div>
              </div>
            `;
          }).join("")}
        </div>
      </div>
    `;

    document.querySelectorAll("[data-choice-row]").forEach(row => {
      row.addEventListener("click", () => {
        if (graded) return;
        const inp = row.querySelector("input[type=radio]");
        if (!inp) return;
        inp.checked = true;
        picks[index] = inp.value;
        renderOne();
        setButtons();
      });
    });

    if (graded) {
      const correct = q.answer;
      const chosenVal = picks[index];

      document.querySelectorAll("[data-choice-row]").forEach(row => {
        const inp = row.querySelector("input[type=radio]");
        const fb = row.querySelector("[data-feedback]");
        const val = inp ? inp.value : "";

        row.style.background = "transparent";
        row.style.outline = "1px solid rgba(255,255,255,0.06)";
        if (fb) fb.style.display = "none";

        if (val === correct) {
          row.style.background = "rgba(0,255,160,0.06)";
          row.style.outline = "1px solid rgba(0,255,160,0.25)";
          if (fb) {
            fb.style.display = "block";
            fb.textContent = "t('Correct answer','الإجابة الصحيحة')";
            fb.style.color = "rgba(0,255,160,0.9)";
          }
        } else if (chosenVal && val === chosenVal) {
          row.style.background = "rgba(255,80,80,0.06)";
          row.style.outline = "1px solid rgba(255,80,80,0.25)";
          if (fb) {
            fb.style.display = "block";
            fb.textContent = "t('Your choice','اختيارك')";
            fb.style.color = "rgba(255,120,120,0.95)";
          }
        }

        const inp2 = row.querySelector("input[type=radio]");
        if (inp2) inp2.disabled = true;
      });
    }

    setButtons();
  }

  async function loadCases() {
    graded = false;
    result.textContent = "";
    root.innerHTML = `<div class="small">${t('Loading cases','جاري تحميل الحالات')}…</div>`;

    const url = `/api/ai/cases/${encodeURIComponent(kind)}?n=${encodeURIComponent(n)}`;
    const res = await fetch(url);

    if (!res.ok) {
      root.innerHTML = `<div class="small" style="color:var(--bad)">${t('Cases API error:','خطأ في API الحالات:')} ${res.status}</div>`;
      return;
    }

    data = await res.json();
    index = 0;
    for (const k of Object.keys(picks)) delete picks[k];

    renderOne();
  }

  function gradeAll() {
    if (!data?.questions?.length) return;
    graded = true;

    let correct = 0;
    const total = data.questions.length;

    for (let i = 0; i < total; i++) {
      const q = data.questions[i];
      if (picks[i] && picks[i] === q.answer) correct++;
    }

    result.innerHTML = `<strong>${correct}</strong> / ${total} ${t('correct','صحيح')}`;
    renderOne();
  }

  btnPrev?.addEventListener("click", () => {
    if (index > 0) {
      index--;
      renderOne();
    }
  });

  btnNext?.addEventListener("click", () => {
    const total = data?.questions?.length || 0;
    if (index < total - 1) {
      index++;
      renderOne();
    }
  });

  btnSubmit?.addEventListener("click", gradeAll);
  btnReload?.addEventListener("click", loadCases);

  onLangChange(()=>{ renderOne(); setButtons(); });
  await loadCases();
});
