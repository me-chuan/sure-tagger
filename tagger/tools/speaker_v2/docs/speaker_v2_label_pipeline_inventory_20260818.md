# Speaker v2 标签与链路清单

> 更新日期：2026-08-20  
> 范围：当前 `speaker_v2` 的公开标签、内部 claim、内部 evidence capability 及规划能力。本文不包含 tagger 通用 pipeline 的其它公开标签。

## 1. 结论

- 当前正式 claim 为 `C/M/O/X`；公开 speaker schema 包含 `speaker_count`、`multi_speaker`、`speaker_change_count`、`speaker_change`、`overlap_ratio`、`speaker_overlap`。其中 change count 和 overlap ratio 从 X/O 实际选中的 decision timeline 派生。
- `I/V/A` 是内部 evidence capability，不是当前公开标签；`D` 尚未接入正式 claim/output。
- Speaker v2 推理阶段不读取 native metadata。当前有效链路均属于“通过可评估模型”。native metadata 只允许在推理完成后用于评测。
- Certification gate 已移除；可决策的六字段结果会直接写入 `evaluation_output.speaker` 和 `public_adapter.speaker`。
- 下表按新版模型选择方案 `quality-shadow` 展开，同时保留 legacy、fallback、guard 和审计链路。
- 表中置信度是冻结数据集上的全局 SURE 指标估计，不是单条样本的校准概率。

## 2. 标签链路总表

| 标签名 | 链路 | 链路类型 | 预估置信度（SURE） |
| --- | --- | --- | --- |
| C `speaker_count`（公开 schema） | 音频 → Sortformer timeline → speaker count（primary） | 通过可评估模型 | **73.5%** exact count accuracy；MAE `0.292` |
| C `speaker_count`（公开 schema） | 音频 → MOSS timeline → speaker count（primary 不可用时 fallback） | 通过可评估模型 | **62.4%** exact count accuracy；MAE `0.428` |
| C `speaker_count`（公开 schema） | 音频 → pyannote timeline → speaker count（excluded/audit，不参与 candidate） | 通过可评估模型 | **33.5%** exact count accuracy；MAE `0.940` |
| M `multi_speaker`（公开 schema） | Sortformer timeline → `speaker_count >= 2`（primary） | 通过可评估模型 | **96.5%** multi accuracy |
| M `multi_speaker`（公开 schema） | MOSS timeline → `speaker_count >= 2`（negative false-positive guard） | 通过可评估模型 | **95.8%** multi accuracy |
| M `multi_speaker`（公开 schema） | pyannote timeline → `speaker_count >= 2`（excluded/audit） | 通过可评估模型 | **89.0%** multi accuracy |
| O `speaker_overlap` / `overlap_ratio`（公开 schema） | pyannote timeline → overlap bool/regions/ratio（primary） | 通过可评估模型 | **83.8%** bool accuracy；ratio MAE `0.0696`；frame/event F1 `70.87%/52.18%` |
| O `speaker_overlap` / `overlap_ratio`（公开 schema） | Sortformer timeline → overlap（secondary witness；primary 不可用时 fallback） | 通过可评估模型 | **82.8%** bool accuracy；ratio MAE `0.0672`；frame/event F1 `68.96%/46.32%` |
| O `speaker_overlap` / `overlap_ratio`（公开 schema） | MOSS timeline → overlap（positive-only corroboration；negative 不得 veto） | 通过可评估模型 | **67.5%** bool accuracy；ratio MAE `0.1125`；frame/event F1 `45.41%/31.79%` |
| X `speaker_change` / `speaker_change_count`（公开 schema） | MOSS timeline → change bool/count/points（primary） | 通过可评估模型 | **94.9%** bool accuracy；F1@0.25s/0.5s `57.16%/62.47%`；count MAE `1.473` |
| X `speaker_change` / `speaker_change_count`（公开 schema） | Sortformer timeline → change（recall witness；primary 不可用时 fallback） | 通过可评估模型 | **95.5%** bool accuracy；F1@0.25s/0.5s `55.24%/62.75%`；count MAE `1.978` |
| X `speaker_change` / `speaker_change_count`（公开 schema） | pyannote timeline → change（excluded/audit） | 通过可评估模型 | **90.1%** bool accuracy；F1@0.25s/0.5s `43.72%/49.99%`；count MAE `1.807` |
| I `speaker_identity_comparison`（内部 evidence） | 按 C policy 选择预测 timeline（通常 Sortformer，失效时 MOSS）→ non-overlap regions → ECAPA embedding/cosine → same/different（quality/lean） | 通过可评估模型 | 约 **89.21%**（`1-EER`）；test accuracy `96.43%`；predicted-region E2E 尚未评测 |
| I `speaker_identity_comparison`（内部 evidence） | 预测 timeline → non-overlap regions → CAM++ embedding/score → same/different（legacy；中文/显式 fallback） | 通过可评估模型 | 约 **82.60%**（`1-EER`）；test accuracy `94.37%`；当前运行阈值仍需校准 |
| V `speech_coverage`（内部 evidence） | Brouhaha → speech segments/coverage（quality primary） | 通过可评估模型 | **95.35%** VAD F1；boundary F1 `52.95%`；DCF `0.0876` |
| V `speech_coverage`（内部 evidence） | FireRedVAD → speech segments/coverage（低误报/边界 guard；legacy primary） | 通过可评估模型 | **92.24%** VAD F1；PFA `6.75%`；boundary F1 `19.09%` |
| A `lexical_timeline`（内部 audit capability） | MOSS → transcript/lexical clock | 通过可评估模型 | 中文约 **97.24%**（`1-CER`）；英文约 **96.29%**（`1-WER`）；word coverage `97.48%/96.51%` |
| A `lexical_timeline`（内部 audit capability） | Whisper Base → transcript/lexical clock | 通过可评估模型 | 中文约 **64.52%**（`1-CER`）；英文约 **94.84%**（`1-WER`）；word coverage `65.88%/95.53%`；时间戳未单独评测 |
| D `full_diarization`（规划能力） | 当前没有正式 claim/output 链路 | — | — |

