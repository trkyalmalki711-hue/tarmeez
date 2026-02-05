// app/static/js/quiz.js
document.addEventListener("DOMContentLoaded", async () => {
  const root = document.getElementById("quizRoot");
  const submitBtn = document.getElementById("submitBtn");
  const resultBox = document.getElementById("resultBox");
  const reloadBtn = document.getElementById("reloadBtn");
  const qCount = document.getElementById("qCount");

  // config from HTML
  const cfg = document.getElementById("quizConfig");
  const KIND = (cfg?.dataset?.kind || "cpt").toLowerCase();
  let N = Number(cfg?.dataset?.n || 10);

  let questions = [];
  let answers = {}; // i -> chosen option index

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[c]));

  function render() {
    if (!questions.length) {
      root.innerHTML = `<div class="muted">No questions found.</div>`;
      return;
    }

    root.innerHTML = questions.map((q, i) => {
      const hintBtn = q.hint
        ? `<button class="btn hintbtn" data-i="${i}" type="button">Show hint</button>`
        : "";

      const hintBox = q.hint
        ? `<div class="hintbox muted" id="hint_${i}" style="display:none;">💡 ${esc(q.hint)}</div>`
        : "";

      const opts = (q.options || []).map((opt, j) => `
        <label class="opt" data-i="${i}" data-j="${j}">
          <input type="radio" name="q_${i}" value="${j}">
          <span>${esc(opt)}</span>
        </label>
      `).join("");

      return `
        <div class="qcard" id="qcard_${i}">
          <div class="qhead">
            <div class="qnum">Q${i + 1}</div>
            <div class="qtext">${esc(q.prompt || "")}</div>
          </div>

          <div class="hintrow">${hintBtn}</div>
          ${hintBox}

          <div class="opts">${opts}</div>
          <div class="hint muted" id="state_${i}">Pick one answer.</div>
        </div>
      `;
    }).join("");

    // radio change
    root.querySelectorAll("input[type=radio]").forEach((r) => {
      r.addEventListener("change", (e) => {
        const idx = Number(e.target.name.split("_")[1]);
        answers[idx] = Number(e.target.value);
      });
    });

    // hint toggle
    root.querySelectorAll(".hintbtn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const i = btn.dataset.i;
        const box = document.getElementById(`hint_${i}`);
        if (!box) return;
        const open = box.style.display === "block";
        box.style.display = open ? "none" : "block";
        btn.textContent = open ? "Show hint" : "Hide hint";
      });
    });
  }

  async function loadQuiz() {
    resultBox.textContent = "";
    answers = {};
    root.innerHTML = `<div class="muted">Loading questions...</div>`;

    // IMPORTANT: your API is /quiz/{kind}?n=...
const url = `/api/quiz/${encodeURIComponent(KIND)}?n=${encodeURIComponent(N)}`;
    const res = await fetch(url);

    if (!res.ok) {
      root.innerHTML = `<div class="err">API error: ${res.status}</div>`;
      return;
    }

    const data = await res.json();
    questions = (data.questions || []).map(q => ({
      prompt: q.prompt,
      options: q.options || [],
      answer: q.answer,
      hint: q.hint || ""
    }));

    render();
  }

  function grade() {
    let correct = 0;
    let answered = 0;

    questions.forEach((q, i) => {
      const pickedIdx = answers[i];
      const correctIdx = (q.options || []).indexOf(q.answer);

      const state = document.getElementById(`state_${i}`);
      const card = document.getElementById(`qcard_${i}`);

      if (pickedIdx !== undefined) answered++;

      // reset classes
      if (card) {
        card.querySelectorAll(".opt").forEach(el => el.classList.remove("ok", "bad"));
      }

      if (pickedIdx === undefined) {
        if (state) state.textContent = "Not answered.";
        return;
      }

      if (pickedIdx === correctIdx) {
        correct++;
        if (state) state.textContent = "Correct ✅";
      } else {
        if (state) state.textContent = `Wrong ❌ (Correct: ${q.answer})`;
      }

      // highlight options
      if (card) {
        const opts = card.querySelectorAll(".opt");
        opts.forEach((el) => {
          const j = Number(el.getAttribute("data-j"));
          if (j === correctIdx) el.classList.add("ok");
          if (j === pickedIdx && pickedIdx !== correctIdx) el.classList.add("bad");
        });
      }
    });

    const score = Math.round((correct / questions.length) * 100);
    resultBox.innerHTML = `
      <div class="score">
        <div class="score-big">${score}%</div>
        <div class="score-sub">${correct} / ${questions.length} correct • ${answered} answered</div>
      </div>
    `;
  }

  submitBtn?.addEventListener("click", grade);

  reloadBtn?.addEventListener("click", () => {
    const v = Number(qCount?.value || 10);
    N = Math.min(50, Math.max(5, v));
    if (cfg) cfg.dataset.n = String(N);
    loadQuiz();
  });

  loadQuiz();
});
