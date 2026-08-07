const data = window.DEMO_DATA;

const state = {
  filter: "all",
  activeId: data.samples[0]?.sampleId,
  tagGroup: "overview",
};

const tagGroups = [
  ["overview", "Overview"],
  ["basic_acoustic", "Basic acoustic"],
  ["sound_field_scene", "Sound field"],
  ["language_content", "Language"],
  ["speaker", "Speaker"],
];

const datasetColors = new Map();
const palette = ["#16796f", "#2d62a3", "#c67828", "#6a5aa8", "#b14b4b", "#557a2f", "#8b5b2e", "#52616b"];
const waveformCache = new Map();
let audioContext;
let waveformState = null;

const els = {
  metricGrid: document.querySelector("#metricGrid"),
  filterRow: document.querySelector("#filterRow"),
  sampleList: document.querySelector("#sampleList"),
  visibleCount: document.querySelector("#visibleCount"),
  activeDataset: document.querySelector("#activeDataset"),
  activeTitle: document.querySelector("#activeTitle"),
  activeNote: document.querySelector("#activeNote"),
  activeSampleId: document.querySelector("#activeSampleId"),
  audioPlayer: document.querySelector("#audioPlayer"),
  waveform: document.querySelector("#waveform"),
  transcriptText: document.querySelector("#transcriptText"),
  tagToolbar: document.querySelector("#tagToolbar"),
  tagGrid: document.querySelector("#tagGrid"),
  rawJson: document.querySelector("#rawJson"),
  datasetBars: document.querySelector("#datasetBars"),
  coverageBars: document.querySelector("#coverageBars"),
};

function init() {
  data.summary.datasets.forEach((dataset, index) => {
    datasetColors.set(dataset.name, palette[index % palette.length]);
  });
  renderMetrics();
  renderFilters();
  renderSampleList();
  renderTagToolbar();
  renderBars();
  renderActiveSample();
  setupWaveformEvents();
}

function getActiveSample() {
  return data.samples.find((sample) => sample.sampleId === state.activeId) || data.samples[0];
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "未生成";
  if (typeof value !== "number") return String(value);
  if (Math.abs(value) >= 100) return value.toFixed(0);
  return value.toFixed(digits).replace(/\\.00$/, "");
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "未生成";
  return `${Math.round(value * 100)}%`;
}

function formatDuration(value) {
  if (value === null || value === undefined) return "未知时长";
  return `${formatNumber(value, 2)}s`;
}

function formatUnit(value, unit, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "未生成";
  return `${formatNumber(value, digits)} ${unit}`;
}

function compactDataset(name) {
  return name.replace("TUT Urban Acoustic Scenes 2018", "TUT 2018").replace("WHAM! noise", "WHAM");
}

function hasTranscript(sample) {
  return Boolean(sample.transcript && sample.transcript.trim());
}

function renderMetrics() {
  const smoke = data.summary.smoke || {};
  const metrics = [
    ["Phase2 samples", data.summary.sampleCount, `${data.summary.datasetCount} 个数据集，每个 5 条样本`],
    ["Demo audio", data.summary.selectedCount, "精选代表性音频，可播放和查看波形"],
    ["AMI smoke", `${smoke.sampleCount || 0}/3`, "topic + metadata VAD + speaker 已跑通"],
    ["Topic labels", `${smoke.topicCount || 0}/3`, "OpenAI Responses 输出层级 topic"],
  ];

  els.metricGrid.innerHTML = metrics
    .map(
      ([label, value, caption]) => `
        <article class="metric-card">
          <p class="metric-label">${label}</p>
          <div class="metric-value">${value}</div>
          <p class="metric-caption">${caption}</p>
        </article>
      `,
    )
    .join("");
}

function renderFilters() {
  const filters = [["all", "全部"], ...data.summary.datasets.map((dataset) => [dataset.name, compactDataset(dataset.name)])];
  els.filterRow.innerHTML = filters
    .map(
      ([value, label]) => `
        <button type="button" data-filter="${escapeAttr(value)}" class="${state.filter === value ? "is-active" : ""}">
          ${label}
        </button>
      `,
    )
    .join("");

  els.filterRow.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      const filtered = getFilteredSamples();
      if (!filtered.some((sample) => sample.sampleId === state.activeId)) {
        state.activeId = filtered[0]?.sampleId || data.samples[0]?.sampleId;
      }
      renderFilters();
      renderSampleList();
      renderActiveSample();
    });
  });
}

function getFilteredSamples() {
  if (state.filter === "all") return data.samples;
  return data.samples.filter((sample) => sample.dataset === state.filter);
}

