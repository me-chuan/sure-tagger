# Development

本文件记录项目开发期的全局约束。它不是运行期 agent 指导文件；整体开发完成后如需面向 agent 的说明，另建 `AGENTS.md`。

根目录文档只放项目级接口和边界。具体工具的调度顺序、依赖、模型配置、缓存、失败联动和内部实现说明，放到对应 `tagger/tools/...` 目录下。

## 目标

本项目构建 sample-level 的 ASR 数据集打标工具。公开输出只包含本次打标得到的 tag 值，不包含 `sample_id`、原始记录、工具名、证据、置信度、来源、状态、warning、审计信息或推理过程。

当前 tag 分组：

| 分组 | 字段 |
| --- | --- |
| `basic_acoustic` | `duration_sec`、`sample_rate_hz`、`channels`、`silence_segments`、`silence_ratio` |
| `audio_quality` | `snr_db`、`dnsmos_sig`、`dnsmos_bak`、`dnsmos_ovrl`、`dnsmos_p808` |
| `room_acoustic` | `far_field`、`rt60_sec`、`c50_db` |
| `sound_field_scene` | `speech_music_events`、`music_present`、`sound`、`external_noise_type`、`noise_composition` |
| `speaker` | `speaker_count`、`multi_speaker`、`speaker_change_count`、`speaker_change`、`overlap_ratio`、`speaker_overlap` |
| `language_content` | `topic`、`language`、`word_count`、`punctuation`、`repetition`、`filler` |

其中 `language_content.language` 由 FireRed LID 音频模型产出（`firered_lid`
stage），其余 `language_content` 字段由确定性文本工具产出。
`sound_field_scene.external_noise_type` 由 DASS 音频模型产出（`dass`
stage），值为 docs/DASS.md 类别键数组（见下方约束 bullet）。DASS 是
默认链路的背景噪音主模型。排除策略是全有/全无的，传 `--no-exclusion`
时全部关闭。PANNs 不再默认启用，
但仍可通过 `--only-tags panns` 或 `--only-tags sound_field_scene.sound`
显式运行，产出 `sound_field_scene.sound`（保留字段）。
Brouhaha 的 C50 预测只作为内部 evidence（`internal.brouhaha_c50_db`）用于
与 `room_acoustic.c50_db` 交叉验证，不进入公开输出。

## 全局原则

- 先结构化 closed raw-only 输入，再运行登记的 Python 标签程序。
- `corpus` 和 `sample` 在 pipeline 中视为不可变原始输入。
- 输入对象只能包含数据集原生数据，不得混入工具输出、推理、归一化结果、解析文档正文、运行时 provenance 或默认值。
- 最终 tag 只能来自 registry 登记的 Python 标签程序输出；登记工具可以在显式启用时调用模型或外部 API，但不得由人工推断、未登记脚本、corpus-level 默认值、native metadata 或绕过 pipeline 的 LLM 输出直接生成。
- 工具内部可以使用模型、规则、阈值、缓存、证据和审计信息，但这些内容不得进入公开 tags-only 输出。
- 程序未实现、不可用、失败、缺失字段或输出非法时，对应最终 tag 为 `null`。
- 新增或变更 tag 时，同步更新 schema、registry、pipeline、resolver/auditor 和测试样例；只有全局接口变化才需要更新本文件。

## 输入 Schema

输入是封闭 raw-only schema：

```json
{
  "corpus": {
    "dataset_name": "",
    "source_urls": {
      "article": [],
      "github": [],
      "huggingface": [],
      "dataset_card": []
    },
    "native_metadata": {}
  },
  "sample": {
    "sample_id": "",
    "audio": {
      "path": ""
    },
    "text": {
      "transcript": ""
    },
    "native_metadata": {}
  }
}
```

约束：

- 顶层只允许 `corpus`、`sample`。
- `corpus` 只允许 `dataset_name`、`source_urls`、`native_metadata`。
- `source_urls` 只允许 `article`、`github`、`huggingface`、`dataset_card` 四个数组字段。
- `sample` 只允许 `sample_id`、`audio`、`text`、`native_metadata`。
- `sample.audio` 只允许 `path`。
- `sample.text` 只允许 `transcript`。
- `native_metadata` 只能保存数据集原始记录中已有键值。
- 数据集原生但无法放入固定字段的内容，只能放入对应层级的 `native_metadata`。
- 不允许写入 `uri`、`format`、`dataset_field`、`raw_documents`、`raw_metadata`、`metadata`、`provenance`、`manifest_path`、`row_index`、`source_split`、`raw_record`、`raw_text_fields` 或其他扩展字段。
- 不允许把网页正文、README 正文、dataset card 正文、字段解释、规范化字段名、运行时路径、split、行号、缓存键、工具输出或派生值写入 raw input。
- `sample.sample_id`、`sample.audio.path`、`sample.text.transcript` 必须来自数据集原生字段或原始 manifest；运行时生成的定位信息只能进入内部 provenance。

