# Tagging Pipeline 架构说明

本文档说明当前 ASR 数据集二次打标 pipeline 的入口、执行流程、各环节调用的
程序和模型，以及只补充标签时的行为。

## 1. 主程序

推荐入口是：

```bash
PYTHONPATH=. python3 scripts/run_tagger.py \
  --manifest phase2_asr_sample/manifest.jsonl \
  --output outputs/phase2_tags.jsonl \
  --artifact-dir outputs/phase2_artifacts
```

代码入口：

```text
scripts/run_tagger.py
  -> tagger.pipelines.tagging.main()
  -> tagger.pipelines.tagging.run_manifest()
  -> tagger.pipelines.tagging._tag_record_internal()
```

旧入口仍保留为兼容 wrapper：

```text
scripts/run_signal.py
tagger/pipelines/signal.py
```

新代码和文档应使用 `run_tagger.py` 和 `tagger.pipelines.tagging`。

## 2. 整体数据流

输入是 raw-only manifest JSONL。每一行必须包含 `sample.sample_id`、
`sample.audio.path`、`sample.text.transcript` 和 `sample.native_metadata` 等
字段，完整 schema 见 `development.md`。

输出是 tags-only JSONL。默认情况下，输入每个样本对应输出一行；输出只包含
公开 tag 值，不包含 `sample_id`、模型置信度、warning 或内部 evidence。
Speaker metadata、Rec-RIR 等非公开中间结果会写到 `--artifact-dir`。

每条样本的执行顺序：

1. 校验输入 schema。
2. 读取已有 tags，或创建空 tags。
3. 根据 `--only-tags`、`--input-tags`、`--missing-only` 计算本行要运行的 stage。
4. 应用无 transcript guard。
5. 运行语言层 stage。
6. 对需要音频的 stage 解析音频路径并按需运行 `audio_probe`。
7. 运行 VAD、speaker、声学质量、声音事件、背景声和 RIR stage。
8. audit public tag 值。
9. 写出 tags-only JSONL。

## 3. Stage 划分

当前 full pipeline 包含这些 stage：

| Stage | 输出 tag path |
| --- | --- |
| `language_deterministic` | `language_content.word_count`, `punctuation`, `repetition`, `filler` |
| `topic` | `language_content.topic` |
| `audio_probe` | `basic_acoustic.duration_sec`, `sample_rate_hz`, `channels` |
| `silence` | `basic_acoustic.silence_segments`, `silence_ratio` |
| `speaker` | `speaker.speaker_count`, `multi_speaker`, `speaker_change_count`, `speaker_change`, `overlap_ratio`, `speaker_overlap`, `profiles` |
| `brouhaha` | `audio_quality.snr_db`（C50 仅作为内部 evidence `internal.brouhaha_c50_db`） |
| `dnsmos` | `audio_quality.dnsmos_sig`, `dnsmos_bak`, `dnsmos_ovrl`, `dnsmos_p808` |
| `firered_aed` | `sound_field_scene.speech_music_events`, `music_present` |
| `dass` | `sound_field_scene.external_noise_type`（docs/DASS.md 类别键）, `noise_composition`（各类别具体标签） |
| `recrir` | `room_acoustic.rt60_sec`, `room_acoustic.c50_db` |
| `firered_lid` | `language_content.language` |

`panns`（`sound_field_scene.sound`）已于 2026-08-25 废弃删除——DASS 是
背景噪音分类的主模型，具体标签由 `sound_field_scene.noise_composition`
展开。`panns_background_detector` 模块保留可导入，仅作后续交叉验证
evidence 用，不注册、不进入公开输出。

`--only-tags` 可以接收 stage 名、tag group 名或具体 tag path。例如：

```bash
--only-tags speaker
--only-tags language_content.topic,basic_acoustic.silence_ratio
--only-tags recrir
```

如果选中的 stage 需要音频 duration/channels，而已有 tags 中没有这些值，
pipeline 会自动补跑 `audio_probe`。

## 4. 无 transcript guard

如果 `sample.text.transcript` 为空，pipeline 会先尝试使用 speaker-v2 的联合
ASR（MOSS）生成替代文本。生成成功时，language-content 的全部标签使用这段
ASR 文本；生成失败时才跳过依赖语言内容的 stage。其它音频和非语言 stages
仍按正常流程运行：

