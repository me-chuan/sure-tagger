# Speaker v2 标签与链路清单

> 更新日期：2026-09-01  
> 范围：当前 `speaker_v2` 的公开标签、内部 claim、内部 evidence capability 及规划能力。本文不包含 tagger 通用 pipeline 的其它公开标签。

## 1. 结论

- 当前正式 claim 为 `C/M/O/X`；standalone resolver 的公开 speaker 对象包含
  `speaker_count`、`multi_speaker`、`speaker_change_count`、`speaker_change`、
  `overlap_ratio`、`speaker_overlap` 和 `profiles`。其中 change count 和 overlap
  ratio 从 X/O 实际选中的 decision timeline 派生。
- 主 tagging adapter 另行派生 `speaker_present`，并发布双路路由后的
  `speaker.asr_transcript`，所以 tags-only speaker 合同共九个字段。
- `I/V` 和原始 `A` 候选是内部 evidence capability；`A` 的路由结果通过上一条
  tagging 字段公开。`D` 尚未接入正式 claim/output。
- Speaker v2 推理阶段不读取 native metadata。当前有效链路均属于“通过可评估模型”。native metadata 只允许在推理完成后用于评测。
- Certification gate 已移除；可决策的六字段结果会直接写入 `evaluation_output.speaker` 和 `public_adapter.speaker`。
- 下表按新版模型选择方案 `quality-shadow` 展开，同时保留 legacy、fallback、guard 和审计链路。
- 表中置信度是冻结数据集上的全局 SURE 指标估计，不是单条样本的校准概率。
- ASR 由 MOSS 和 FireRedASR2-AED 双路并行提供。只有 FireRed LID/语言元数据为
  `en`、FireRed 文本通过严格 ASCII-English script heuristic 且 MOSS 可用时才选择
  MOSS；中文、混合、非拉丁或未知语言（包括没有语言元数据）均选择 FireRed。
  FireRed 只提供 lexical/ASR evidence，不参与 C/M/O/X speaker timeline claim。

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
| A `asr_transcript` / `lexical_timeline`（内部 ASR candidate） | FireRedASR2-AED → transcript、原生 timestamp 和 confidence | 通过可评估模型 | 7 集对照：AISHELL CER `0.5767%/0.5916%`；Wenet meeting CER `4.5853%/4.4935%`；Wenet net CER `4.5239%/4.5248%`；LibriSpeech clean/other WER `1.7095%/3.5078%`；SlideSpeech `7.7737%`；GigaSpeech `10.0492%` |
| A `lexical_timeline`（内部 audit capability） | Whisper Base → transcript/lexical clock | 通过可评估模型 | 中文约 **64.52%**（`1-CER`）；英文约 **94.84%**（`1-WER`）；word coverage `65.88%/95.53%`；时间戳未单独评测 |
| D `full_diarization`（规划能力） | 当前没有正式 claim/output 链路 | — | — |

## 3. 公开与内部状态

| 能力 | 当前状态 |
| --- | --- |
| `C/M/O/X` | 对应六个 standalone 公开字段。resolver 直接发布可决策 candidate；冲突、缺失或非法派生仍输出 `null`。 |
| `profiles` | standalone resolver 的确定性公开画像数组；与 decision timeline 对齐，不引入新模型。 |
| `speaker_present` | 仅由主 tagging adapter 根据已校验的 `speaker_count > 0` 确定性派生。 |
| `A` / `speaker.asr_transcript` | MOSS/FireRed 原始候选和路由诊断属于内部 evidence；standalone 通过 `speaker_asr_transcript` 返回选中文本，主 tagging adapter 将其写入公开 `speaker.asr_transcript`。 |
| `I/V` | 内部 evidence，用于假设验证和 coverage 诊断，不直接写公开 speaker 标签。 |
| `D` | 当前没有正式 claim、resolver 输出或本轮 1k 链路。 |

## 4. 路由行为说明

1. `primary` 可用时直接产生 candidate；只有 primary 不可用时才选择有序 `fallback`。
2. 当前 guard 只生成 observation，`guards_affect_candidate=false`，不会修改 candidate。
3. `excluded/audit` evidence 会保留用于审计，但不参与该 claim 的候选决策。
4. 当前没有完成 1k fusion/ablation，因此没有多模型组合后的联合 SURE 分数；表中分数均为单模型分数。
5. MOSS 的 overlap negative 不能否决 pyannote/Sortformer 的 positive；pyannote 的 count/change 不参与 `quality-shadow` candidate。
6. ASR route 在 evidence collection 后确定：只有 FireRed LID/语言元数据 `en` 加上
   ASCII-English 文本且 MOSS 可用时选择 MOSS；未知语言也走 FireRed。路由不会改变
   C/M/O/X 的 claim source。

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

独立 speaker CLI 无参数时仍默认：

```text
--profile legacy-shadow
```

因此，不显式指定 profile 时：

- C/M/O/X 仍按 legacy 的三路 timeline 行为运行；
- MOSS 与 FireRedASR2-AED 同时运行，仅 FireRed LID/语言元数据为 `en` 且文本通过
  ASCII-English heuristic 时使用 MOSS；未知语言也使用 FireRed；
- I 使用 CAM++，ECAPA 默认关闭；
- V 使用 FireRedVAD，Brouhaha 默认关闭。

独立 speaker CLI 要运行本文描述的新版选型，需显式使用：

```text
--profile quality-shadow
```

主 tagging CLI 的 `--speaker-profile` 已默认 `quality-shadow`，无需额外参数；如需
回滚可显式传 `--speaker-profile legacy-shadow`。

## 7. 依据

- 路由/profile：`tagger/tools/speaker_v2/profiles.py`
- resolver/public adapter：`tagger/tools/speaker_v2/resolver.py`
- 直接公开输出合同：`tagger/tools/speaker_v2/docs/direct_public_output_20260820.md`
- evidence 采集：`tagger/pipelines/speaker_evidence.py`
- ASR 双路评测：`tagger/tools/speaker_v2/evalue/asr双路评测报告_20260831.md`
- SURE 汇总：`tagger/tools/speaker_v1/model_evaluate/evaluation_matrix.md`
- 模型选择实施记录：`tagger/tools/speaker_v2/docs/model_selection_and_framework_cleanup_implementation_20260817.md`
