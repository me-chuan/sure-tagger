const $ = (id) => document.getElementById(id);

function pct(value) { return `${Number(value || 0).toFixed(1)}%`; }

async function loadStats() {
  try {
    const response = await fetch('/api/stats', {cache: 'no-store'});
    const stats = await response.json();
    if (!response.ok) throw new Error(stats.error || '统计读取失败');
    $('statsLoading').hidden = true;
    $('statsContent').hidden = false;
    $('completedCount').textContent = stats.completed;
    $('responseCount').textContent = stats.total_responses;
    $('sureRate').textContent = pct(stats.rates.sure_tagger);
    $('captionerRate').textContent = pct(stats.rates.captioner);
    $('sampleCount').textContent = `${stats.per_sample.length} 个样本`;
    const list = $('sampleResults');
    if (!stats.per_sample.length) {
      list.innerHTML = '<div class="empty-result">还没有提交记录。</div>';
      return;
    }
    list.innerHTML = stats.per_sample.map((row) => {
      const total = row.sure_tagger + row.captioner + row.unsure;
      const sureWidth = total ? row.sure_tagger / total * 100 : 0;
      const capWidth = total ? row.captioner / total * 100 : 0;
      return `<article class="result-row">
        <div class="result-meta"><span>样本 ${String(row.position).padStart(2, '0')}</span><strong>${total} 次回答</strong></div>
        <div class="result-bar"><span class="bar-sure" style="width:${sureWidth}%"></span><span class="bar-captioner" style="width:${capWidth}%"></span></div>
        <div class="result-counts"><span>sure tagger ${row.sure_tagger}</span><span>captioner ${row.captioner}</span><span>无法判断 ${row.unsure}</span></div>
      </article>`;
    }).join('');
  } catch (error) {
    $('statsLoading').hidden = true;
    $('statsError').textContent = error.message;
    $('statsError').hidden = false;
  }
}

loadStats();