```text
language_deterministic
topic
firered_lid
```

没有可用 ASR 时，对应的 language-content public tags 会被设置为：

```text
language_content.* = null  （仅在 speaker-v2 没有可用 ASR 时）
```

`topic` 仍遵循默认关闭的配置；即使 ASR 可用，未启用 topic 时该字段也保持
`null`。

speaker-v2 ASR 只作为 language-content 的输入，不会把输入 transcript 传入
speaker resolver。`audio_probe`、`silence`、
`speaker`、`brouhaha`、`dnsmos`、`firered_aed`、`dass` 和 `recrir` 仍可运行，
因为它们可以用于纯噪声或无 transcript 音频的基础音频、声学、说话人和声场分析。

补标时这个行为也生效。若某条无 transcript 样本已有旧标签，本次选择
`language_content.*` 时会先运行 speaker-v2 以获取替代文本；只有拿不到 ASR
时才按当前规则重置 language-content 字段。补其它标签时不会因为 transcript
为空而跳过对应音频或非语言 stage。

## 5. 每个环节调用的程序和模型

### 5.1 语言确定性层

程序：

```text
tagger/tools/language_content/deterministic.py
```

模型：无。

输入：非空时使用 `sample.text.transcript`；为空时使用 speaker-v2 的 MOSS
联合 ASR 文本。

输出：

```text
language_content.word_count
language_content.punctuation
language_content.repetition
language_content.filler
```

`language_content.language` 在非空 transcript 时由 FireRed LID 音频模型产出；
空 transcript 时改由上述 ASR 文本的 Unicode script heuristic 产出。

### 5.1b FireRed LID

程序：

```text
tagger/tools/language_content/firered_lid_detector.py
```

模型：

```text
FireRed LID
models/FireRedASR2S/pretrained_models/FireRedLID/{model.pth.tar,cmvn.ark,dict.txt}
models/FireRedASR2S/examples_infer/lid/fireredlid
```

默认 Python 环境：

```text
.runtime/fireredlid_py311/bin/python
```

输出：

```text
language_content.language  （ISO 语言码或 zh-<region> 方言码，如 zh-xinan）
```

### 5.2 Topic

程序：

```text
tagger/tools/language_content/topic.py
```

模型/API：OpenAI-compatible Responses API。

默认关闭，必须显式传入：

```bash
--topic-enable
```

API key/model/base URL 来源优先级：

1. 环境变量 `OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_BASE_URL`
2. CLI 参数，例如 `--topic-api-key`、`--topic-model`
3. `--topic-api-key-path`，默认是 `api.txt`
4. `~/.codex/config.toml` 中 `--topic-model-provider` 指向的 provider

topic 结果会写入 `language_content.topic`，格式为：

```text
major_topic/minor_topic
```

短 utterance guard 会把 `yeah`、`ok`、`uh` 这类无主题短回应直接标成
`other/insufficient_context`，不调用外部 API。API 响应默认缓存到：

```text
outputs/cache/topic_openai_responses_cache.jsonl
```

### 5.3 Audio Probe

程序：

```text
tagger/tools/basic_acoustic/audio_probe.py
```

模型：无。

读取原始音频 header 或 `ffprobe`，输出：

```text
basic_acoustic.duration_sec
basic_acoustic.sample_rate_hz
basic_acoustic.channels
```

### 5.4 Silence / VAD

优先程序：

```text
tagger/tools/basic_acoustic/native_metadata_vad.py
```

模型：无。优先从 `sample.native_metadata` 中读取：

```text
silence_segments
speech_segments
vad_segments
segments
utterances
words
```

如果 metadata 可用，直接确定性生成 `basic_acoustic.silence_segments`。

fallback 程序：

```text
tagger/tools/basic_acoustic/firered_vad_silence_detector.py
```

模型：

```text
FireRedVAD VAD
models/FireRedVAD/pretrained_models/FireRedVAD/VAD
```

默认 Python 环境：

```text
.runtime/fireredvad_rebuild_py310/bin/python
```

之后用：

```text
tagger/tools/basic_acoustic/silence_ratio_calculator.py
```

计算 `basic_acoustic.silence_ratio`。

### 5.5 Speaker

