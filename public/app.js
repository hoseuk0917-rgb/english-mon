const BANK_URL = "../data/question_bank_v0_2.json";
const HISTORY_KEY = "englishmon.history.v0.1";

const state = {
  bank: null,
  pool: [],
  mission: [],
  index: 0,
  current: null,
  selectedOption: null,
  score: 0,
  checked: false,
  history: loadHistory(),
};

const el = {
  score: document.querySelector("#score"),
  unitSelect: document.querySelector("#unitSelect"),
  modeSelect: document.querySelector("#modeSelect"),
  startBtn: document.querySelector("#startBtn"),
  checkBtn: document.querySelector("#checkBtn"),
  nextBtn: document.querySelector("#nextBtn"),
  resetBtn: document.querySelector("#resetBtn"),
  modeBadge: document.querySelector("#modeBadge"),
  promptTitle: document.querySelector("#promptTitle"),
  progressText: document.querySelector("#progressText"),
  questionArea: document.querySelector("#questionArea"),
  feedback: document.querySelector("#feedback"),
  seenCount: document.querySelector("#seenCount"),
  correctCount: document.querySelector("#correctCount"),
  wrongCount: document.querySelector("#wrongCount"),
  weakCount: document.querySelector("#weakCount"),
};

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return { seen: 0, correct: 0, wrong: 0, byWord: {} };
    return JSON.parse(raw);
  } catch {
    return { seen: 0, correct: 0, wrong: 0, byWord: {} };
  }
}

function saveHistory() {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(state.history));
}

function updateStats() {
  el.score.textContent = String(state.score);
  el.seenCount.textContent = String(state.history.seen || 0);
  el.correctCount.textContent = String(state.history.correct || 0);
  el.wrongCount.textContent = String(state.history.wrong || 0);

  const weak = Object.values(state.history.byWord || {}).filter(x => (x.wrong || 0) > 0).length;
  el.weakCount.textContent = String(weak);
}

function shuffle(items) {
  const arr = [...items];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function modeName(type) {
  return {
    meaning_sniper: "뜻 스나이퍼",
    definition_sniper: "영어뜻 스나이퍼",
    cipher_blank: "암호 해독",
    typo_repair: "오타 수리",
    boss_input: "보스 입력",
    mixed: "랜덤 미션",
  }[type] || type;
}

function normalizeAnswer(value) {
  return String(value || "").trim().toLowerCase();
}

async function init() {
  const res = await fetch(BANK_URL);
  if (!res.ok) throw new Error("question bank load failed");
  state.bank = await res.json();

  el.startBtn.addEventListener("click", startMission);
  el.checkBtn.addEventListener("click", checkAnswer);
  el.nextBtn.addEventListener("click", nextQuestion);
  el.resetBtn.addEventListener("click", resetHistory);

  updateStats();
}

function startMission() {
  const unit = el.unitSelect.value;
  const mode = el.modeSelect.value;

  let questions = state.bank.questions;

  if (unit !== "all") {
    questions = questions.filter(q => String(q.unit) === unit);
  }

  if (mode !== "mixed") {
    questions = questions.filter(q => q.type === mode);
  }

  state.pool = shuffle(questions);
  state.mission = state.pool.slice(0, 10);
  state.index = 0;
  state.score = 0;
  state.checked = false;

  renderQuestion();
  updateStats();
}

function renderQuestion() {
  state.current = state.mission[state.index];
  state.selectedOption = null;
  state.checked = false;

  el.feedback.textContent = "";
  el.feedback.className = "feedback";
  el.checkBtn.disabled = false;
  el.nextBtn.disabled = true;

  const q = state.current;

  if (!q) {
    el.modeBadge.textContent = "완료";
    el.promptTitle.textContent = "미션 완료";
    el.progressText.textContent = "10 / 10";
    el.questionArea.innerHTML = `<p class="big-word">🎉</p><p class="meaning">오늘 미션 완료!</p>`;
    el.checkBtn.disabled = true;
    el.nextBtn.disabled = true;
    return;
  }

  el.modeBadge.textContent = modeName(q.type);
  el.progressText.textContent = `${state.index + 1} / ${state.mission.length}`;

  if (q.type === "meaning_sniper" || q.type === "definition_sniper") renderMeaningSniper(q);
  if (q.type === "cipher_blank") renderCipherBlank(q);
  if (q.type === "typo_repair") renderTypoRepair(q);
  if (q.type === "boss_input") renderBossInput(q);
}

function renderMeaningSniper(q) {
  el.promptTitle.textContent = "PDF 영어뜻을 골라라";
  const options = q.options.map(opt => `
    <button class="option" data-option="${opt.option_id}">
      ${opt.option_id}. ${escapeHtml(opt.text)}
    </button>
  `).join("");

  el.questionArea.innerHTML = `
    <div>
      <div class="big-word">${escapeHtml(q.prompt.word)}</div>
      <div class="options">${options}</div>
    </div>
  `;

  document.querySelectorAll(".option").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".option").forEach(x => x.classList.remove("selected"));
      btn.classList.add("selected");
      state.selectedOption = btn.dataset.option;
    });
  });
}

