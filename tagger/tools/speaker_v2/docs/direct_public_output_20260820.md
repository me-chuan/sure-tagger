# Speaker v2 直接公开输出

> 更新日期：2026-08-20  
> 状态：certification gate 已移除。

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
  "speaker_overlap": true
}
```

`evaluation_output.mode` 固定为 `direct`，`production_eligible` 和
`public_metadata_published` 固定为 `true`。`compat_metadata.json.gz` 同步保存同一份
speaker 对象，并设置 `published=true`。

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

`legacy-shadow`、`quality-shadow` 和 `lean-shadow` 名称继续保留，用于模型集合和
claim policy 选择；名称中的 `shadow` 不再表示 public adapter 被禁用。