## 3. 公开与内部状态

| 能力 | 当前状态 |
| --- | --- |
| `C/M/O/X` | 对应六个公开 speaker schema 字段。resolver 直接发布可决策 candidate；冲突、缺失或非法派生仍输出 `null`。 |
| `I/V/A` | 内部 evidence，用于假设验证、coverage 诊断和 lexical audit，不直接写公开 speaker 标签。 |
| `D` | 当前没有正式 claim、resolver 输出或本轮 1k 链路。 |

## 4. 路由行为说明

1. `primary` 可用时直接产生 candidate；只有 primary 不可用时才选择有序 `fallback`。
2. 当前 guard 只生成 observation，`guards_affect_candidate=false`，不会修改 candidate。
3. `excluded/audit` evidence 会保留用于审计，但不参与该 claim 的候选决策。
4. 当前没有完成 1k fusion/ablation，因此没有多模型组合后的联合 SURE 分数；表中分数均为单模型分数。
5. MOSS 的 overlap negative 不能否决 pyannote/Sortformer 的 positive；pyannote 的 count/change 不参与 `quality-shadow` candidate。

## 5. 置信度口径

- `C`：使用 exact `count_accuracy`，同时报告 `count_mae`。
- `M`：使用 `multi_accuracy`。
- `O`：使用样本级 `overlap_accuracy` 作为主估计，同时报告更严格的 frame/event F1。
- `X`：使用 `change_bool_accuracy` 作为布尔标签估计，同时报告 change-point F1 和 count MAE。
- `I`：由于 benchmark 正负样本约为 `1:10`，主估计使用更保守的 `1-EER`；test accuracy 仅作补充。
- `V`：使用时长级 VAD F1，同时报告边界 F1、PFA 或 DCF。
- `A`：使用 `1-CER`/`1-WER` 作为文本正确度代理；该分数不能代表 lexical timestamp 的置信度。

评测数据为冻结的 `ami_utterance_1k_v1`：C/M/O/X/V 共 1,000 条 utterance；I 从同一批数据构建 23,815 个 verification trials。AMI 上的分数仍需通过非 AMI、meeting-separated 数据复核，尤其是可能存在 AMI 预训练污染的模型。

## 6. 当前配置注意事项

CLI 无参数时仍默认：

```text
--profile legacy-shadow
```

因此，不显式指定 profile 时：

- C/M/O/X 仍按 legacy 的三路 timeline 行为运行；
- I 使用 CAM++，ECAPA 默认关闭；
- V 使用 FireRedVAD，Brouhaha 默认关闭。

要运行本文描述的新版选型，必须显式使用：

```text
--profile quality-shadow
```

## 7. 依据

- 路由/profile：`tagger/tagger/tools/speaker_v2/profiles.py`
- resolver/public adapter：`tagger/tagger/tools/speaker_v2/resolver.py`
- 直接公开输出合同：`tagger/tagger/tools/speaker_v2/docs/direct_public_output_20260820.md`
- evidence 采集：`tagger/tagger/pipelines/speaker_evidence.py`
- SURE 汇总：`tagger/tagger/tools/speaker_v1/model_evaluate/evaluation_matrix.md`
- 模型选择实施记录：`tagger/tagger/tools/speaker_v2/docs/model_selection_and_framework_cleanup_implementation_20260817.md`
