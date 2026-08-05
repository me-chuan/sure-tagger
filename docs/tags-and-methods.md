# Signal Pipeline 标签与打标方法

本文档说明 `scripts/run_signal.py` 当前能够生成的公开标签、每个标签的
计算方法、音频预处理方式，以及输入和输出 JSON 示例。

## 1. 运行方式

CPU 运行：

```bash
python3 scripts/run_signal.py \
  --manifest phase1_asr_samples/manifest.jsonl \
  --output phase1_asr_samples/outputs/full_pipeline_tags.jsonl
```

在当前部署环境中让 PANNs 和 Rec-RIR 使用 GPU 0：

```bash
CUDA_VISIBLE_DEVICES=0 python3 scripts/run_signal.py \
  --manifest phase1_asr_samples/manifest.jsonl \
  --output phase1_asr_samples/outputs/full_pipeline_tags.jsonl \
  --panns-use-gpu \
  --recrir-use-gpu
```

模型和独立 Python 环境的路径配置在 `tagger/local_config.py`。当前
FireRed 和 Brouhaha 环境使用 CPU 版 PyTorch，因此运行示例没有传入它们的
GPU 参数。

## 2. 输入 JSONL

manifest 每行是一个封闭的 raw-only JSON 对象。例如：

```json
{
  "corpus": {
    "dataset_name": "phase1_asr_samples",
    "source_urls": {
      "article": [],
      "github": [],
      "huggingface": [],
      "dataset_card": []
    },
    "native_metadata": {}
  },
  "sample": {
    "sample_id": "example_001",
    "audio": {
      "path": "audio/example.wav"
    },
    "text": {
      "transcript": ""
    },
    "native_metadata": {}
  }
}
```

音频路径可以是绝对路径，也可以是相对当前工作目录或 manifest 所在目录的
路径。完整输入约束见 `development.md`。

## 3. 当前可打标签

当前 signal pipeline 实现了 16 个公开字段。

### 3.1 基础声学标签

| Tag | 类型 / 单位 | 打标方法 | 含义 |
| --- | --- | --- | --- |
| `basic_acoustic.duration_sec` | number / 秒 | 使用 Python WAV header；不支持时使用 `ffprobe` | 原始音频持续时间，保留 6 位小数。 |
| `basic_acoustic.sample_rate_hz` | integer / Hz | 读取原始音频流元数据 | 源文件采样率，不是模型重采样后的采样率。 |
| `basic_acoustic.channels` | integer | 读取原始音频流元数据 | 源文件声道数，不是模型降混后的声道数。 |
| `basic_acoustic.silence_segments` | array | FireRed VAD 检出语音段，再取语音段相对于整段音频的补集 | 静音时间段，每项为 `{"start_sec": number, "end_sec": number}`。 |
| `basic_acoustic.silence_ratio` | number / `[0, 1]` | 静音段总时长除以 `duration_sec` | 静音占整段音频的比例。 |
| `basic_acoustic.snr_db` | number / dB | Brouhaha 输出逐帧 SNR，再对所有有效预测取算术均值 | 语音相对背景噪声的强度；通常越大越好。 |
| `basic_acoustic.c50` | number / dB | Brouhaha 直接预测逐帧 C50，再取算术均值 | 模型预测的语音清晰度；通常越大越清晰。 |
| `basic_acoustic.dnsmos_sig` | number / MOS `[1, 5]` | DNSMOS P.835 SIG | 语音信号本身的质量和失真程度；越高越好。 |
| `basic_acoustic.dnsmos_bak` | number / MOS `[1, 5]` | DNSMOS P.835 BAK | 背景噪声的不干扰程度；越高越好。 |
| `basic_acoustic.dnsmos_ovrl` | number / MOS `[1, 5]` | DNSMOS P.835 OVRL | 综合语音和背景影响的整体质量；越高越好。 |
| `basic_acoustic.dnsmos_p808` | number / MOS `[1, 5]` | DNSMOS P.808 | P.808 模型预测的主观整体质量；越高越好。 |

DNSMOS 将短于 9.01 秒的音频循环补足，使用 9.01 秒窗口和 1 秒 hop，
最后对所有完整窗口的分数取均值。

### 3.2 声场和声音事件标签

| Tag | 类型 / 单位 | 打标方法 | 含义 |
| --- | --- | --- | --- |
| `sound_field_scene.rt60` | number / 秒 | Rec-RIR 估计 RIR；对 Schroeder 能量衰减曲线的 `-5 dB` 到 `-25 dB` 区间做 T20 线性拟合，并外推到 `-60 dB` | 混响衰减时间；通常越大表示混响尾部越长。 |
| `sound_field_scene.c50` | number / dB | 在 Rec-RIR 估计结果中定位最大绝对幅值的直达声，计算其后 50 ms 早期能量与剩余晚期能量之比 `10*log10(E_early/E_late)` | 基于估计 RIR 的清晰度；越大通常越清晰。 |
| `sound_field_scene.audio_events` | string array | FireRed AED | 检出的 `speech`、`singing`、`music` 类别，始终按这个固定顺序排列。事件时间段和帧比例仅保留为内部 evidence。 |
| `sound_field_scene.music` | boolean | FireRed AED | `audio_events` 是否包含 `music`。保留该字段用于直接进行音乐样本筛选。 |
| `sound_field_scene.sound` | string array | PANNs Cnn14 / AudioSet | 达到阈值的具体背景声类别，按模型分数从高到低排列，最多 10 类。公开结果只包含英文类别名，不包含分数。 |

