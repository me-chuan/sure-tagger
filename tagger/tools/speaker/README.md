# Speaker Layer

Speaker layer 从原始音频估计说话人结构。输入仍遵守 root `development.md` 的 raw-only schema，公开输出只包含 tags，不包含工具名、模型名、timeline、confidence、artifact path 或 warning。

## 快速开始

### Mix-Headset / mono 混合录音

混合录音优先走 MOSS diarize。MOSS 默认关闭，需要显式传 endpoint：

```bash
python3 scripts/run_signal.py \
  --manifest outputs/moss_smoke/ami_ES2005a_mix_headset_manifest.jsonl \
  --output outputs/moss_smoke/ami_ES2005a_moss_tags.jsonl \
  --artifact-dir outputs/moss_smoke/artifacts \
  --moss-diarize-enable \
  --moss-diarize-endpoint http://localhost:8000/v1/audio/transcriptions \
  --moss-diarize-model /hpc_stor03/sjtu_home/huifei.wang/models/moss_td_model
```

可选参数：

```text
--moss-diarize-model
--moss-diarize-timeout-sec
--moss-diarize-max-new-tokens
--moss-diarize-api-key
```

### 多通道 / separated headset

多通道 / separated headset 在启用 MOSS 时默认走 merged-headset MOSS：pipeline 会先把多通道 headset 音频混成临时 mono WAV，再对混合音频跑一次 MOSS diarize。这样让 MOSS 在同一个声场里做 speaker clustering，避免逐通道串音被重复识别成多路 speaker。

AMI 原始 separated headset 如果是多个文件（例如 `ES2005a.Headset-0.wav` 到 `ES2005a.Headset-3.wav`），生产输入应先把这些 headset 合成同一段多通道 WAV 或对应的 utterance-level 多通道切片，再写入 `sample.audio.path`。不要把单个 `Headset-N` 文件作为生产 speaker route 输入；单通道 headset 只适合作诊断。

```bash
python3 scripts/run_signal.py \
  --manifest path/to/headset_manifest.jsonl \
  --output outputs/headset_tags.jsonl \
  --artifact-dir outputs/artifacts \
  --moss-diarize-enable \
  --moss-diarize-endpoint http://localhost:8000/v1/audio/transcriptions \
  --moss-diarize-model /hpc_stor03/sjtu_home/huifei.wang/models/moss_td_model
```

如果没有配置 MOSS，或 merged-headset MOSS 失败，pipeline 才回退到 channel activity baseline。`--speaker-prefer-channel-activity` 可以显式先跑旧的 energy-based channel activity route。

如果路径或原生 metadata 标明是 `Mix-Headset`，即使音频是 stereo，也不会把左右声道当作 separated headset。

## Pipeline

### 1. Audio Probe

`tagger.pipelines.signal` 先读取 `sample.audio.path`，用 audio probe 得到：

```text
duration_sec
sample_rate_hz
channels
```

speaker layer 不依赖 transcript，也不读取人工 speaker label。

### 2. Route 选择

pipeline 根据音频和原生 metadata 选择 route：

| input | route | tool |
| --- | --- | --- |
| `mix_headset` / mono mixed recording | MOSS diarize | `moss_diarizer.py` |
| `separated_headset_channels` / multi-channel WAV with MOSS enabled | merged-headset MOSS diarize | `moss_diarizer.py` |
| `separated_headset_channels` / multi-channel WAV without MOSS | channel activity fallback | `channel_activity.py` |
| `separated_headset_files` | prepare multi-channel WAV before pipeline | preprocessing |
| unknown mono/mixed input with MOSS enabled | MOSS diarize | `moss_diarizer.py` |
| no usable route or tool failure | null speaker tags | pipeline fallback |

`--speaker-prefer-moss` 目前保留为兼容参数；启用 MOSS 时 separated headset 默认已经优先使用 merged-headset MOSS。

### 3. Route 输出归一

两个 route 都会先生成内部 timeline：

```text
speaker_id
start_sec
end_sec
source_channel_id
optional text
```

随后 `metrics.py` 把 timeline 归一成统一 speaker metadata。当前 raw-only schema 中的 `sample` 是 utterance-level，因此公开标签按当前 utterance 解释：

```text
speakers
segments
overlap_segments
utterances
recording_summary
quality
```

metadata 写入：

```text
<artifact_dir>/speaker/<row>_<sample_id>.<route>.json.gz
```

### 4. Public Tags

公开 output 只保留 `development.md` 中登记的 3 个 utterance-level speaker 字段：

```text
speaker.multi_speaker
speaker.speaker_change
speaker.speaker_overlap
```

公开标签优先从 speaker artifact 的当前 `utterances[]` 条目派生；没有 `utterances[]` 时，只在当前 sample 音频本身就是 utterance 切片的前提下使用 sample-level summary fallback。其它 timeline、speaker、overlap 和 summary 信息只留在 artifact 中，不进入公开 tags-only output。

`speaker.speaker_overlap` 使用 `overlap_ratio >= 0.05` 判断；`overlap_ratio = overlap_duration_sec / speech_union_duration_sec`，其中 `speech_union_duration_sec` 是 utterance 内所有 speaker segment 的并集 speech 时长。

完整 metadata 示例和字段来源见 `speaker_metadata_standard.md`。

## 关键文件

```text
tagger/tools/speaker/config.py
tagger/tools/speaker/moss_diarizer.py
tagger/tools/speaker/channel_activity.py
tagger/tools/speaker/metrics.py
tagger/tools/speaker/artifacts.py
tagger/tools/speaker/registry.py
tagger/pipelines/signal.py
```