function renderSampleList() {
  const samples = getFilteredSamples();
  els.visibleCount.textContent = `${samples.length} 条`;
  els.sampleList.innerHTML = samples
    .map((sample) => {
      const active = sample.sampleId === state.activeId ? "is-active" : "";
      const transcriptState = hasTranscript(sample) ? "transcript" : "no transcript";
      const sound = sample.tags.sound_field_scene?.sound || [];
      const soundState = sound.length ? `sound: ${sound.slice(0, 2).join(", ")}` : "sound: none";
      const topic = sample.tags.language_content?.topic;
      const speaker = speakerHasValues(sample.tags.speaker) ? "speaker: ready" : "speaker: none";
      const color = datasetColors.get(sample.dataset) || "#16796f";
      return `
        <button type="button" class="sample-button ${active}" data-sample="${escapeAttr(sample.sampleId)}">
          <div class="sample-title">
            <span><span class="dataset-dot" style="background:${color}"></span> ${sample.title}</span>
          </div>
          <div class="sample-meta">
            <span>${compactDataset(sample.dataset)}</span>
            <span>${formatDuration(sample.durationSec)}</span>
            <span>${transcriptState}</span>
            <span>${topic ? `topic: ${topic}` : soundState}</span>
            <span>${speaker}</span>
          </div>
        </button>
      `;
    })
    .join("");

  els.sampleList.querySelectorAll(".sample-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeId = button.dataset.sample;
      renderSampleList();
      renderActiveSample();
    });
  });
}

function renderTagToolbar() {
  els.tagToolbar.innerHTML = tagGroups
    .map(
      ([value, label]) => `
        <button type="button" role="tab" data-group="${value}" class="${state.tagGroup === value ? "is-active" : ""}">
          ${label}
        </button>
      `,
    )
    .join("");
  els.tagToolbar.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.tagGroup = button.dataset.group;
      renderTagToolbar();
      renderTags(getActiveSample());
    });
  });
}

function renderActiveSample() {
  const sample = getActiveSample();
  if (!sample) return;

  els.activeDataset.textContent = sample.dataset;
  els.activeTitle.textContent = sample.title;
  els.activeNote.textContent = sample.note;
  els.activeSampleId.textContent = sample.sampleId;
  els.audioPlayer.src = sample.audio;
  els.audioPlayer.load();

  if (hasTranscript(sample)) {
    els.transcriptText.classList.remove("is-empty");
    els.transcriptText.textContent = sample.transcript;
  } else {
    els.transcriptText.classList.add("is-empty");
    els.transcriptText.textContent = "该样本没有 transcript，语言层只保留空结果，主要展示声学与声场标签。";
  }

  els.rawJson.textContent = JSON.stringify(sample.tags, null, 2);
  renderTags(sample);
  loadWaveform(sample);
}

