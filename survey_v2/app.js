const SESSIONS_KEY = 'sure-tagger-survey-v2-sessions-v4';

const state = {
  sessionId: null,
  createdAt: null,
  questions: [],
  answers: {},
  submitted: new Set(),
  current: 0,
  saving: false,
};

const $ = (id) => document.getElementById(id);

function shuffle(items) {
  const result = [...items];
  for (let index = result.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
  }
  return result;
}

function readSessions() {
  try {
    const sessions = JSON.parse(localStorage.getItem(SESSIONS_KEY) || '[]');
    return Array.isArray(sessions) ? sessions : [];
  } catch (error) {
    return [];
  }
}

function writeSessions(sessions) {
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
}

function serializeState() {
  return {
    sessionId: state.sessionId,
    createdAt: state.createdAt,
    questions: state.questions,
    answers: state.answers,
    submitted: [...state.submitted],
    completedAt: state.completedAt || null,
  };
}

function persistState() {
  const sessions = readSessions().filter((session) => session.sessionId !== state.sessionId);
  sessions.push(serializeState());
  writeSessions(sessions);
}

function newSession() {
  const questions = shuffle(window.SURVEY_SAMPLES).map((sample, index) => {
    const options = shuffle([
      {audio: sample.sure, method: 'sure_tagger'},
      {audio: sample.captioner, method: 'captioner'},
    ]);
    return {
      question_number: index + 1,
      sample_id: sample.sample_id,
      position: sample.position,
      reference: sample.reference,
      options: {A: options[0], B: options[1]},
    };
  });
  state.sessionId = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
  state.createdAt = new Date().toISOString();
  state.questions = questions;
  state.answers = {};
  state.submitted = new Set();
  state.current = 0;
  state.completedAt = null;
  persistState();
}

function restoreOrCreateSession() {
  const sessions = readSessions();
  const active = [...sessions].reverse().find((session) => !session.completedAt);
  if (!active) {
    newSession();
    return;
  }
  state.sessionId = active.sessionId;
  state.createdAt = active.createdAt;
  state.questions = active.questions;
  state.answers = active.answers || {};
  state.submitted = new Set(active.submitted || []);
  state.current = Math.min(state.submitted.size, state.questions.length - 1);
  state.completedAt = active.completedAt || null;
}

function setAudio(id, src) {
  const audio = $(id);
  audio.pause();
  audio.currentTime = 0;
  audio.src = src;
  audio.load();
}

function updateProgress() {
  const total = state.questions.length;
  const answered = state.submitted.size;
  const current = state.current + 1;
  $('progressText').textContent = `${answered} / ${total} 已保存`;
  $('progressBar').style.width = `${Math.round(answered / total * 100)}%`;
  $('sampleCounter').textContent = `${current} / ${total}`;
  $('questionKicker').textContent = `第 ${current} 题`;
  $('prevButton').disabled = state.current === 0 || state.saving;
  $('nextButton').disabled = state.saving;
  $('nextButton').textContent = current === total ? '保存本题并完成 ✓' : '保存本题并下一题 →';
}

function renderQuestion() {
  const question = state.questions[state.current];
  setAudio('referenceAudio', question.reference);
  setAudio('audioA', question.options.A.audio);
  setAudio('audioB', question.options.B.audio);
  const selected = state.answers[question.question_number]?.selected;
  document.querySelectorAll('input[name="choice"]').forEach((input) => {
    input.checked = selected === input.value;
  });
  document.querySelectorAll('.candidate-card').forEach((card) => card.classList.remove('selected'));
  if (selected === 'A') $('optionACard').classList.add('selected');
  if (selected === 'B') $('optionBCard').classList.add('selected');
  updateProgress();
}

function captureChoice() {
  const checked = document.querySelector('input[name="choice"]:checked');
  if (!checked) return;
  const question = state.questions[state.current];
  const option = question.options[checked.value];
  state.answers[question.question_number] = {
    selected: checked.value,
    selected_method: option?.method || null,
    saved_at: new Date().toISOString(),
  };
  persistState();
}

function showError(message) {
  $('errorMessage').textContent = message;
  $('errorMessage').hidden = false;
}

function exportPayload() {
  return {
    format: 'sure-tagger-survey-v2/v4',
    session_id: state.sessionId,
    created_at: state.createdAt,
    completed_at: state.completedAt || null,
    answers: state.questions.map((question) => ({
      question_number: question.question_number,
      position: question.position,
      sample_id: question.sample_id,
      selected: state.answers[question.question_number]?.selected || null,
      selected_method: state.answers[question.question_number]?.selected_method || null,
      submitted: state.submitted.has(question.question_number),
    })),
  };
}

function downloadExport() {
  const payload = JSON.stringify(exportPayload(), null, 2);
  const blob = new Blob([payload], {type: 'application/json'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `sure-tagger-survey-${state.sessionId}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
  ['exportStatus', 'exportProgressStatus'].forEach((id) => {
    const status = $(id);
    if (status) status.textContent = '结果文件已生成，请发送给问卷发起人。';
  });
}

async function copyExport() {
  const payload = JSON.stringify(exportPayload(), null, 2);
  try {
    await navigator.clipboard.writeText(payload);
    ['exportStatus', 'exportProgressStatus'].forEach((id) => {
      const status = $(id);
      if (status) status.textContent = '结果 JSON 已复制。';
    });
  } catch (error) {
    ['exportStatus', 'exportProgressStatus'].forEach((id) => {
      const status = $(id);
      if (status) status.textContent = '浏览器不允许自动复制，请使用“下载结果 JSON”。';
    });
  }
}

function showComplete() {
  $('survey').hidden = true;
  $('complete').hidden = false;
  $('completeText').textContent = `已保存 ${state.submitted.size} 个样本的听感选择。结果只保存在当前浏览器中。`;
}

function saveCurrentAnswer() {
  captureChoice();
  const question = state.questions[state.current];
  if (!state.answers[question.question_number]?.selected) {
    showError('请先选择本题答案，再保存并进入下一题。');
    return;
  }
  state.saving = true;
  $('errorMessage').hidden = true;
  state.submitted.add(question.question_number);
  const isComplete = state.submitted.size === state.questions.length;
  if (isComplete) state.completedAt = new Date().toISOString();
  persistState();
  state.saving = false;
  if (isComplete) {
    showComplete();
    return;
  }
  state.current = Math.min(state.current + 1, state.questions.length - 1);
  renderQuestion();
}

function startSurvey() {
  try {
    restoreOrCreateSession();
    $('loading').hidden = true;
    if (state.completedAt) showComplete();
    else {
      $('survey').hidden = false;
      renderQuestion();
    }
  } catch (error) {
    $('loading').textContent = `无法读取本地记录：${error.message}`;
    $('loading').classList.add('error-state');
  }
}

document.addEventListener('change', (event) => {
  if (event.target.name !== 'choice') return;
  captureChoice();
  $('optionACard').classList.toggle('selected', event.target.value === 'A' && event.target.checked);
  $('optionBCard').classList.toggle('selected', event.target.value === 'B' && event.target.checked);
});

$('prevButton').addEventListener('click', () => {
  captureChoice();
  if (state.current > 0) {
    state.current -= 1;
    renderQuestion();
  }
});
$('nextButton').addEventListener('click', saveCurrentAnswer);
$('exportProgressButton').addEventListener('click', downloadExport);
$('exportButton').addEventListener('click', downloadExport);
$('copyButton').addEventListener('click', copyExport);
$('newSurveyButton').addEventListener('click', () => {
  newSession();
  $('complete').hidden = true;
  $('survey').hidden = false;
  renderQuestion();
});

startSurvey();