function renderCipherBlank(q) {
  el.promptTitle.textContent = "가려진 철자를 복구하라";
  el.questionArea.innerHTML = `
    <div>
      <p class="meaning">${escapeHtml(q.prompt.meaning_ko)}</p>
      <div class="masked">${escapeHtml(q.prompt.masked_word)}</div>
      <input id="answerInput" class="answer-input" autocomplete="off" placeholder="전체 단어 입력" />
    </div>
  `;
  focusInput();
}

function renderTypoRepair(q) {
  el.promptTitle.textContent = "오타몬을 수리하라";
  el.questionArea.innerHTML = `
    <div>
      <p class="meaning">${escapeHtml(q.prompt.meaning_ko)}</p>
      <div class="big-word typo">${escapeHtml(q.prompt.typo_word)}</div>
      <input id="answerInput" class="answer-input" autocomplete="off" placeholder="올바른 단어 입력" />
    </div>
  `;
  focusInput();
}

function renderBossInput(q) {
  el.promptTitle.textContent = "보스에게 전체 단어를 입력하라";
  el.questionArea.innerHTML = `
    <div>
      <p class="meaning">${escapeHtml(q.prompt.meaning_ko)} · ${escapeHtml(q.prompt.pos)}</p>
      <input id="answerInput" class="answer-input" autocomplete="off" placeholder="영어 단어 전체 입력" />
    </div>
  `;
  focusInput();
}

function focusInput() {
  const input = document.querySelector("#answerInput");
  if (!input) return;

  input.focus();
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !state.checked) {
      checkAnswer();
    } else if (e.key === "Enter" && state.checked) {
      nextQuestion();
    }
  });
}

function checkAnswer() {
  if (!state.current || state.checked) return;

  const q = state.current;
  let isCorrect = false;
  let submitted = "";

  if (q.type === "meaning_sniper") {
    submitted = state.selectedOption;
    isCorrect = submitted === q.answer;
  } else {
    const input = document.querySelector("#answerInput");
    submitted = input ? input.value : "";
    isCorrect = normalizeAnswer(submitted) === normalizeAnswer(q.answer);
  }

  state.checked = true;
  el.checkBtn.disabled = true;
  el.nextBtn.disabled = false;

  recordResult(q, isCorrect, submitted);

  if (isCorrect) {
    state.score += q.difficulty || 1;
    el.feedback.textContent = "정답! 단어몬 포획 성공";
    el.feedback.className = "feedback good";
  } else {
    el.feedback.textContent = `오답몬 발견. 정답은 ${q.answer}`;
    el.feedback.className = "feedback bad";
  }

  updateStats();
}

function nextQuestion() {
  state.index += 1;
  renderQuestion();
}

function recordResult(q, isCorrect, submitted) {
  const h = state.history;
  h.seen = (h.seen || 0) + 1;
  h.correct = (h.correct || 0) + (isCorrect ? 1 : 0);
  h.wrong = (h.wrong || 0) + (isCorrect ? 0 : 1);

  h.byWord = h.byWord || {};
  h.byWord[q.word_id] = h.byWord[q.word_id] || {
    seen: 0,
    correct: 0,
    wrong: 0,
    lastWrongAnswer: "",
    types: {},
  };

  const item = h.byWord[q.word_id];
  item.seen += 1;
  item.correct += isCorrect ? 1 : 0;
  item.wrong += isCorrect ? 0 : 1;
  item.types[q.type] = item.types[q.type] || { seen: 0, correct: 0, wrong: 0 };
  item.types[q.type].seen += 1;
  item.types[q.type].correct += isCorrect ? 1 : 0;
  item.types[q.type].wrong += isCorrect ? 0 : 1;

  if (!isCorrect) {
    item.lastWrongAnswer = String(submitted || "");
  }

  saveHistory();
}

function resetHistory() {
  if (!confirm("개인 이력을 초기화할까?")) return;
  localStorage.removeItem(HISTORY_KEY);
  state.history = loadHistory();
  state.score = 0;
  updateStats();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

init().catch(err => {
  console.error(err);
  el.questionArea.innerHTML = `<p class="empty">데이터 로드 실패: ${escapeHtml(err.message)}</p>`;
});

