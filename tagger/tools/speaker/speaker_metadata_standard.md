# Speaker Metadata 与展示标签

本文档定义内部 speaker metadata 的字段含义，并说明当前按 `development.md` 展示的 utterance-level speaker 标签。

## Metadata 用途

MOSS diarize 和 channel activity route 都会归一成同一种内部 metadata。该 metadata 写入 `artifacts/speaker/*.json.gz`，用于排查和后续对齐；公开 tags-only output 不展示 route、工具名、模型名、timeline、recording summary 或 artifact path。

## 顶层字段

| field | type | meaning |
| --- | --- | --- |
| `metadata_version` | `string` | speaker metadata schema 版本。 |
| `sample_id` | `string` | 当前 sample/utterance 的 ID，来自 raw input。 |
| `recording_id` | `string` | 当前 sample 所属录音或会议 ID；无法从原生 metadata 读取时等于 `sample_id`。 |
| `input_kind` | `string` | 内部音频布局判断，例如 `mix_headset`、`separated_headset_channels`、`separated_headset_files`、`unknown_audio_layout`。 |
| `primary_route` | `string` | 生成该 metadata 的主路线，例如 `moss_diarize`、`moss_diarize_merged_headset` 或 `channel_activity`。 |
| `duration_sec` | `number` | 当前音频时长，单位秒。 |
| `speakers` | `array` | 匿名说话人列表，按当前 metadata 内部 speaker ID 汇总。 |
| `segments` | `array` | 归一化后的说话人时间片段。 |
| `overlap_segments` | `array` | 至少两个说话人同时 active 的时间片段。 |
| `utterances` | `array` | 对 target utterance 计算出的 utterance-level speaker metadata。 |
| `recording_summary` | `object` | 当前音频范围内的内部汇总统计，只用于诊断和派生，不作为公开展示标签。 |
| `quality` | `object` | 内部质量状态和 warning。 |

## `speakers[]`

| field | type | meaning |
| --- | --- | --- |
| `speaker_id` | `string` | 匿名 speaker ID，只在同一个 metadata/recording 内稳定，不表示真实身份。 |
| `source_channel_id` | `string/null` | channel-activity route 中对应的原始 channel ID；MOSS mixed/merged-headset route 通常为 `null`。 |
| `speech_duration_sec` | `number` | 该 speaker 在当前音频范围内的有效 speech 总时长。 |
| `turn_count` | `int` | 合并短间隔后的该 speaker turn 数。 |

## `segments[]`

| field | type | meaning |
| --- | --- | --- |
| `segment_id` | `string` | 内部 segment ID。 |
| `start_sec` | `number` | segment 起始时间，单位秒，相对当前音频起点。 |
| `end_sec` | `number` | segment 结束时间，单位秒，相对当前音频起点。 |
| `speaker_id` | `string` | 该 segment 的匿名 speaker ID。 |
| `source_channel_id` | `string/null` | channel-activity route 的来源 channel；无来源 channel 时为 `null` 或缺省。 |
| `text` | `string` | 可选内部转写文本，只用于对齐检查，不替换 raw input transcript。 |

## `overlap_segments[]`

| field | type | meaning |
| --- | --- | --- |
| `start_sec` | `number` | overlap 起始时间，单位秒。 |
| `end_sec` | `number` | overlap 结束时间，单位秒。 |
| `speaker_ids` | `array<string>` | 该 overlap 区间内同时 active 的匿名 speaker ID。 |

## `utterances[]`

`utterances[]` 是当前展示标签的主要来源。每个元素对应一个 target utterance；当输入音频本身就是 utterance 切片时，通常只有一个元素，且 `unit_id` 与 `sample_id` 一致。

| field | type | meaning |
| --- | --- | --- |
| `unit_id` | `string` | utterance ID，优先与 raw input 的 `sample_id` 对齐。 |
| `start_sec` | `number` | utterance 起始时间，单位秒，相对当前音频起点。 |
| `end_sec` | `number` | utterance 结束时间，单位秒，相对当前音频起点。 |
| `primary_speaker_id` | `string/null` | utterance 内覆盖时长最长的匿名 speaker ID。 |
| `active_speaker_count` | `int` | utterance 内有 speech 覆盖的 speaker 数。 |
| `speaker_change_count` | `int` | utterance 内发生的 speaker change 次数。 |
| `speaker_change` | `bool` | `speaker_change_count > 0`。 |
| `is_overlapped` | `bool` | `overlap_ratio >= 0.05` 时为 `true`。 |
| `overlap_ratio` | `number` | `overlap_duration_sec / speech_union_duration_sec`，范围 `[0, 1]`；当 `speech_union_duration_sec == 0` 时取 `0`。 |
| `overlap_duration_sec` | `number` | utterance 内 overlap 总时长，单位秒。 |
| `speech_union_duration_sec` | `number` | utterance 内所有 speaker segment 的并集 speech 时长，单位秒；分母只累计有 speech 覆盖的时间。 |
| `primary_speaker_coverage` | `number/null` | primary speaker speech 覆盖时长 / utterance 时长，范围 `[0, 1]`。 |
| `turn_position` | `single/start/continue/overlap` | 内部粗粒度 turn 位置：单人、speaker 开始、延续上一 speaker、或重叠说话。 |

## `recording_summary`