PANNs 的默认阈值是 `0.30`。音频被切成互不重叠的 10 秒分块，最后一个
分块不足 10 秒时补零。每个 AudioSet 类别取所有分块中的最大概率，然后
输出达到阈值的前 10 个背景声类别。主语音、静音、室内/室外场景标签、
混响和回声被排除；音乐、歌唱、人群声、动物、自然声、车辆、机械和噪声等
类别可以进入结果。

`basic_acoustic.c50` 是 Brouhaha 的直接模型预测，
`sound_field_scene.c50` 是从 Rec-RIR 输出计算的物理指标。两者来源不同，
不能互相覆盖或当作同一个字段使用。

## 4. 模型输入预处理

Pipeline 保留原音频文件，不会先生成一个供所有模型共享的转换版本。每个
模型适配器根据自身输入要求单独降混和重采样。

| 模块 | 实际送入模型的格式 | 处理方式 |
| --- | --- | --- |
| 音频元数据探测 | 原始格式 | 只读取源文件，不重采样、不降混。 |
| FireRed VAD / AED | 16 kHz、单通道、16-bit PCM WAV | 不满足要求时使用 FFmpeg 生成临时 WAV，推理后删除。 |
| Brouhaha | 16 kHz、单通道 | pyannote 在内存中对多通道取均值并重采样。 |
| DNSMOS | 16 kHz、单通道 | 多通道取均值，使用 librosa 重采样。 |
| PANNs Cnn14 | 32 kHz、单通道 | `librosa.load(..., sr=32000, mono=True)`。 |
| Rec-RIR | 16 kHz、单通道 | torchaudio 对多通道取均值并重采样，临时 WAV 推理后删除。 |

因此 8 kHz 或双通道音频可以正常进入模型。需要注意，8 kHz 上采样只能
满足模型输入格式，无法恢复原音频 4 kHz 以上已经不存在的频率信息；多通道
取平均也可能丢失通道间差异。

## 5. 输出 JSON 示例

公开输出也是 JSONL，每个输入样本对应一行，只包含 tag 值。输出行和输入
manifest 行顺序一致，但不会包含 `sample_id`、模型名、分数、置信度、
warning 或推理证据。

下面是当前 Pipeline 实际输出结构的完整示例：

```json
{
  "basic_acoustic": {
    "c50": 4.294436,
    "channels": 2,
    "dnsmos_bak": 1.066441,
    "dnsmos_ovrl": 1.045056,
    "dnsmos_p808": 2.162502,
    "dnsmos_sig": 1.174226,
    "duration_sec": 15.963062,
    "sample_rate_hz": 16000,
    "silence_ratio": 0.674248,
    "silence_segments": [
      {"start_sec": 0.0, "end_sec": 3.29},
      {"start_sec": 3.83, "end_sec": 4.15},
      {"start_sec": 5.21, "end_sec": 5.33},
      {"start_sec": 8.41, "end_sec": 13.22},
      {"start_sec": 13.74, "end_sec": 15.963062}
    ],
    "snr_db": -1.159983
  },
  "sound_field_scene": {
    "far_field": null,
    "rt60": 0.801379,
    "c50": 14.032025,
    "audio_events": ["singing", "music"],
    "music": true,
    "sound": ["Music"]
  },
  "speaker": {
    "multi_speaker": null,
    "speaker_change": null,
    "speaker_overlap": null
  },
  "language_content": {
    "topic": null,
    "language": null,
    "word_count": null,
    "punctuation": null,
    "repetition": null,
    "filler": null
  }
}
```

列表字段成功执行但没有检出时输出空数组，例如：

```json
{
  "audio_events": ["speech"],
  "music": false,
  "sound": []
}
```

工具未部署、音频无法读取、推理失败或结果校验失败时，对应字段输出
`null`。不同模型相互隔离，例如 PANNs 失败只会使 `sound` 为 `null`，不会
清空 FireRed 的 `audio_events` 和 `music`。

## 6. 当前预留字段

以下 10 个字段属于公开 schema，但尚未接入当前 signal pipeline 的已注册
工具，因此目前输出 `null`：

| Tag | 计划含义 |
| --- | --- |
| `sound_field_scene.far_field` | 是否为远场拾音或远距离声源。 |
| `speaker.multi_speaker` | 是否包含两个或更多不同说话人。 |
| `speaker.speaker_change` | 样本内是否发生说话人切换。 |
| `speaker.speaker_overlap` | 是否存在多个说话人同时发言。 |
| `language_content.topic` | 转写文本的主题或层级主题类别。 |
| `language_content.language` | 转写文本的语言。 |
| `language_content.word_count` | 转写文本的词数统计。 |
| `language_content.punctuation` | 标点数量和终止标点信息。 |
| `language_content.repetition` | 连续词语或短语重复。 |
| `language_content.filler` | `uh`、`um`、`ah` 等填充词统计。 |

## 7. 内部产物

Rec-RIR 估计的完整 RIR 波形不进入公开 JSON。默认保存位置为输出文件同级的
`artifacts/rir/` 目录，例如：

```text
phase1_asr_samples/outputs/artifacts/rir/
```

公开输出只保留从该 RIR 计算得到的 `sound_field_scene.rt60` 和
`sound_field_scene.c50`。
