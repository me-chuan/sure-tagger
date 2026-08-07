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
| `language_deterministic` | `language_content.language`, `word_count`, `punctuation`, `repetition`, `filler` |
| `topic` | `language_content.topic` |
| `audio_probe` | `basic_acoustic.duration_sec`, `sample_rate_hz`, `channels` |
| `silence` | `basic_acoustic.silence_segments`, `silence_ratio` |
| `speaker` | `speaker.multi_speaker`, `speaker_change`, `speaker_overlap` |
| `brouhaha` | `basic_acoustic.snr_db`, `basic_acoustic.c50` |
| `dnsmos` | `basic_acoustic.dnsmos_sig`, `dnsmos_bak`, `dnsmos_ovrl`, `dnsmos_p808` |
| `firered_aed` | `sound_field_scene.audio_events`, `music` |
| `panns` | `sound_field_scene.sound` |
| `recrir` | `sound_field_scene.rt60`, `sound_field_scene.c50` |

`--only-tags` 可以接收 stage 名、tag group 名或具体 tag path。例如：

```bash
--only-tags speaker
--only-tags language_content.topic,basic_acoustic.silence_ratio
--only-tags recrir
```

如果选中的 stage 需要音频 duration/channels，而已有 tags 中没有这些值，
pipeline 会自动补跑 `audio_probe`。

## 4. 无 transcript guard

如果 `sample.text.transcript` 为空，pipeline 会把该样本视为非语音或无可用语音
文本样本，并跳过这些 speech-dependent stages：

```text
language_deterministic
topic
silence
speaker
dnsmos
recrir
```

对应 public tags 会被设置为：

```text
language_content.* = null
basic_acoustic.silence_segments = null
basic_acoustic.silence_ratio = null
basic_acoustic.dnsmos_* = null
sound_field_scene.rt60 = null
sound_field_scene.c50 = null
speaker.multi_speaker = false
speaker.speaker_change = false
speaker.speaker_overlap = false
```

这些 stage 不会调用外部模型或 API。`audio_probe`、`brouhaha`、`firered_aed`
和 `panns` 仍可运行，因为它们可以用于纯噪声或无 transcript 音频的基础音频
分析和声音事件展示。

补标时这个 guard 仍然生效。若某条无 transcript 样本已有旧标签，但本次又
选择了上述 speech-dependent stage，pipeline 会按当前规则重置相关字段，以
避免对无语音文本样本继续做 speech-specific 推理。

## 5. 每个环节调用的程序和模型

### 5.1 语言确定性层

程序：

```text
tagger/tools/language_content/deterministic.py
```

模型：无。

输入：`sample.text.transcript`。

输出：

```text
language_content.language
language_content.word_count
language_content.punctuation
language_content.repetition
language_content.filler
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

优先程序：

```text
tagger/tools/speaker/native_metadata_diarizer.py
tagger/tools/speaker/metrics.py
```

模型：无。优先从 `sample.native_metadata` 中读取：

```text
speaker_segments
diarization_segments
segments
utterances
```

segment 需要 start/end 和 speaker 字段。speaker 字段可为：

```text
speaker
speaker_id
label
spk
```

如果 metadata 可用，pipeline 会先构建 speaker timeline，再由 `metrics.py`
生成公开标签：

```text
speaker.multi_speaker
speaker.speaker_change
speaker.speaker_overlap
```

fallback route：

1. 对 separated headset 且明确单通道单说话人的输入，可走
   `tagger/tools/speaker/channel_activity.py`。
2. 启用 `--moss-diarize-enable` 后，可走
   `tagger/tools/speaker/moss_diarizer.py`。

MOSS 默认模型配置：

```text
models/MOSS-Transcribe-Diarize-model
.runtime/moss_transcribe_diarize_py312/bin/python
```

MOSS 默认不启用；只在传入 `--moss-diarize-enable` 或测试注入 client 时运行。
Speaker 的完整 timeline 和 route 信息写入 `--artifact-dir/speaker/*.json.gz`，
不进入 public tags-only 输出。

### 5.6 Brouhaha

程序：

```text
tagger/tools/basic_acoustic/brouhaha_signal_estimator.py
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
basic_acoustic.snr_db
basic_acoustic.c50
```

### 5.7 DNSMOS

程序：

```text
tagger/tools/basic_acoustic/dnsmos_quality_estimator.py
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
basic_acoustic.dnsmos_sig
basic_acoustic.dnsmos_bak
basic_acoustic.dnsmos_ovrl
basic_acoustic.dnsmos_p808
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
sound_field_scene.audio_events
sound_field_scene.music
```

### 5.9 PANNs

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

输出：

```text
sound_field_scene.sound
```

默认阈值是 `0.30`，可通过 `--panns-threshold` 修改。

### 5.10 Rec-RIR

程序：

```text
tagger/tools/sound_field_scene/rir_estimator.py
tagger/tools/sound_field_scene/rt60_estimator.py
tagger/tools/sound_field_scene/c50_estimator.py
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
sound_field_scene.rt60
sound_field_scene.c50
```

RIR 结果作为内部 artifact 保存，public tags-only 输出只保留派生出的 RT60 和
C50。

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
--only-tags speaker.multi_speaker,speaker.speaker_change,speaker.speaker_overlap
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
`speaker.multi_speaker`、`speaker.speaker_change` 和
`speaker.speaker_overlap`。如果旧结果中这三个字段都为空，这通常是期望行为；
如果只想严格保留同 stage 的其它旧字段，当前 pipeline 还没有字段级执行模式。

如果补标 stage 需要依赖 duration/channels，而旧 tags 中没有这些值，
pipeline 会自动补跑 `audio_probe`。例如只补 `speaker.*` 时，如果
`basic_acoustic.duration_sec` 或 `channels` 缺失，会先读取音频元数据。

无 transcript guard 在补标模式也会生效。也就是说，对 transcript 为空的样本
补 `topic`、`silence`、`speaker`、`dnsmos` 或 `recrir` 时，pipeline 不会调用
对应模型，而会按当前规则写入 `null` 或 speaker 的 `false`。

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
  --only-tags speaker.multi_speaker,speaker.speaker_change,speaker.speaker_overlap \
  --missing-only
```