总线程序：

```text
tagger/pipelines/speaker_evidence.py
tagger/tools/speaker_v2/
```

`tagger.pipelines.tagging` 直接调用 speaker v2，不经过旧 speaker registry，
也不再根据 native metadata 或声道布局分流。默认 `quality-shadow` profile 使用：

```text
MOSS-Transcribe-Diarize
FireRed VAD
NVIDIA Streaming Sortformer 4spk v2
Pyannote Community-1
SpeechBrain ECAPA
Brouhaha
```

公开输出固定为六字段加 `profiles` 画像数组：

```text
speaker.speaker_count
speaker.multi_speaker
speaker.speaker_change_count
speaker.speaker_change
speaker.overlap_ratio
speaker.speaker_overlap
speaker.profiles
```

`profiles` 是 2026-08-26 起接入的确定性说话人画像（语速、音高档位、片段内
相对音量），与六个 claim 使用同一 decision timeline，不引入新模型，失败或
证据不足时独立为 `null`，不影响六字段。可通过
`--speaker-profile-disable` 关闭画像计算。profile 计算与 `--speaker-profile`
选择的模型组合无关。

profile 可通过 CLI 选择：

```bash
--speaker-profile quality-shadow
--speaker-profile lean-shadow
```

旧 MOSS 显式启用门禁和 channel-activity fallback 已移除。
`--speaker-v2-skip-model-verification` 只跳过固定模型资产的 hash 校验，不会
下载模型，也不会跳过模型推理。完整 evidence、timeline comparison、claim
route 和 fusion 结果写入
`--artifact-dir/speaker_v2/<sample-id>-sample-<manifest-line>/`，不进入 public
tags-only 输出。

### 5.6 Brouhaha

程序：

```text
tagger/tools/audio_quality/brouhaha_signal_estimator.py
```

模型：

```text
Brouhaha
models/brouhaha/brouhaha-vad/models/best/checkpoints/best.ckpt
```

默认 Python 环境：

```text
.runtime/fireredvad_rebuild_py310/bin/python
```

输出：

```text
audio_quality.snr_db
```

Brouhaha C50 仍由工具产出（`internal.brouhaha_c50_db`），但只进入内部
evidence 用于与 Rec-RIR C50 交叉验证，不进入公开输出。

### 5.7 DNSMOS

程序：

```text
tagger/tools/audio_quality/dnsmos_quality_estimator.py
```

模型：

```text
models/DNS-Challenge/DNSMOS/DNSMOS/sig_bak_ovr.onnx
models/DNS-Challenge/DNSMOS/DNSMOS/model_v8.onnx
```

默认 Python 环境：

```text
.runtime/recrir_py310_torch271/bin/python
```

输出：

```text
audio_quality.dnsmos_sig
audio_quality.dnsmos_bak
audio_quality.dnsmos_ovrl
audio_quality.dnsmos_p808
```

### 5.8 FireRed AED

程序：

```text
tagger/tools/sound_field_scene/firered_aed_detector.py
```

模型：

```text
FireRedVAD AED
models/FireRedVAD/pretrained_models/FireRedVAD/AED
```

默认 Python 环境：

```text
.runtime/fireredvad_rebuild_py310/bin/python
```

输出：

```text
sound_field_scene.speech_music_events
sound_field_scene.music_present
```

2026-08-25 起 `singing`、`music` 进入 `speech_music_events`（及 `music_present = true`）
需满足事件占比 ≥ `--firered-aed-min-singing-ratio` / `--firered-aed-min-music-ratio`
（均默认 0.10，caption_pairs_3000 校准：语音帧被帧级误判为歌声/音乐的短段占比均 < 0.10，
真实歌声/音乐占比远高）。被门控的段仍保留在内部 evidence
（`event_segments`/`event_ratios`/`event_gates`）。

### 5.9 PANNs（已废弃，2026-08-25）

程序：

```text
tagger/tools/sound_field_scene/panns_background_detector.py
```

模型：

```text
PANNs Cnn14 AudioSet
models/audioset_tagging_cnn/checkpoints/Cnn14_mAP=0.431.pth
```

默认 Python 环境：

```text
.runtime/panns_py310/bin/python
```

