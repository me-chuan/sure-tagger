# Development

本文件记录项目开发期的全局约束。它不是运行期 agent 指导文件；整体开发完成后如需面向 agent 的说明，另建 `AGENTS.md`。

根目录文档只放项目级接口和边界。具体工具的调度顺序、依赖、模型配置、缓存、失败联动和内部实现说明，放到对应 `tagger/tools/...` 目录下。

## 目标

本项目构建 sample-level 的 ASR 数据集打标工具。公开输出只包含本次打标得到的 tag 值，不包含 `sample_id`、原始记录、工具名、证据、置信度、来源、状态、warning、审计信息或推理过程。

当前 tag 分组：

| 分组 | 字段 |
| --- | --- |
| `basic_acoustic` | `duration_sec`、`sample_rate_hz`、`channels`、`silence_segments`、`silence_ratio`、`snr_db`、`c50` |
| `sound_field_scene` | `far_field`、`rir`、`rt60`、`c50`、`music`、`sound` |
| `speaker` | `multi_speaker`、`speaker_change`、`speaker_overlap` |
| `language_content` | `topic`、`language`、`word_count`、`punctuation`、`repetition`、`filler` |

## 全局原则

- 先结构化 closed raw-only 输入，再运行登记的 Python 标签程序。
- `corpus` 和 `sample` 在 pipeline 中视为不可变原始输入。
- 输入对象只能包含数据集原生数据，不得混入工具输出、推理、归一化结果、解析文档正文、运行时 provenance 或默认值。
- 最终 tag 只能来自 registry 登记的 Python 标签程序输出；不得由 LLM、人工推断、未登记脚本、corpus-level 默认值或 native metadata 直接生成。
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
    "silence_ratio": null,
    "snr_db": null,
    "c50": null
  },
  "sound_field_scene": {
    "far_field": null,
    "rir": null,
    "rt60": null,
    "c50": null,
    "music": null,
    "sound": null
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

约束：

- 最终输出不得包含 raw input、`sample_id`、工具标识、方法、状态、来源、证据、置信度、warning、rationale、prompt、模型名或审计结论。
- 字段缺失、无法可靠判断或对应程序输出非法时，字段值必须为 `null`。
- 同名字段如果位于不同路径，按不同 tag 处理。例如 `basic_acoustic.c50` 和 `sound_field_scene.c50` 不得跨字段复制，除非 registry 明确登记同一程序同时产出两个字段。

## 工具开发

- 工具代码放在对应 `tagger/tools/<tag_group>/` 目录。
- 每个公开 tag 必须通过该分组的 registry 暴露给 pipeline。
- 工具输出先进入内部结果对象，再由 pipeline/auditor 归并成 tags-only 输出。
- 工具级运行顺序和失败联动不要写在根目录文档；需要说明时，在对应工具目录下新增简短说明文件。