`recording_summary` 保留当前音频范围内的内部统计。它可以帮助排查 MOSS/channel route 质量，也可在没有 `utterances[]` 且当前 sample 音频本身就是 utterance 切片时作为 fallback 派生三项公开标签；但这些字段本身不进入公开 output。

| field | type | meaning |
| --- | --- | --- |
| `speaker_count` | `int` | 当前音频范围内有效 speaker 数。 |
| `multi_speaker` | `bool` | `speaker_count >= 2`。 |
| `turn_count` | `int` | 当前音频范围内合并后的 speaker turn 总数。 |
| `speaker_change_count` | `int` | 当前音频范围内 speaker change 次数。 |
| `speaker_change_points` | `array<number>` | speaker change 发生时间点，单位秒。 |
| `speaker_change_rate_per_min` | `number/null` | 每分钟 speaker change 次数。 |
| `overlap_ratio_speech` | `number/null` | overlap 时长 / speech union 时长。 |
| `overlap_ratio_audio` | `number/null` | overlap 时长 / 当前音频总时长。 |
| `dominant_speaker_ratio` | `number/null` | speech 时长最长 speaker 的 speech 时长 / speech union 时长。 |
| `speaker_balance` | `number/null` | 说话时长分布均衡度，范围 `[0, 1]`，越高越均衡。 |
| `crosstalk_level` | `none/low/medium/high/null` | 从 overlap ratio 派生的内部重叠说话等级。 |

## `quality`

| field | type | meaning |
| --- | --- | --- |
| `status` | `ok/failed` | metadata 构建质量状态。 |
| `warnings` | `array<object>` | 内部 warning 列表；不进入公开 output。 |

## Metadata 示例

```json
{
  "metadata_version": "speaker_diarization_v0.1",
  "sample_id": "AMI:ES2005a:utt_00010",
  "recording_id": "ES2005a",
  "input_kind": "mix_headset",
  "primary_route": "moss_diarize",
  "duration_sec": 3.3,
  "speakers": [
    {
      "speaker_id": "spk_000",
      "source_channel_id": null,
      "speech_duration_sec": 2.4,
      "turn_count": 1
    },
    {
      "speaker_id": "spk_001",
      "source_channel_id": null,
      "speech_duration_sec": 0.8,
      "turn_count": 1
    }
  ],
  "segments": [
    {
      "segment_id": "seg_000001",
      "start_sec": 0.0,
      "end_sec": 2.4,
      "speaker_id": "spk_000",
      "source_channel_id": null,
      "text": "optional internal transcript"
    },
    {
      "segment_id": "seg_000002",
      "start_sec": 2.2,
      "end_sec": 3.0,
      "speaker_id": "spk_001",
      "source_channel_id": null
    }
  ],
  "overlap_segments": [
    {
      "start_sec": 2.2,
      "end_sec": 2.4,
      "speaker_ids": ["spk_000", "spk_001"]
    }
  ],
  "utterances": [
    {
      "unit_id": "AMI:ES2005a:utt_00010",
      "start_sec": 0.0,
      "end_sec": 3.3,
      "primary_speaker_id": "spk_000",
      "active_speaker_count": 2,
      "speaker_change_count": 1,
      "speaker_change": true,
      "is_overlapped": true,
      "overlap_ratio": 0.067,
      "overlap_duration_sec": 0.2,
      "speech_union_duration_sec": 3.0,
      "primary_speaker_coverage": 0.727,
      "turn_position": "overlap"
    }
  ],
  "recording_summary": {
    "speaker_count": 2,
    "multi_speaker": true,
    "turn_count": 2,
    "speaker_change_count": 1,
    "speaker_change_points": [2.2],
    "speaker_change_rate_per_min": 18.18,
    "overlap_ratio_speech": 0.067,
    "overlap_ratio_audio": 0.061,
    "dominant_speaker_ratio": 0.8,
    "speaker_balance": 0.811,
    "crosstalk_level": "low"
  },
  "quality": {
    "status": "ok",
    "warnings": []
  }
}
```

说明：

- `speaker_id` 是匿名 ID，只在同一个 recording 内稳定，不表示真实身份。
- `source_channel_id` 只用于已确认单通道单说话人的 channel-activity route；merged-headset MOSS 不把 headset channel 当作 speaker ID 或展示字段。
- `text` 只用于内部对齐检查，不替换 raw manifest transcript。
- `speakers`、`segments`、`overlap_segments`、`utterances`、`recording_summary` 都是内部 metadata，不进入公开 output。

## 当前展示标签

`development.md` 约定 sample 是 utterance-level。因此 speaker 分组只展示下面三个 utterance-level 标签：

| tag | type | source | meaning |
| --- | --- | --- | --- |
| `speaker.multi_speaker` | `bool/null` | `utterances[].active_speaker_count >= 2` | 当前 utterance 内是否至少有两个有效说话人。 |
| `speaker.speaker_change` | `bool/null` | `utterances[].speaker_change_count > 0` | 当前 utterance 内是否发生说话人切换。 |
| `speaker.speaker_overlap` | `bool/null` | `utterances[].is_overlapped` | 当前 utterance 内是否存在重叠说话。 |

如果 artifact 中没有 `utterances[]`，pipeline 只在当前 sample 音频本身就是 utterance 切片时使用 sample-level summary 作为 fallback。`recording_summary` 保留为内部诊断信息，不进入公开 tags-only output。
