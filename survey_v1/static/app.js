const state = {
  sessionId: null,
  questions: [],
  answers: new Map(),
  submitted: new Set(),
  current: 0,
  saving: false,
};

const $ = (id) => document.getElementById(id);

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
  $('progressText').textContent = `${answered} / ${total} 已提交`;
  $('progressBar').style.width = `${Math.round(answered / total * 100)}%`;
  $('sampleCounter').textContent = `${current} / ${total}`;
  $('questionKicker').textContent = `第 ${current} 题`;
  $('prevButton').disabled = state.current === 0 || state.saving;
  const isLast = state.current === total - 1;
  $('nextButton').disabled = state.saving;
  $('nextButton').textContent = isLast ? '提交本题并完成 ✓' : '提交本题并下一题 →';
}

function renderQuestion() {
  const q = state.questions[state.current];
  setAudio('referenceAudio', q.reference);
  setAudio('audioA', q.options.A.audio);
  setAudio('audioB', q.options.B.audio);
  document.querySelectorAll('input[name="choice"]').forEach((input) => {
    input.checked = state.answers.get(q.question_number) === input.value;
  });
  document.querySelectorAll('.candidate-card').forEach((card) => card.classList.remove('selected'));
  const selected = state.answers.get(q.question_number);
  if (selected === 'A') $('optionACard').classList.add('selected');
  if (selected === 'B') $('optionBCard').classList.add('selected');
  updateProgress();
}

function captureChoice() {
  const checked = document.querySelector('input[name="choice"]:checked');
  if (checked) state.answers.set(state.questions[state.current].question_number, checked.value);
  updateProgress();
}

function showError(message) {
  $('errorMessage').textContent = message;
  $('errorMessage').hidden = false;
}

async function submitCurrentAnswer() {
  captureChoice();
  const question = state.questions[state.current];
  const selected = state.answers.get(question.question_number);
  if (!selected) {
    showError('请先选择本题答案，再提交并进入下一题。');
    return;
  }
  state.saving = true;
  $('errorMessage').hidden = true;
  updateProgress();
  try {
    const response = await fetch('/api/answer', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        session_id: state.sessionId,
        question_number: question.question_number,
        selected,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '提交失败');
    state.submitted.add(question.question_number);
    if (data.complete) {
      $('survey').hidden = true;
      $('complete').hidden = false;
      $('completeText').textContent = `已逐题记录 ${data.answered} 个样本的听感选择。`;
      return;
    }
    state.current += 1;
    renderQuestion();
  } catch (error) {
    showError(error.message);
  } finally {
    state.saving = false;
    if (!$('survey').hidden) updateProgress();
  }
}

async function startSurvey() {
  try {
    const response = await fetch('/api/session', {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '无法创建问卷');
    state.sessionId = data.session_id;
    state.questions = data.questions;
    $('loading').hidden = true;
    $('survey').hidden = false;
    renderQuestion();
  } catch (error) {
    $('loading').textContent = error.message;
    $('loading').classList.add('error-state');
  }
}

document.addEventListener('change', (event) => {
  if (event.target.name === 'choice') {
    captureChoice();
    $('optionACard').classList.toggle('selected', event.target.value === 'A' && event.target.checked);
    $('optionBCard').classList.toggle('selected', event.target.value === 'B' && event.target.checked);
  }
});

$('prevButton').addEventListener('click', () => {
  captureChoice();
  if (state.current > 0) { state.current -= 1; renderQuestion(); }
});

$('nextButton').addEventListener('click', () => {
  submitCurrentAnswer();
});

$('newSurveyButton').addEventListener('click', () => window.location.reload());
startSurvey();