## 输出 Schema

公开输出是 tags-only JSON：

```json
{
  "basic_acoustic": {
    "duration_sec": null,
    "sample_rate_hz": null,
    "channels": null,
    "silence_segments": null,
    "silence_ratio": null
  },
  "audio_quality": {
    "snr_db": null,
    "dnsmos_sig": null,
    "dnsmos_bak": null,
    "dnsmos_ovrl": null,
    "dnsmos_p808": null
  },
  "room_acoustic": {
    "far_field": null,
    "rt60_sec": null,
    "c50_db": null
  },
  "sound_field_scene": {
    "speech_music_events": null,
    "music_present": null,
    "sound": null,
    "external_noise_type": null,
    "noise_composition": null
  },
  "speaker": {
    "speaker_count": null,
    "multi_speaker": null,
    "speaker_change_count": null,
    "speaker_change": null,
    "overlap_ratio": null,
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

约束：

- 最终输出不得包含 raw input、`sample_id`、工具标识、方法、状态、来源、证据、置信度、warning、rationale、prompt、模型名或审计结论。
- Rec-RIR 生成的 RIR 波形不得进入公开输出；pipeline 只公开由该波形计算出的 `room_acoustic.rt60_sec` 和 `room_acoustic.c50_db`，波形保存为内部 artifact。
- `sound_field_scene.speech_music_events` 是 FireRed AED 检出的 `speech`、`singing`、`music` 类别数组；`sound_field_scene.music_present` 是该数组是否包含 `music` 的布尔值；`sound_field_scene.sound` 是 PANNs 达到阈值的 AudioSet 背景声显示名称数组（panns stage 需显式选择，默认不启用）；`sound_field_scene.external_noise_type` 是 DASS 检出的 docs/DASS.md 类别键数组：`music`、`animal`、`mechanical`、`nature`、`formless`、`channel_environment`（人类声音与未归类标签永不公开），由全量 527 类向量中未被排除（主语音、Silence、声学场景、混响、回声）且达到 `--dass-threshold`（默认 0.25）的标签归组而来，按各类别最高分降序排列。成功但没有检出时输出空数组，工具失败时输出 `null`；模型分数、比例和时间段不进入公开输出。
- `sound_field_scene.noise_composition` 是 DASS 全量 527 类 sigmoid 输出按 docs/DASS.md 类别归组后的背景声组成对象，固定含 `music`、`animal`、`mechanical`、`nature`、`formless`、`channel_environment` 六个键，每键为按分数降序的标签名数组（每类最多 `--dass-composition-top-k` 个，默认 3；入组阈值 `--dass-composition-threshold`，默认 0.3，与 `external_noise_type` 的 0.25 阈值相互独立）。音乐类别以 FireRed AED 为准：`music_present` 为 `false` 时输出空数组，为 `true` 或 AED 未运行（`null`）时输出 DASS 音乐类标签；人类声音与未归类标签只进内部 evidence（`category_events`），不进入公开输出。类别分数、证据和 AED 门控状态不进入公开输出。
- 字段缺失、无法可靠判断或对应程序输出非法时，字段值必须为 `null`。
- `audio_quality` 与 `room_acoustic` 是独立分组，字段不得跨组复制。Brouhaha C50（内部 `internal.brouhaha_c50_db`）只作为内部 evidence，不进入公开输出；公开的 `room_acoustic.c50_db` 只能来自 Rec-RIR 派生的 C50 估计。

## 工具开发

- 工具代码放在对应 `tagger/tools/<tag_group>/` 目录。
- 每个公开 tag 必须通过该分组的 registry 暴露给 pipeline。
- 工具输出先进入内部结果对象，再由 pipeline/auditor 归并成 tags-only 输出。
- 工具级运行顺序和失败联动不要写在根目录文档；需要说明时，在对应工具目录下新增简短说明文件。

## 下载相关
- 优先使用国内源
- 下载失败后终止，并提醒开发者手动下载上传