PANNs stage 与 `sound_field_scene.sound` 字段已于 2026-08-25 废弃删除
（`noise_composition` 取代其功能）。工具模块、模型与 runtime 均保留，
供后续交叉验证 evidence 使用，但 stage 未注册、不可通过 `--only-tags`
选择，其输出不得进入公开 tags。

### 5.9b DASS

程序：

```text
tagger/tools/sound_field_scene/dass_noise_type_detector.py
```

模型：

```text
DASS medium AudioSet-2M（49M 参数，mAP 48.9）
models/DASS/saurabhati__DASS_medium_AudioSet_48.9/
```

checkpoint 由 sure-harness 部署后复制到项目内；权重版本固定在
`DASS_MODEL_VERSION`（`huggingface:saurabhati/DASS_medium_AudioSet_48.9@250cdd3…`）。

默认 Python 环境（sure-harness 的模型 venv）：

```text
~/sure-harness_v1/sure/models/saurabhati__DASS_medium_AudioSet_48.9/.venv/bin/python
```

输出：

```text
sound_field_scene.external_noise_type
sound_field_scene.noise_composition
```

DASS 是默认链路的背景噪音主模型。`external_noise_type` 输出的是
docs/DASS.md 的类别键（`music`/`animal`/`mechanical`/`nature`/`formless`/
`channel_environment`）：全量 527 类向量中任一未被排除的标签达到默认
阈值 `0.25`（2026-08-24 在 phase2 上校准，见 docs/tags-and-methods.md
3.4 说明），其所属类别即进入结果，按各类别最高分降序排列；排除政策
同样作用于类别推导（Silence 不会把干净语音样本标成 `formless`），
人类声音与未归类标签永不公开。阈值可通过 `--dass-threshold` 修改。
默认排除策略（主语音、静音、声学场景、混响、回声不算
背景噪音）只作用于内部 evidence 的 top 事件；传 `--no-exclusion`
后排除策略整体关闭，便于观察原始类别分布。成功但没有达到阈值的
类别时输出空数组，工具失败时输出 `null`。

`noise_composition` 把 `external_noise_type` 的每个类别展开为具体标签：
全量 527 维 sigmoid 向量按 docs/DASS.md 的类别归组（映射表在
`tagger/tools/sound_field_scene/dass_categories.py`，不受排除策略影响），
公开 `music`/`animal`/`mechanical`/`nature`/`formless`/
`channel_environment` 六个键，每类 top-3（`--dass-composition-top-k`）且
不低于 0.25（`--dass-composition-threshold`，2026-08-25 起默认值与类别
阈值对齐，保证有类别的行组成非空）。音乐类别以 FireRed AED 的
`music_present` 门控（AED 先于 DASS 运行）；人类声音和未归类标签只进
内部 evidence 的 `category_events`，声道/环境/背景类别的分数也在其中，
留作 far_field/混响标签的补充证据。

### 5.10 Rec-RIR

程序：

```text
tagger/tools/room_acoustic/rir_estimator.py
tagger/tools/room_acoustic/rt60_estimator.py
tagger/tools/room_acoustic/c50_estimator.py
```

模型：

```text
Rec-RIR
models/Rec-RIR/config/Rec-RIR.toml
models/Rec-RIR/ckpt/epoch35.tar
```

默认 Python 环境：

```text
.runtime/recrir_py310_torch271/bin/python
```

输出：

```text
room_acoustic.rt60_sec
room_acoustic.c50_db
```

RIR 结果作为内部 artifact 保存，public tags-only 输出只保留派生出的 RT60 和
C50。

### 5.11 FireRed LID

见 5.1b。

## 6. 补充标签模式

补标使用同一个入口，只是把已有 tags-only JSONL 作为 base：

```bash
PYTHONPATH=. python3 scripts/run_tagger.py \
  --manifest phase2_asr_sample/manifest.jsonl \
  --input-tags outputs/phase2_full_pipeline_tags.jsonl \
  --output outputs/phase2_plus_topic.jsonl \
  --artifact-dir outputs/phase2_plus_topic_artifacts \
  --only-tags language_content.topic \
  --missing-only \
  --topic-enable \
  --topic-api-key-path api.txt
```

关键规则：