function renderTags(sample) {
  const cards = getCardsForGroup(sample, state.tagGroup);
  els.tagGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="tag-card ${card.isNull ? "is-null" : ""}">
          <p class="tag-label">${card.label}</p>
          <div class="tag-value">${card.value}</div>
          <p class="tag-subtext">${card.subtext || ""}</p>
        </article>
      `,
    )
    .join("");
}

function getCardsForGroup(sample, group) {
  const tags = sample.tags;
  const basic = tags.basic_acoustic || {};
  const scene = tags.sound_field_scene || {};
  const lang = tags.language_content || {};
  const speaker = tags.speaker || {};

  if (group === "overview") {
    const speakerReady = speakerHasValues(speaker);
    return [
      card("Duration", formatDuration(basic.duration_sec), `${formatNumber(basic.sample_rate_hz, 0)} Hz / ${basic.channels || "?"} channel`),
      card("SNR", formatUnit(basic.snr_db, "dB", 2), "更高通常表示背景噪声更少", basic.snr_db == null),
      card("Silence ratio", formatPercent(basic.silence_ratio), `${(basic.silence_segments || []).length} silence segment(s)`),
      card("DNSMOS OVRL", formatNumber(basic.dnsmos_ovrl, 2), "模型估计的整体语音质量", basic.dnsmos_ovrl == null),
      card("Language", lang.language || "未生成", hasTranscript(sample) ? `${lang.word_count ?? 0} words/chars` : "缺少 transcript", !lang.language),
      card("Topic", lang.topic || "未生成", "OpenAI Responses taxonomy label", !lang.topic),
      card("RT60", formatUnit(scene.rt60, "s", 3), "Rec-RIR reverberation estimate", scene.rt60 == null),
      card("Speaker", speakerStatus(speaker), speakerReady ? "metadata-first diarization flags" : "未生成", !speakerReady),
    ];
  }

  if (group === "basic_acoustic") {
    return [
      card("duration_sec", formatNumber(basic.duration_sec, 3), "音频时长"),
      card("sample_rate_hz", formatNumber(basic.sample_rate_hz, 0), "采样率"),
      card("channels", basic.channels ?? "未生成", "声道数"),
      card("snr_db", formatUnit(basic.snr_db, "dB", 3), "估计信噪比", basic.snr_db == null),
      card("c50", formatNumber(basic.c50, 3), "清晰度指标"),
      card("silence_ratio", formatPercent(basic.silence_ratio), "metadata 优先；缺失时退回 VAD 模型"),
      card("silence_segments", listSegments(basic.silence_segments), "静音片段，波形中以琥珀色显示", !basic.silence_segments?.length),
      card("dnsmos_sig", formatNumber(basic.dnsmos_sig, 3), "speech quality"),
      card("dnsmos_bak", formatNumber(basic.dnsmos_bak, 3), "background quality", basic.dnsmos_bak == null),
      card("dnsmos_ovrl", formatNumber(basic.dnsmos_ovrl, 3), "overall quality", basic.dnsmos_ovrl == null),
      card("dnsmos_p808", formatNumber(basic.dnsmos_p808, 3), "P.808 MOS estimate"),
    ];
  }

  if (group === "sound_field_scene") {
    return [
      card("audio_events", listValue(scene.audio_events), "PANNs top events", !scene.audio_events?.length),
      card("sound", listValue(scene.sound), "detected non-speech sound", !scene.sound?.length),
      card("music", scene.music === true ? "true" : "false", "music flag"),
      card("rt60", formatUnit(scene.rt60, "s", 4), "reverberation time", scene.rt60 == null),
      card("c50", formatNumber(scene.c50, 4), "scene clarity"),
      card("far_field", scene.far_field ?? "未生成", "预留字段", scene.far_field == null),
    ];
  }

  if (group === "language_content") {
    return [
      card("language", lang.language || "未生成", hasTranscript(sample) ? "deterministic transcript tag" : "缺少 transcript", !lang.language),
      card("word_count", lang.word_count ?? "未生成", "英文按 token，中文按字符/分词结果"),
      card("filler", lang.filler ?? "未生成", "um/uh/okay 等填充表达"),
      card("punctuation", punctuationValue(lang.punctuation), "标点统计", !lang.punctuation),
      card("repetition", repetitionValue(lang.repetition), "重复词统计", !lang.repetition),
      card("topic", lang.topic ?? "未生成", "OpenAI Responses 层级 topic", !lang.topic),
    ];
  }

  const speakerReady = speakerHasValues(speaker);
  return [
    card("multi_speaker", speaker.multi_speaker ?? "未生成", "metadata 优先；缺失时退回 diarization", !speakerReady),
    card("speaker_change", speaker.speaker_change ?? "未生成", "当前 utterance 内是否存在说话人切换", !speakerReady),
    card("speaker_overlap", speaker.speaker_overlap ?? "未生成", "当前 utterance 内是否存在重叠说话", !speakerReady),
  ];
}

function card(label, value, subtext, isNull = false) {
  return { label, value: String(value), subtext, isNull };
}

function listValue(value) {
  if (!Array.isArray(value) || value.length === 0) return "[]";
  return value.join(", ");
}

function listSegments(segments) {
  if (!Array.isArray(segments) || segments.length === 0) return "[]";
  return segments.map((segment) => `${formatNumber(segment.start_sec, 2)}-${formatNumber(segment.end_sec, 2)}s`).join(", ");
}

function punctuationValue(value) {
  if (!value) return "未生成";
  return `${value.punctuation_count ?? 0} punctuation / terminal ${value.has_terminal_punctuation ? "yes" : "no"}`;
}

function repetitionValue(value) {
  if (!value) return "未生成";
  return `${value.repetition_count ?? 0} repetition / ${value.has_repetition ? "detected" : "none"}`;
}

function speakerStatus(value) {
  if (!value) return "未生成";
  return speakerHasValues(value) ? "已生成" : "未生成";
}

function speakerHasValues(value) {
  if (!value) return false;
  return Object.values(value).some((item) => item !== null && item !== undefined);
}

function renderBars() {
  const maxDataset = Math.max(...data.summary.datasets.map((dataset) => dataset.count));
  els.datasetBars.innerHTML = data.summary.datasets
    .map((dataset) => renderBar(dataset.name, dataset.count, maxDataset, `${dataset.count} samples`))
    .join("");

  const groupLabels = {
    basic_acoustic: "Basic acoustic",
    sound_field_scene: "Sound field scene",
    language_content: "Language content",
    speaker: "Speaker diarization",
  };
  els.coverageBars.innerHTML = Object.entries(data.summary.coverage)
    .map(([group, count]) => renderBar(groupLabels[group] || group, count, data.summary.sampleCount, `${count}/${data.summary.sampleCount}`))
    .join("");
}

function renderBar(label, value, max, text) {
  const width = max > 0 ? Math.max(2, Math.round((value / max) * 100)) : 0;
  return `
    <div class="bar-row">
      <div class="bar-label">${label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
      <div class="bar-value">${text}</div>
    </div>
  `;
}

function setupWaveformEvents() {
  window.addEventListener("resize", () => {
    if (waveformState) drawWaveform(waveformState);
  });

  els.audioPlayer.addEventListener("timeupdate", () => {
    if (waveformState) drawWaveform(waveformState);
  });

  els.waveform.addEventListener("click", (event) => {
    if (!waveformState || !els.audioPlayer.duration) return;
    const rect = els.waveform.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
    els.audioPlayer.currentTime = ratio * els.audioPlayer.duration;
    drawWaveform(waveformState);
  });
}

async function loadWaveform(sample) {
  waveformState = null;
  drawLoadingWaveform("正在解码音频波形...");

  try {
    if (!waveformCache.has(sample.sampleId)) {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      const response = await fetch(sample.audio);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      waveformCache.set(sample.sampleId, buildWaveformPeaks(audioBuffer));
    }
    waveformState = {
      peaks: waveformCache.get(sample.sampleId),
      duration: sample.tags.basic_acoustic?.duration_sec || els.audioPlayer.duration || sample.durationSec,
      silenceSegments: sample.tags.basic_acoustic?.silence_segments || [],
    };
    drawWaveform(waveformState);
  } catch (error) {
    drawLoadingWaveform("无法读取波形；请通过本地 HTTP 服务访问 demo。");
  }
}

function buildWaveformPeaks(audioBuffer) {
  const channel = audioBuffer.getChannelData(0);
  const bucketCount = 900;
  const bucketSize = Math.max(1, Math.floor(channel.length / bucketCount));
  const peaks = [];
  for (let i = 0; i < bucketCount; i += 1) {
    let min = 1;
    let max = -1;
    const start = i * bucketSize;
    const end = Math.min(channel.length, start + bucketSize);
    for (let j = start; j < end; j += 1) {
      const value = channel[j];
      if (value < min) min = value;
      if (value > max) max = value;
    }
    peaks.push(Math.max(Math.abs(min), Math.abs(max)));
  }
  return peaks;
}

function resizeCanvas() {
  const canvas = els.waveform;
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(320, Math.floor(rect.width * dpr));
  canvas.height = Math.floor(160 * dpr);
  return { canvas, width: canvas.width, height: canvas.height, dpr };
}

function drawLoadingWaveform(message) {
  const { canvas, width, height, dpr } = resizeCanvas();
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#101716";
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = "#dfe8e4";
  ctx.font = `${14 * dpr}px system-ui, sans-serif`;
  ctx.fillText(message, 18 * dpr, 84 * dpr);
}

function drawWaveform(current) {
  const { canvas, width, height, dpr } = resizeCanvas();
  const ctx = canvas.getContext("2d");
  const centerY = height / 2;
  const barWidth = Math.max(1, Math.floor(width / current.peaks.length));

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#101716";
  ctx.fillRect(0, 0, width, height);

  if (current.duration) {
    ctx.fillStyle = "rgba(198, 120, 40, 0.34)";
    for (const segment of current.silenceSegments) {
      const start = (segment.start_sec / current.duration) * width;
      const end = (segment.end_sec / current.duration) * width;
      ctx.fillRect(start, 0, Math.max(1, end - start), height);
    }
  }

  ctx.strokeStyle = "rgba(255, 255, 255, 0.16)";
  ctx.beginPath();
  ctx.moveTo(0, centerY);
  ctx.lineTo(width, centerY);
  ctx.stroke();

  ctx.fillStyle = "#8fd0c6";
  current.peaks.forEach((peak, index) => {
    const x = index * barWidth;
    const barHeight = Math.max(2 * dpr, peak * height * 0.78);
    ctx.fillRect(x, centerY - barHeight / 2, Math.max(1, barWidth - 1), barHeight);
  });

  const duration = els.audioPlayer.duration || current.duration;
  if (duration && els.audioPlayer.currentTime) {
    const x = (els.audioPlayer.currentTime / duration) * width;
    ctx.fillStyle = "#f2d39a";
    ctx.fillRect(x, 0, 2 * dpr, height);
  }

  canvas.title = "点击波形跳转播放";
}

function escapeAttr(value) {
  return String(value).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

init();
