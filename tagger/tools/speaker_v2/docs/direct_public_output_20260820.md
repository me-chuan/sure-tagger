# Speaker v2 直接公开输出

> 更新日期：2026-09-01  
> 状态：certification gate 已移除；speaker profile v0.1 已接入 phase 0~1。

## 输出行为

Speaker v2 不再提供 `SpeakerEvidenceConfig.certification_gate_enabled` 或
`--certification-gate-enable`。resolver 完成 claim 路由后，直接把可决策结果写入
`evaluation_output.speaker` 和 `public_adapter.speaker`：

```json
{
  "speaker_count": 2,
  "multi_speaker": true,
  "speaker_change_count": 1,
  "speaker_change": true,
  "overlap_ratio": 0.125,
  "speaker_overlap": true,
  "profiles": [
    {
      "speaker_id": "speaker_1",
      "speech_rate": {
        "band": "normal",
        "value": 4.2,
        "unit": "zh_char_per_sec"
      },
      "pitch": "mid",
      "speaker_volume": "normal"
    }
  ]
}
```

`profiles` 使用与 `speaker_count` 相同的 decision timeline。没有可用时间轴时为
`null`，有效音频但没有语音时为 `[]`；不可靠的单个画像值也保持 `null`。首版只
发布语言感知语速、相对音高档位和片段内相对音量，不推断年龄、性别、情绪或口音。

`evaluation_output.mode` 固定为 `direct`，`production_eligible` 和
`public_metadata_published` 固定为 `true`。`compat_metadata.json.gz` 同步保存同一份
speaker 对象，并设置 `published=true`。

这里有两层输出合同：standalone resolver 的 `public_adapter.speaker` 是上述六个
C/M/O/X 字段加 `profiles`；`run_record` 另行返回路由后的
`speaker_asr_transcript`。主 tagging adapter 在此基础上派生 `speaker_present`，并把
路由文本写入 `speaker.asr_transcript`，因此 tags-only 的完整 speaker 对象共九个
字段。原始双路候选始终只在内部 evidence/fusion artifact 中。

## 空值语义

移除上线门禁不等于强制生成数值。以下情况仍输出 `null`：

- claim 的 decision source 缺失或不可用；
- 多个实际 decision source 产生冲突；
- 数值派生所需的 timeline 字段缺失或非法。

claim status、decision source、evidence id、policy version 和 policy hash 继续写入
artifact，供故障定位和质量分析使用，但不再作为发布阻断条件。

## CLI

运行方式不再包含 certification gate 参数：

```bash
python3.11 scripts/run_speaker_evidence_v2.py \
  --manifest <manifest.jsonl> \
  --output-dir <output_dir> \
  --profile quality-shadow
```

若只需回归六个旧字段，可显式使用 `--speaker-profile-disable`；此时画像 evidence
记录为 `missing`，不会影响旧 claim。

`legacy-shadow`、`quality-shadow` 和 `lean-shadow` 名称继续保留，用于模型集合和
claim policy 选择；名称中的 `shadow` 不再表示 public adapter 被禁用。
当前 policy 为 `speaker_v2.claim_policy.20260831.1`。standalone CLI 默认
`legacy-shadow`，主 tagging CLI 默认 `quality-shadow`。

## 双路 ASR

speaker stage 对完整音频同时调用 MOSS-Transcribe-Diarize 和 FireRedASR2-AED。
只有 FireRed LID 明确返回 `en`，且文本至少含一个 ASCII 英文字母并且没有非 ASCII
字母时，
主 tagging 输出的 `speaker.asr_transcript` 才在 MOSS 可用时选择 MOSS；standalone
结果使用独立的 `speaker_asr_transcript` 字段承载同一选择。中文、混合、非拉丁或
未知语言选择 FireRed。没有语言元数据或 LID 失败都按 unknown 选择 FireRed。两路候选、`asr_route.selected_source`、
`language_route` 和失败/fallback 原因只写入 fusion/evidence artifact，不改变
speaker C/M/O/X claim。FireRed 模型资产与 7 集对照见
[`asr双路评测报告_20260831.md`](../evalue/asr双路评测报告_20260831.md)。

独立 speaker CLI 与主 tagging CLI 都支持 `--firered-asr-disable-lid` 和
`--firered-asr-lid-model`。禁用或加载失败时不会丢弃 FireRed ASR 文本，语言路由
按 unknown 处理；具体错误保存在候选与 `asr_route.language_error`。