| 参数 | 行为 |
| --- | --- |
| `--input-tags` | 读取已有 tags-only JSONL。行号必须和 manifest 对齐。 |
| `--sample-id` | 只处理指定样本；可重复传入。 |
| `--only-tags` | 根据指定 tag path、tag group 或 stage 决定要调度哪些 stage。 |
| `--missing-only` | 先按指定 tag path 判断哪些当前为 `null`，再决定是否调度对应 stage。 |

没有 `--input-tags` 时，如果传入 `--sample-id`，输出只包含选中的样本。

有 `--input-tags` 时，未选中的样本会原样写入新输出；选中的样本会先合并旧
tags，再运行本次指定的 stage。

补标时推荐使用具体 tag path，而不是宽泛 group/stage。例如：

```bash
--only-tags language_content.topic
--only-tags speaker.speaker_count,speaker.multi_speaker,speaker.speaker_change_count,speaker.speaker_change,speaker.overlap_ratio,speaker.speaker_overlap,speaker.profiles
--only-tags basic_acoustic.silence_segments,basic_acoustic.silence_ratio
```

原因是 `--missing-only` 只能用具体 tag path 判断当前值是否为 `null`；
如果传入 `speaker` 这种 group，pipeline 会把它作为一个 stage 运行。

需要注意，当前执行单元仍然是 stage，不是单个字段。也就是说，某个 stage
一旦被调度，就可能重算并覆盖该 stage 负责的多个字段。例如：

```text
--only-tags language_content.topic
```

只会调度 topic stage，因此只影响 `language_content.topic`。

```text
--only-tags speaker.multi_speaker
```

会调度 speaker stage；speaker stage 运行后可能同时写入
全部六个 `speaker.*` 字段。如果旧结果中这些字段都为空，这通常是期望行为；
如果只想严格保留同 stage 的其它旧字段，当前 pipeline 还没有字段级执行模式。

如果补标 stage 需要依赖 duration/channels，而旧 tags 中没有这些值，
pipeline 会自动补跑 `audio_probe`。例如只补 `speaker.*` 时，如果
`basic_acoustic.duration_sec` 或 `channels` 缺失，会先读取音频元数据。

无 transcript guard 在补标模式也会生效。对 transcript 为空的样本补
`language_content.*` 时，pipeline 会先尝试使用 speaker-v2 ASR 作为替代文本；
只有没有可用 ASR 时才按当前规则写入 `null`。补其它标签时仍会调用对应音频
或非语言工具。

## 7. 常用命令

完整链路：

```bash
PYTHONPATH=. python3 scripts/run_tagger.py \
  --manifest phase2_asr_sample/manifest.jsonl \
  --output outputs/phase2_full_tags.jsonl \
  --artifact-dir outputs/phase2_artifacts \
  --topic-enable \
  --topic-api-key-path api.txt
```

只跑 AMI 的 topic + metadata VAD + speaker smoke：

```bash
PYTHONPATH=. python3 scripts/run_tagger.py \
  --manifest ami_en2001a_utterances/manifest.jsonl \
  --output outputs/ami_smoke_tags.jsonl \
  --artifact-dir outputs/ami_smoke_artifacts \
  --sample-id EN2001a_utterance_00000 \
  --sample-id EN2001a_utterance_00001 \
  --sample-id EN2001a_utterance_00002 \
  --only-tags language_content.topic,basic_acoustic.silence_ratio,speaker \
  --topic-enable \
  --topic-api-key-path api.txt
```

给已有 phase2 结果只补 topic：

```bash
PYTHONPATH=. python3 scripts/run_tagger.py \
  --manifest phase2_asr_sample/manifest.jsonl \
  --input-tags outputs/phase2_full_pipeline_tags.jsonl \
  --output outputs/phase2_topic_patch.jsonl \
  --only-tags language_content.topic \
  --missing-only \
  --topic-enable \
  --topic-api-key-path api.txt
```

给 AMI 样本只补 speaker：

```bash
PYTHONPATH=. python3 scripts/run_tagger.py \
  --manifest ami_en2001a_utterances/manifest.jsonl \
  --input-tags outputs/old_ami_tags.jsonl \
  --output outputs/ami_speaker_patch.jsonl \
  --artifact-dir outputs/ami_speaker_artifacts \
  --only-tags speaker \
  --speaker-profile quality-shadow \
  --missing-only
```
