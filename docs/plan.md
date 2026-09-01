名称（sure-tagger，建议命名）	和公司对齐的新名称	所用或备选模型	现状（2026-08-23 核对代码）
basic_acoustic.duration_sec	attribute.duration	ffprobe / audio_probe 确定性脚本	✅ 已实现（audio_probe stage）
basic_acoustic.sample_rate_hz	attribute.sample_rate	ffprobe / audio_probe	✅ 已实现
basic_acoustic.channels	attribute.channels	ffprobe / audio_probe	✅ 已实现
basic_acoustic.silence_ratio	annotation[].vad.silence_ratio	FireRedVAD	✅ 已实现；优先 native_metadata 确定性生成，缺失时 FireRedVAD 兜底
basic_acoustic.silence_segments	annotation[].vad.silence_segments	FireRedVAD	✅ 已实现（同上）
音频质量		
audio_quality.snr_db	annotation[].audio_quality.snr	Brouhaha	✅ 已实现（brouhaha stage → audio_quality.snr_db）
audio_quality.dnsmos_sig	annotation[].audio_quality.dnsmos_sig	DNSMOS	✅ 已实现
audio_quality.dnsmos_bak	annotation[].audio_quality.dnsmos_bak	DNSMOS	✅ 已实现
audio_quality.dnsmos_ovrl	annotation[].audio_quality.dnsmos	DNSMOS	✅ 已实现
audio_quality.dnsmos_p808	annotation[].audio_quality.dnsmos_p808	DNSMOS P.808	✅ 已实现（personalized 模型，--dnsmos-personalized）
空间声学信息		
room_acoustic.far_field	annotation[].room_acoustic.far_field	暂无可靠直接模型；Rec-RIR + Brouhaha 规则融合 / Qwen3-Omni 辅助	❌ 未实现。字段仅占位恒为 null，无 stage 产出；Qwen3-8B 与 vLLM runtime 已备好但未接线
room_acoustic.rt60_sec	annotation[].room_acoustic.rt60	Rec-RIR	✅ 已实现（recrir stage → room_acoustic.rt60_sec）
room_acoustic.c50_db	annotation[].room_acoustic.c50	Rec-RIR；Brouhaha C50 可交叉验证	⚠️ Rec-RIR 产出 room_acoustic.c50_db；Brouhaha C50 已降级为内部 evidence（internal.brouhaha_c50_db），两者自动交叉验证未实现
声学环境		
sound_field_scene.speech_music_events（三个）	annotation[].task_extension.sound_event	FireRedVAD-AED	⚠️ AED 已实现（speech_music_events/music_present；2026-08-25 起 singing/music 需事件占比 ≥ --firered-aed-min-singing-ratio / --firered-aed-min-music-ratio 默认 0.10 才公开，caption_pairs_3000 校准消除语音帧误报）；DASS 辅助验证未实现
sound_field_scene.music_present是否有背景音乐	annotation[].others.music_state	FireRedVAD-AED；DASS 可辅助验证	⚠️ 同上（music 占比门控 2026-08-25）
sound_field_scene.external_noise_type背景噪音	annotation[].sweeper_scene.external_noise_info.type	DASS-Small 50.1（主） / CED-Small（备） / PANNs（baseline）	✅ 已实现（2026-08-23，dass stage）：复用 sure-harness 已部署的 DASS medium AudioSet-2M 48.9（saurabhati/DASS_medium_AudioSet_48.9），checkpoint 复制到 models/DASS，venv 复用 harness 的 .venv。2026-08-23 起 DASS 为默认链路背景噪音主模型（panns 于 2026-08-25 废弃删除，PANNs 工具模块保留仅作交叉验证 evidence）；默认排除主语音、Silence、声学场景、混响、回声，--no-exclusion 关闭全部排除以便观察原始类别分布。2026-08-24 起同时产出 sound_field_scene.noise_composition（全量 527 类按 docs/DASS.md 归组，每类 top-3 ≥0.3，音乐类别以 FireRed AED music_present 门控；人类/未归类与各类别分数只进内部 evidence category_events，⑦ 类别留作 far_field/混响补充证据）；同日 external_noise_type 默认阈值 0.5→0.25（phase2 校准：真实噪声类分数偏软 0.1–0.45，干净语音 <0.15），并把 external_noise_type 改为输出 DASS.md 类别键（未被排除且 ≥0.25 的标签所归类别，按类内最高分降序，人类/未归类永不公开），具体标签由 noise_composition 展开。CED 未接入。注：计划写的是 DASS-Small 50.1，实际部署的是 medium 48.9，同为 DASS 系列
sound_field_scene.acoustic_scene 声学环境	annotation[].sweeper_scene.acoustic_scene 	DCASE ASC：WestAI DCASE24（主） / CNN14 DCASE-2020（备）	❌ 未实现，无 stage、无输出字段
多说话人		
speaker.multi_speaker	annotation[].speaker.multi_speaker	pyannote Community-1（主） / MOSS-Diarize / Sortformer	⚠️ 三模型均已接入 speaker_v2；但 quality-shadow profile 中 speaker_count/multi_speaker 主源为 Sortformer（pyannote 被排除），与计划"pyannote 为主"不一致，需确认
speaker.speaker_count	annotation[].speaker.speaker_count	pyannote Community-1（主） / MOSS-Diarize / Sortformer	⚠️ 同上
speaker.speaker_change	annotation[].speaker.speaker_change	pyannote Community-1 / MOSS-Diarize / Sortformer	⚠️ 三模型已接入，claim 路由见 speaker_v2/profiles.py
speaker.speaker_change_count	annotation[].speaker.speaker_change_count	pyannote Community-1 / MOSS-Diarize / Sortformer	⚠️ 同上
speaker.speaker_overlap	annotation[].speaker.speaker_overlap	pyannote Community-1  / Sortformer/ MOSS-Diarize	✅ 已实现（overlap 主源为 pyannote，与计划一致）
speaker.overlap_ratio	annotation[].speaker.overlap_ratio	pyannote Community-1  / Sortformer / MOSS-Diarize	✅ 已实现（同上）
speaker.profiles	（公司 schema 暂无对应；对齐 captioner speakerProfile 的 speed/pitch/speaker_volume）	确定性统计适配器（复用 decision timeline / MOSS 文本 / VAD，无新模型）	✅ 已实现（2026-08-26）：speaker_v2.speaker_profile.v0.1，语速（zh_char_per_sec / word_per_min）、相对音高档位、片段内相对音量；不可靠值为 null，不推断年龄/性别/情绪/口音（属 Phase 3 属性模型闸门）
speaker.asr_transcript	annotation[].transcription.text	MOSS + FireRedASR2-AED 双路 ASR（FireRed LID 明确 en 且 ASCII-English 才选 MOSS，其它语言选 FireRed）	✅ 已实现（2026-08-31）：两路并行推理；只有 FireRed LID 明确 en 且文本通过 ASCII-English 检查时路由到 MOSS，中文/混合/非拉丁/未知路由到 FireRed；一路失败显式回退；不含时间戳/speaker ID，不读取输入 transcript
语言		
language_content.language	annotation[].transcription.language	FireRedLID	✅ 已实现（2026-08-23）：firered_lid stage，模型 models/FireRedASR2S/pretrained_models/FireRedLID，runtime .runtime/fireredlid_py311，支持 100+ 语言与 zh-<region> 方言码；原 Unicode script 启发式保留在 deterministic.py 但不再注册为 language 来源
language_content.word_count	annotation[].transcription.word_count	确定性脚本	✅ 已实现
language_content.punctuation	annotation[].transcription.punctuation	确定性脚本	✅ 已实现
language_content.repetition	annotation[].transcription.repeat_times	确定性脚本	✅ 已实现
language_content.filler	annotation[].transcription.filler_count	确定性脚本	✅ 已实现

