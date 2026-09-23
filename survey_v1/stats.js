const SESSIONS_KEY = 'sure-tagger-survey-sessions-v1';
const $ = (id) => document.getElementById(id);

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

function pct(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function buildStats(sessions) {
  const perSample = {};
  const totals = {sure_tagger: 0, captioner: 0, unsure: 0};
  let totalResponses = 0;
  sessions.forEach((session) => {
    (session.answers ? Object.entries(session.answers) : []).forEach(([questionNumber, answer]) => {
      if (!answer || !session.submitted?.includes(Number(questionNumber))) return;
      const question = (session.questions || []).find((row) => row.question_number === Number(questionNumber));
      if (!question) return;
      const sample = perSample[question.sample_id] ||= {
        position: question.position,
        sample_id: question.sample_id,
        sure_tagger: 0,
        captioner: 0,
        unsure: 0,
      };
      const key = answer.selected === 'unsure' ? 'unsure' : answer.selected_method;
      if (!Object.hasOwn(sample, key)) return;
      sample[key] += 1;
      totals[key] += 1;
      totalResponses += 1;
    });
  });
  const rows = Object.values(perSample).sort((a, b) => a.position - b.position);
  const rated = rows.filter((row) => row.sure_tagger + row.captioner > 0);
  const rates = rated.length ? {
    sure_tagger: rated.reduce((sum, row) => sum + row.sure_tagger / (row.sure_tagger + row.captioner) * 100, 0) / rated.length,
    captioner: rated.reduce((sum, row) => sum + row.captioner / (row.sure_tagger + row.captioner) * 100, 0) / rated.length,
  } : {sure_tagger: 0, captioner: 0};
  return {
    completed: sessions.filter((session) => session.completedAt).length,
    totalResponses,
    totals,
    rates,
    rows,
  };
}

function render() {
  const sessions = readSessions();
  const stats = buildStats(sessions);
  $('statsLoading').hidden = true;
  $('statsContent').hidden = false;
  $('completedCount').textContent = stats.completed;
  $('responseCount').textContent = stats.totalResponses;
  $('sureRate').textContent = pct(stats.rates.sure_tagger);
  $('captionerRate').textContent = pct(stats.rates.captioner);
  $('sampleCount').textContent = `${stats.rows.length} 个样本`;
  const list = $('sampleResults');
  if (!stats.rows.length) {
    list.innerHTML = '<div class="empty-result">还没有本地结果。可以导入参与者发来的 JSON。</div>';
    return;
  }
  list.innerHTML = stats.rows.map((row) => {
    const total = row.sure_tagger + row.captioner + row.unsure;
    const sureWidth = total ? row.sure_tagger / total * 100 : 0;
    const capWidth = total ? row.captioner / total * 100 : 0;
    return `<article class="result-row">
      <div class="result-meta"><span>样本 ${String(row.position).padStart(2, '0')}</span><strong>${total} 次回答</strong></div>
      <div class="result-bar"><span class="bar-sure" style="width:${sureWidth}%"></span><span class="bar-captioner" style="width:${capWidth}%"></span></div>
      <div class="result-counts"><span>sure tagger ${row.sure_tagger}</span><span>captioner ${row.captioner}</span><span>无法判断 ${row.unsure}</span></div>
    </article>`;
  }).join('');
}

async function importFiles(files) {
  const imported = [];
  for (const file of files) {
    try {
      const payload = JSON.parse(await file.text());
      if (payload.format !== 'sure-tagger-survey/v1' || !payload.session_id || !Array.isArray(payload.answers)) continue;
      const answers = {};
      const submitted = [];
      payload.answers.forEach((answer) => {
        if (!answer.submitted || !answer.selected) return;
        answers[answer.question_number] = {
          selected: answer.selected,
          selected_method: answer.selected_method || null,
          saved_at: payload.completed_at || payload.created_at || new Date().toISOString(),
        };
        submitted.push(Number(answer.question_number));
      });
      imported.push({
        sessionId: payload.session_id,
        createdAt: payload.created_at || null,
        completedAt: payload.completed_at || null,
        answers,
        submitted,
        questions: payload.answers.map((answer) => ({
          question_number: Number(answer.question_number),
          position: Number(answer.position),
          sample_id: answer.sample_id,
        })),
      });
    } catch (error) {
      // Ignore malformed files and continue importing valid files.
    }
  }
  const sessions = readSessions();
  const ids = new Set(sessions.map((session) => session.sessionId));
  imported.forEach((session) => {
    if (!ids.has(session.sessionId)) sessions.push(session);
  });
  writeSessions(sessions);
  $('importStatus').textContent = imported.length ? `已导入 ${imported.length} 份结果。` : '没有找到可导入的结果文件。';
  render();
}

$('importResults').addEventListener('change', (event) => importFiles([...event.target.files]));
$('clearResultsButton').addEventListener('click', () => {
  if (!window.confirm('确定清空当前浏览器中的全部本地结果吗？')) return;
  localStorage.removeItem(SESSIONS_KEY);
  $('importStatus').textContent = '本地结果已清空。';
  render();
});

render();