## 当前链路

入口 `scripts/run_tagger.py` → `tagger/pipelines/tagging.py`，当前 stage：

```
language_deterministic / audio_probe / silence / speaker /
brouhaha / dnsmos / firered_aed / dass / recrir / firered_lid
```

`panns` stage 与 `sound_field_scene.sound` 字段已于 2026-08-25 废弃删除
（DASS 为背景噪音主模型，具体标签由 `noise_composition` 展开）；PANNs
工具模块保留，仅作后续交叉验证 evidence 用，不注册、不进入公开输出。

输出为内部 schema（`basic_acoustic.*`、`audio_quality.*`、`room_acoustic.*`、
`sound_field_scene.*`、`speaker.*`、`language_content.*`）的 tags-only JSONL，
详细说明见 `docs/pipeline-architecture.md`。命名已于 2026-08-23 按本表第一列
统一。

## 结构性 gap

1. **公司 schema 导出层缺失（最大 gap）**：pipeline 输出的是内部 schema，目前
   没有任何 stage 或脚本把内部 tags 转成公司格式（`attribute.*` +
   `annotation[].*`）。根目录 `schema.json` 和 `company-label-alignment.md`
   已定义目标格式与映射规则，但无对应代码。
2. `bridge/sure-tagger` 是包含旧 topic 实验的历史语言层原型，输出的是
   sure_tagger 自有 `{value, confidence, ...}` 格式，也不是当前公开 schema。
   当前 sure-tagger 不产出 topic；开放短语 topic 由下游语言模型生成。

## 下一步清单

1. 未实现标签：
   - `far_field`（暂时不实现）
   - `acoustic_scene`（暂时不实现）
2. 确认 speaker claim 路由与计划的偏差：按计划把主源改回 pyannote
   Community-1，还是更新计划（quality-shadow 已按实测设定为 Sortformer 主）。
3. 实现内部 schema → 公司 `annotation[]` 格式的导出/桥接层（可复用
   `company-label-alignment.md` 的映射规则）。
4. 可选增强：Brouhaha C50 与 Rec-RIR C50 的自动交叉验证；DASS 对 AED
   music_present/speech_music_events 的验证。
