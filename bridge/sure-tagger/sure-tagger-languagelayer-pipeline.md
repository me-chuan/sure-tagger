# Sure Tagger 语言层 Pipeline 使用说明

本文档说明当前语言层 meeting-level tagging pipeline 的流程、输入输出、配置和常用命令。

项目路径：

```text
/hpc_stor03/sjtu_home/huifei.wang/sure-tagger
```

当前样板数据集：

```text
/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI
```

## 1. Pipeline 做什么

这条 pipeline 把原始 ASR 数据集先转成底层 segment manifest，再聚合成 meeting manifest，最终对每一整场会议生成语言层 tags。

当前支持的语言层 tags：

- `language`: 文本语言。
- `word_count`: 词数、字符数、token 数。
- `punctuation`: 标点数量和终止标点。
- `filler`: 填充词，例如 `uh`, `um`, `ah`。
- `repetition`: 连续词语重复。
- `topic`: 层级主题标签，包含大类、小类、关键词、专有名词。

AMI 当前使用两级粒度：

- `segment`: 底层解析粒度，用来从 AMI XML 中恢复话语片段、时间戳和 speaker。
- `meeting`: 最终打标粒度，把同一 `meeting_id` 下的所有 segment 合并成一条 meeting record。

正式 tag 输出是一场会议一条结果，而不是一个 segment 一条结果。

## 2. 整体流程

```text
AMI raw data
  |
  | build-manifest
  v
segment_manifest.jsonl
  |
  | build-meeting-manifest
  v
meeting_manifest.jsonl
  |
  | tag: language / word_count / punctuation / filler / repetition
  v
meeting deterministic tag results
  |
  | tag: topic with gpt-5.5 API
  v
meeting topic tag results
  |
  | inspect / report
  v
人工 QA 抽样文件和运行报告
```

各阶段含义：

1. `build-manifest`: 从数据集原始结构抽取 segment manifest。
2. `build-meeting-manifest`: 按 `meeting_id` 聚合 segment，生成 meeting manifest。
3. `tag`: 对 meeting manifest 中每场会议打语言层标签。
4. `inspect`: 合并 meeting manifest 和 tags，生成抽样 QA 文件。
5. `report`: 每次运行自动生成统计报告。

## 3. 代码结构

```text
sure_tagger/
  cli.py                    # 命令行入口
  schemas.py                # manifest/tag/error 基础结构
  meeting_manifest.py       # segment manifest 到 meeting manifest 的聚合
  datasets/ami.py           # AMI adapter
  text/
    normalize.py            # 文本清洗和标点拼接
    tokenizer.py            # tokenizer、标点统计
    context.py              # topic 上下文窗口
    key_terms.py            # 关键词和专有名词启发式抽取
  tags/
    language.py
    word_count.py
    punctuation.py
    filler.py
    repetition.py
    topic.py
  llm/
    client.py               # OpenAI API client
    cache.py                # JSONL cache
    prompts.py              # topic prompt 构造
  io/jsonl.py
  report.py

configs/
  ami.yaml
  tags_language_mvp.yaml
  topic_taxonomy_general.yaml
  topic_response_schema.json
```

## 4. 输入输出格式

### 4.1 Segment Manifest

segment manifest 是 JSONL，每行一条 AMI segment，主要作为底层解析结果。关键字段：

```json
{
  "corpus": {
    "dataset_name": "AMI",
    "native_metadata": {
      "annotation_release": "AMI Manual Annotations 1.7"
    }
  },
  "sample": {
    "sample_id": "AMI:ES2002a:A:ES2002a.sync.4",
    "audio": {
      "path": ".../ES2002a.Mix-Headset.wav",
      "start_sec": 77.408,
      "end_sec": 80.955
    },
    "text": {
      "transcript": "Hi, I'm David and I'm supposed to be an industrial designer.",
      "normalized_transcript": "Hi, I'm David and I'm supposed to be an industrial designer."
    },
    "native_metadata": {
      "meeting_id": "ES2002a",
      "speaker_id": "A",
      "segment_id": "ES2002a.sync.4",
      "meeting_type": "scenario",
      "nonword_events": []
    },
    "provenance": {
      "source_path": ".../ES2002a.A.segments.xml",
      "source_split": ""
    }
  }
}
```

### 4.2 Meeting Manifest

meeting manifest 是最终 tagger 的标准输入，每行一整场会议。关键字段：

```json
{
  "corpus": {
    "dataset_name": "AMI",
    "native_metadata": {
      "annotation_release": "AMI Manual Annotations 1.7"
    }
  },
  "sample": {
    "sample_id": "AMI:ES2002a",
    "audio": {
      "path": ".../ES2002a.Mix-Headset.wav",
      "start_sec": 77.408,
      "end_sec": 1800.0
    },
    "text": {
      "transcript": "Hi, I'm David...\nUm, I just got the project announcement...",
      "normalized_transcript": "Hi, I'm David... Um, I just got the project announcement...",
      "speaker_labeled_transcript": "[0:01:17-0:01:21] A: Hi, I'm David..."
    },
    "native_metadata": {
      "granularity": "meeting",
      "meeting_id": "ES2002a",
      "meeting_type": "scenario",
      "source_sample_count": 843,
      "text_segment_count": 760,
      "speaker_ids": ["A", "B", "C", "D"]
    },
    "provenance": {
      "source_path": "outputs/ami/segment_manifest.full.jsonl",
      "source_split": ""
    }
  }
}
```

其中：

- `text.transcript`: 纯文本，用于 `word_count`、`filler`、`repetition` 等确定性 tag。
- `text.speaker_labeled_transcript`: 带时间和 speaker 的文本，用于 `topic` prompt。
- `native_metadata.granularity`: 标记这是 `meeting` 级 record。

### 4.3 Tag Result

tag result 也是 JSONL，每行对应一整场会议。

```json
{
  "sample_id": "AMI:ES2002a",
  "tags": {
    "word_count": {
      "value": 5132,
      "confidence": 1.0,
      "method": "deterministic_tokenizer",
      "tool_version": "word_count_v0.1.0",
      "reliability": "L0",
      "details": {
        "word_count": 5132,
        "character_count": 31200,
        "token_count": 6100
      }
    }
  }
}
```

### 4.4 Topic Result

`topic` 使用层级标签：

```json
{
  "topic": {
    "value": {
      "major_topic": "technology_engineering",
      "minor_topic": "product_design"
    },
    "confidence": 0.78,
    "method": "llm_hierarchical_classification",
    "tool_version": "topic_v0.3.0",
    "reliability": "L2",
    "details": {
      "taxonomy": "general_topic_v0.1.0",
      "topic_keywords": ["remote", "control", "design"],
      "proper_nouns": ["AMI"],
      "evidence_scope": "meeting",
      "evidence_sample_count": 843,
      "prompt_version": "topic_hierarchical_v0.3.0",
      "provider": "openai_responses",
      "llm_call_count": 1,
      "chunking_strategy": "single_call",
      "cache_key": "..."
    }
  }
}
```

topic 调用策略：

- 如果整场会议的 `speaker_labeled_transcript` 不超过 `single_call_max_chars`，只调用一次 `gpt-5.5`。
- 如果超出上限，按 `chunk_chars` 分块，多次调用模型分别判断 chunk topic。
- 多 chunk 的会议不会再额外调用模型做汇总，而是在本地按 `chunk 字符数 * confidence` 加权投票，得到最终会议级 topic。

如果 API 不可用，会按配置 fallback 到 heuristic，并在 `details.llm_error` 中记录原因。

### 4.5 接口清单和作用

这里的“接口”分为本地 CLI 接口、数据接口、tag tool 接口、配置接口和大模型 API 接口。

**CLI 接口**

入口：

```bash
python3 -m sure_tagger.cli <command>
```

| 接口 | 作用 |
| --- | --- |
| `build-manifest` | 从原始数据集生成底层 segment manifest。当前支持 AMI。 |
| `build-meeting-manifest` | 从 segment manifest 聚合生成 meeting manifest，最终 tag 使用这个文件。 |
| `tag` | 对 meeting manifest 中的每场会议打标签，可用 `--tags` 指定要跑哪些 tag。 |
| `inspect` | 把 meeting manifest 和 tag result 合并成 QA 抽样文件，方便人工检查。 |
| `run-meeting-pipeline` | 一条命令执行 segment manifest、meeting manifest、meeting tags 和 QA 抽样。 |

**Dataset Adapter 接口**

AMI adapter：

```text
sure_tagger/datasets/ami.py
```

作用：

- 读取 AMI `words/*.words.xml` 和 `segments/*.segments.xml`。
- 展开 NITE standoff `href`。
- 恢复 segment transcript。
- 绑定音频路径和开始/结束时间。
- 输出统一 segment manifest record。

后续接入新数据集时，新增 dataset adapter 即可。只要 adapter 输出带 `meeting_id` 的 segment manifest，就可以复用 `build-meeting-manifest` 和后面的 tag tools。

**Manifest 数据接口**

meeting manifest 是所有 tagger 的标准输入。最小必需字段：

```text
corpus.dataset_name
sample.sample_id
sample.audio.path
sample.audio.start_sec
sample.audio.end_sec
sample.text.transcript
sample.native_metadata
sample.provenance
```

作用：

- 隔离不同数据集的原始结构。
- 让所有 tag tools 只依赖统一 sample 格式。
- 保存 provenance，方便追溯原始文件。
- 当前最终 tag 粒度是 `native_metadata.granularity = meeting`。

**Tag Tool 接口**

每个 tag tool 位于：

```text
sure_tagger/tags/
```

普通 tag 约定接口：

```python
tag(record, config=None)
```

`topic` 额外接收上下文：

```python
tag(record, config=None, context=context)
```

每个 tag 结果都包含：

```text
value
confidence
method
tool_version
reliability
details
```

作用：

- 每个 tag 可以独立开发、独立重跑。
- 结果带版本和方法，方便后续比较和回溯。

**Topic Taxonomy 接口**

topic taxonomy 配置：

```text
configs/topic_taxonomy_general.yaml
```

作用：

- 定义 `major_topic` 大类。
- 定义每个大类下的 `minor_topic` 小类。
- 让 topic 分类不硬编码在代码里。
- 后续扩展新领域时，只需要修改 taxonomy 配置。

topic 返回结构约束：

```text
configs/topic_response_schema.json
```

作用：

- 作为 topic 返回字段的结构定义。
- 当前默认不把它直接发给远端网关，而是使用 `json_object` 让模型返回 JSON。
- pipeline 会在本地校验 `major_topic/minor_topic` 是否属于 taxonomy，并校验置信度、关键词、专有名词等字段。
- 如果后续确认网关支持 Responses `json_schema`，可把 `use_json_schema` 改为 `true`。

**大模型 API 接口**

topic 使用 OpenAI-compatible Responses API。

当前配置：

```yaml
provider: openai_responses
name: gpt-5.5
api_key_path: api.txt
model_provider: apifusion
codex_config_path: /hpc_stor03/sjtu_home/huifei.wang/.codex/config.toml
```

参数说明：

| 参数 | 示例值 | 是否必需 | 作用 |
| --- | --- | --- | --- |
| `provider` | `openai_responses` | 是 | 指定大模型调用方式。`openai_responses` 表示使用 OpenAI-compatible Responses API。 |
| `name` | `gpt-5.5` | 是 | 指定 topic 分类使用的模型名称。 |
| `api_key_path` | `api.txt` | 是 | 指定 API key 文件路径。pipeline 会读取文件第一行作为 key，不会在日志中打印。 |
| `model_provider` | `apifusion` | 是 | 指定从 `.codex/config.toml` 的哪个 provider 配置读取 `base_url` 等网关信息。 |
| `codex_config_path` | `/hpc_stor03/sjtu_home/huifei.wang/.codex/config.toml` | 是 | 指定兼容网关配置文件路径，用于解析 `model_provider` 对应的接口地址。 |
| `temperature` | `0` | 否 | 控制模型输出随机性。topic 分类建议用 `0`，保证结果更稳定。 |
| `prompt_version` | `topic_hierarchical_v0.3.0` | 否 | 记录 prompt 版本，方便比较不同 prompt 下的结果。 |
| `timeout_sec` | `180` | 否 | 单次 API 请求最长等待秒数，超时后写入 bad samples 或触发 fallback。 |
| `use_json_schema` | `false` | 否 | 是否把 `schema_path` 作为 Responses API 的 `text.format=json_schema` 发给网关。当前 `apifusion` 网关对该格式返回 502，因此默认关闭，改用 `json_object` 并在本地做 taxonomy 校验。 |
| `single_call_max_chars` | `80000` | 否 | topic 会议文本不超过该字符数时，只调用一次模型完成整场会议分类。 |
| `chunk_chars` | `60000` | 否 | topic 会议文本超过 `single_call_max_chars` 时，每个 chunk 的最大字符数。 |

作用：

- 从 `api.txt` 读取 API key。
- 从 `.codex/config.toml` 读取兼容网关的 `base_url`。
- 调用 `{base_url}/responses`。
- 使用 `gpt-5.5` 做 topic 层级分类。
- 默认使用 `json_object` 约束模型输出，并在本地校验 taxonomy。若确认网关支持 Responses `json_schema`，可把 `use_json_schema` 改为 `true`。
- 在会议文本不超长时，每场会议只调用一次模型。
- 超长会议分块调用后本地加权汇总，不额外调用模型做汇总。

`api.txt`：

```text
/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/api.txt
```

作用：

- 保存从 `.codex/config.toml` 复制出来的 API key。
- 文件权限应为 `600`。
- 已加入 `.gitignore`，不要提交或打印内容。

API key 读取优先级：

```text
OPENAI_API_KEY 环境变量
  -> configs/tags_language_mvp.yaml 中的 api_key_path
  -> .codex/config.toml 中 provider env 的 OPENAI_API_KEY
```

base URL 读取优先级：

```text
OPENAI_BASE_URL 环境变量
  -> configs/tags_language_mvp.yaml 中的 base_url
  -> .codex/config.toml 中 model_providers.<provider>.base_url
  -> https://api.openai.com/v1
```

**Cache 接口**

topic cache：

```text
outputs/cache/topic_llm_cache.jsonl
```

作用：

- 避免同一 meeting/prompt/taxonomy 重复调用 API。
- 降低成本。
- 保证重跑时结果可复用。

正式 API 测试时，如果要避免命中过去的 fallback cache，可以使用：

```text
configs/tags_topic_gpt55_api_test.yaml
```

该配置关闭 cache，并关闭 fallback，用于确认真实 API 调用是否成功。

## 5. 配置说明

主配置文件：

```text
configs/tags_language_mvp.yaml
```

关键配置：

```yaml
tags:
  topic:
    enabled: true
    taxonomy_path: configs/topic_taxonomy_general.yaml
    schema_path: configs/topic_response_schema.json
    use_json_schema: false
    fallback: heuristic
    model:
      provider: openai_responses
      name: gpt-5.5
      api_key_path: api.txt
      model_provider: apifusion
      codex_config_path: /hpc_stor03/sjtu_home/huifei.wang/.codex/config.toml
      temperature: 0
      prompt_version: topic_hierarchical_v0.3.0
      timeout_sec: 180
    meeting:
      single_call_max_chars: 80000
      chunk_chars: 60000
    cache:
      enabled: true
      path: outputs/cache/topic_llm_cache.jsonl
```

topic taxonomy：

```text
configs/topic_taxonomy_general.yaml
```

当前大类包括：

- `academic_research`
- `technology_engineering`
- `business_management`
- `law_policy_government`
- `health_medicine`
- `education_training`
- `culture_media_arts`
- `news_current_events`
- `daily_life_social`
- `customer_service_support`
- `meeting_workflow`
- `other`

每个大类下面有若干小类，例如：

```yaml
academic_research:
  minors:
    - mathematics
    - physics
    - computer_science
    - philosophy
    - linguistics
```

## 6. 常用命令

以下命令都在项目根目录执行：

```bash
cd /hpc_stor03/sjtu_home/huifei.wang/sure-tagger
```

### 6.1 一条命令跑完整会议级 pipeline

默认只跑确定性 tags，不调用大模型：

```bash
python3 -m sure_tagger.cli run-meeting-pipeline \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output-dir outputs/ami \
  --run-name full.deterministic
```

如果要包含 topic，并且先用 heuristic 离线验证：

```bash
python3 -m sure_tagger.cli run-meeting-pipeline \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output-dir outputs/ami \
  --run-name full.topic.heuristic \
  --include-topic \
  --topic-provider heuristic
```

如果要调用配置中的 `gpt-5.5` 跑 topic：

```bash
python3 -m sure_tagger.cli run-meeting-pipeline \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output-dir outputs/ami \
  --run-name full.topic.gpt55 \
  --include-topic
```

参数说明：

| 参数 | 示例值 | 是否必需 | 作用 |
| --- | --- | --- | --- |
| `--dataset` | `ami` | 是 | 指定数据集 adapter。当前支持 `ami`。 |
| `--root` | `/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI` | 是 | 原始数据集根目录。 |
| `--output-dir` | `outputs/ami` | 否 | 所有中间产物、最终 tags、报告和 QA 文件的输出目录。 |
| `--output` | `outputs/ami/meeting_tags.full.jsonl` | 否 | 最终 meeting tag 输出路径。不传时自动生成 `meeting_tags.<run-name>.jsonl`。 |
| `--config` | `configs/tags_language_mvp.yaml` | 否 | tag 配置文件，默认使用当前 MVP 配置。 |
| `--meetings` | `ES2002a,ES2005a` | 否 | 只处理指定会议。多个 meeting ID 用英文逗号分隔。不传则处理全部会议。 |
| `--run-name` | `full.topic.heuristic` | 否 | 本次运行名称，会用于自动生成文件名和 `run_id`。 |
| `--tags` | `language,word_count` | 否 | 手动指定要跑的 tags。不传时默认跑 `language,word_count,punctuation,filler,repetition`。 |
| `--include-topic` | 无 | 否 | 在默认确定性 tags 之外追加 `topic`。显式使用该参数才会跑 topic。 |
| `--topic-provider` | `heuristic` | 否 | 临时覆盖 topic provider。用 `heuristic` 可避免调用 API；不传则按 config 使用 `openai_responses`。 |
| `--dry-run` | 无 | 否 | 把 topic provider 临时设为 `dry_run`，用于检查流程。 |
| `--segment-limit` | `100` | 否 | 截断底层 segment，只用于 parser 调试。正式会议级 tag 不建议使用。 |
| `--meeting-limit` | `10` | 否 | 聚合后最多处理多少场会议，用于小规模测试。 |
| `--qa-sample-size` | `20` | 否 | 输出多少场会议用于 QA 抽样。默认 `20`。 |
| `--skip-qa` | 无 | 否 | 不生成 QA 抽样文件。 |
| `--run-id` | `ami_full_v1` | 否 | 写入 tag result 的运行 ID。不传时使用 `--run-name`。 |

该命令会自动生成：

```text
segment_manifest.<run-name>.jsonl
meeting_manifest.<run-name>.jsonl
meeting_tags.<run-name>.jsonl
meeting_qa_samples.<run-name>.jsonl
pipeline.<run-name>.report.json
```

### 6.2 生成单场会议的 segment manifest

用于快速验证 AMI adapter，并为后续会议聚合提供完整的单场会议 segment。注意：如果目标是整场会议打 tag，这一步不要用 `--limit 20` 截断同一场会议。

```bash
python3 -m sure_tagger.cli build-manifest \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --meetings ES2002a \
  --output outputs/ami/segment_manifest.es2002a.jsonl \
  --bad-samples outputs/ami/bad_samples.build_segment_manifest.es2002a.jsonl \
  --report outputs/ami/build_segment_manifest.es2002a.report.json
```

参数说明：

| 参数 | 示例值 | 是否必需 | 作用 |
| --- | --- | --- | --- |
| `--dataset` | `ami` | 是 | 指定数据集 adapter。当前 pipeline 已实现 `ami`。 |
| `--root` | `/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI` | 是 | 指定原始 AMI 数据集根目录，程序会从这里读取 `words/`、`segments/` 等原始文件。 |
| `--meetings` | `ES2002a` | 否 | 只处理指定 meeting ID。多个 meeting 用英文逗号分隔，例如 `ES2002a,ES2002b`。不传则处理全部 meeting。 |
| `--limit` | `20` | 否 | 最多输出多少条 segment，只用于调试 parser。正式 meeting tag 不建议使用。 |
| `--output` | `outputs/ami/segment_manifest.es2002a.jsonl` | 是 | segment manifest 输出路径，每行是一条 AMI segment。 |
| `--bad-samples` | `outputs/ami/bad_samples.build_segment_manifest.es2002a.jsonl` | 否 | 解析失败或异常 segment 的输出路径，用于排查坏数据。 |
| `--report` | `outputs/ami/build_segment_manifest.es2002a.report.json` | 否 | 构建统计报告路径，包含 records、bad records、warnings 等信息。 |

### 6.3 聚合单场会议 manifest

```bash
python3 -m sure_tagger.cli build-meeting-manifest \
  --manifest outputs/ami/segment_manifest.es2002a.jsonl \
  --output outputs/ami/meeting_manifest.es2002a.jsonl \
  --bad-samples outputs/ami/bad_samples.build_meeting_manifest.es2002a.jsonl \
  --report outputs/ami/build_meeting_manifest.es2002a.report.json
```

参数说明：

| 参数 | 示例值 | 是否必需 | 作用 |
| --- | --- | --- | --- |
| `--manifest` | `outputs/ami/segment_manifest.es2002a.jsonl` | 是 | 输入 segment manifest，通常由 `build-manifest` 生成。 |
| `--meetings` | `ES2002a` | 否 | 只聚合指定 meeting ID。输入文件已经过滤时可以不传。 |
| `--limit` | `1` | 否 | 最多输出多少场会议，用于小规模调试。 |
| `--output` | `outputs/ami/meeting_manifest.es2002a.jsonl` | 是 | meeting manifest 输出路径，每行是一整场会议。 |
| `--bad-samples` | `outputs/ami/bad_samples.build_meeting_manifest.es2002a.jsonl` | 否 | 聚合过程中异常记录的输出路径。 |
| `--report` | `outputs/ami/build_meeting_manifest.es2002a.report.json` | 否 | 聚合统计报告路径，包含输入 segment 数和输出 meeting 数。 |

### 6.4 生成完整 AMI segment manifest

```bash
python3 -m sure_tagger.cli build-manifest \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output outputs/ami/segment_manifest.full.jsonl \
  --bad-samples outputs/ami/bad_samples.build_segment_manifest.full.jsonl \
  --report outputs/ami/build_segment_manifest.full.report.json
```

当前已验证结果：

```text
records: 93637
segment_files: 687
bad_records: 0
warnings: 0
```

### 6.5 聚合完整 AMI meeting manifest

```bash
python3 -m sure_tagger.cli build-meeting-manifest \
  --manifest outputs/ami/segment_manifest.full.jsonl \
  --output outputs/ami/meeting_manifest.full.jsonl \
  --bad-samples outputs/ami/bad_samples.build_meeting_manifest.full.jsonl \
  --report outputs/ami/build_meeting_manifest.full.report.json
```

### 6.6 对会议跑确定性语言 tags

确定性 tags 不需要 API。

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --config configs/tags_language_mvp.yaml \
  --tags language,word_count,punctuation,filler,repetition \
  --output outputs/ami/meeting_language_tags.full.deterministic.jsonl \
  --bad-samples outputs/ami/bad_samples.tag.meeting.full.deterministic.jsonl \
  --report outputs/ami/tag.meeting.full.deterministic.report.json
```

参数说明：

| 参数 | 示例值 | 是否必需 | 作用 |
| --- | --- | --- | --- |
| `--manifest` | `outputs/ami/meeting_manifest.full.jsonl` | 是 | 指定要打 tag 的 meeting manifest 输入文件。 |
| `--config` | `configs/tags_language_mvp.yaml` | 否，建议传 | 指定 tag 配置文件，控制启用哪些 tag、topic taxonomy、模型配置、上下文窗口等。 |
| `--tags` | `language,word_count,punctuation,filler,repetition` | 否，建议传 | 指定本次要运行的 tag 名称，多个 tag 用英文逗号分隔。不传时按 config 中 enabled 的 tag 运行。 |
| `--output` | `outputs/ami/meeting_language_tags.full.deterministic.jsonl` | 是 | tag 结果输出路径，每行对应一场会议的所有 tag 结果。 |
| `--bad-samples` | `outputs/ami/bad_samples.tag.meeting.full.deterministic.jsonl` | 否 | tag 过程中异常会议的输出路径。 |
| `--report` | `outputs/ami/tag.meeting.full.deterministic.report.json` | 否 | tag 运行统计报告路径，包含处理数量、失败数量、标签分布等。 |
| `--limit` | `20` | 否 | 最多处理多少场会议，常用于 topic 抽样测试。不传则处理全部 manifest。 |
| `--run-id` | `ami_topic_sample20_v1` | 否 | 给本次运行写入一个可追踪 ID，方便后续比较不同批次结果。 |
| `--topic-provider` | `heuristic` | 否 | 临时覆盖 topic 的 provider。常用 `heuristic` 做离线测试；不传则使用 config 里的 `openai_responses`。 |
| `--dry-run` | 无 | 否 | 不调用大模型，把 topic provider 临时设为 `dry_run`，用于检查流程是否能跑通。 |

当前已验证结果：

```text
records_seen: 171
records_written: 171
bad_records: 0
```

### 6.7 抽样跑会议 topic，不调用 API

用于验证 meeting-level topic schema、taxonomy、聚合文本和 fallback。

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --config configs/tags_language_mvp.yaml \
  --tags topic \
  --topic-provider heuristic \
  --limit 20 \
  --output outputs/ami/meeting_language_tags.topic.heuristic.sample20.jsonl \
  --report outputs/ami/tag.meeting.topic.heuristic.sample20.report.json
```

### 6.8 抽样调用 gpt-5.5 跑会议 topic

默认使用 `configs/tags_language_mvp.yaml` 中的 `api_key_path: api.txt` 读取 key，并从 `.codex/config.toml` 读取内部网关地址。一般不需要手动 `export`。

如果要临时覆盖 key 或接口地址，可以设置环境变量：

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://api.openai.com/v1
```

运行 20 条抽样：

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --config configs/tags_language_mvp.yaml \
  --tags topic \
  --limit 20 \
  --output outputs/ami/meeting_language_tags.topic.gpt55.sample20.jsonl \
  --bad-samples outputs/ami/bad_samples.tag.meeting.topic.gpt55.sample20.jsonl \
  --report outputs/ami/tag.meeting.topic.gpt55.sample20.report.json
```

确认抽样质量后再扩大规模。现在 `--limit 20` 表示 20 场会议，不是 20 个 segment。

### 6.9 全量跑会议 topic

确认 API、费用、速率和抽样质量后再执行：

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --config configs/tags_language_mvp.yaml \
  --tags topic \
  --output outputs/ami/meeting_language_tags.topic.gpt55.full.jsonl \
  --bad-samples outputs/ami/bad_samples.tag.meeting.topic.gpt55.full.jsonl \
  --report outputs/ami/tag.meeting.topic.gpt55.full.report.json
```

### 6.10 生成 QA 抽样文件

```bash
python3 -m sure_tagger.cli inspect \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --tags-file outputs/ami/meeting_language_tags.full.deterministic.jsonl \
  --sample-size 20 \
  --output outputs/ami/meeting_qa_samples.20.jsonl
```

参数说明：

| 参数 | 示例值 | 是否必需 | 作用 |
| --- | --- | --- | --- |
| `--manifest` | `outputs/ami/meeting_manifest.full.jsonl` | 是 | 指定 meeting manifest，用来读取整场会议文本、时间、speaker、来源等信息。 |
| `--tags-file` | `outputs/ami/meeting_language_tags.full.deterministic.jsonl` | 是 | 指定已经生成的会议级 tag 结果文件，用来和 manifest 合并。 |
| `--sample-size` | `20` | 否 | 抽取多少场会议用于人工 QA。默认值是 `100`。 |
| `--output` | `outputs/ami/meeting_qa_samples.20.jsonl` | 是 | QA 抽样输出路径，每行同时包含 meeting manifest 和对应 tags。 |

## 7. 输出文件说明

常见输出：

```text
outputs/ami/segment_manifest.full.jsonl
outputs/ami/meeting_manifest.full.jsonl
outputs/ami/meeting_tags.full.deterministic.jsonl
outputs/ami/meeting_language_tags.full.deterministic.jsonl
outputs/ami/meeting_language_tags.topic.gpt55.sample20.jsonl
outputs/ami/bad_samples.*.jsonl
outputs/ami/*.report.json
outputs/ami/meeting_qa_samples.20.jsonl
outputs/ami/qa_report.md
```

含义：

- `segment_manifest.*.jsonl`: 底层 segment 解析结果。
- `meeting_manifest.*.jsonl`: 最终会议级 tag 输入，一行一场会议。
- `meeting_tags.*.jsonl`: `run-meeting-pipeline` 一条命令生成的会议级 tag 结果。
- `meeting_language_tags.*.jsonl`: 会议级 tag 结果。
- `bad_samples.*.jsonl`: 失败样本，不影响主流程。
- `*.report.json`: 运行统计。`pipeline.*.report.json` 是一条命令总报告。
- `meeting_qa_samples.*.jsonl`: meeting manifest 和 tags 合并后的人工检查样本。
- `qa_report.md`: 当前 AMI 验证报告。

## 8. 测试

运行 smoke tests：

```bash
python3 -m unittest discover -s tests -v
```

当前已验证：

```text
Ran 9 tests
OK
```

测试覆盖：

- AMI `href` 展开。
- tokenizer 和标点统计。
- manifest schema。
- segment 到 meeting manifest 聚合。
- topic taxonomy 校验。
- topic chunk split 和 chunk merge。
- topic schema 开关。
- `run-meeting-pipeline` 默认 tag 选择。

## 9. 最近 API 抽样验证

2026-07-22 使用 `gpt-5.5` 对固定 seed 抽样的 20 场 AMI meeting 跑过真实 topic API，并补齐其他 deterministic tags。

产物：

```text
outputs/ami/meeting_tags.random20.gpt55.fixed_schema.20260722_213010.all_tags.jsonl
outputs/ami/tag.meeting.random20.gpt55.fixed_schema.20260722_213010.report.json
```

验证结果：

```text
records_written: 20
bad_records: 0
topic llm_call_count: 每场 1 次
language: en = 20
```

topic 分布：

| topic | 数量 |
| --- | ---: |
| `technology_engineering / product_design` | 19 |
| `technology_engineering / software_engineering` | 1 |

其他 tag 统计：

| 指标 | min | max | avg |
| --- | ---: | ---: | ---: |
| `word_count` | 2063 | 8573 | 5865.25 |
| `punctuation_count` | 482 | 2078 | 1343.35 |
| `filler_count` | 124 | 897 | 525.70 |
| `repetition_count` | 29 | 315 | 162.05 |

这个结果符合 AMI 样板数据特点：大多数 scenario meeting 都围绕遥控器产品设计，非 scenario 的 `EN2009b` 更偏实验软件和工具讨论，因此落到 `software_engineering`。

## 10. 当前限制

1. `language` 当前是 Unicode script heuristic，不是 fastText/CLD3。AMI 英文数据足够验证流程，但生产建议接入更强 LID。
2. 当前 `apifusion` 网关对 Responses API 的 `text.format=json_schema` 返回 `502 Upstream request failed`；pipeline 已默认关闭 `use_json_schema`，改用 `json_object` 请求并在本地校验 taxonomy。
3. `topic` fallback 是启发式，只用于离线工程验证，不应当作为最终高质量 topic 标签。
4. AMI 当前只处理音频和语言层 XML 标注，没有处理视频。
5. `single_call_max_chars` 是字符级保守阈值，不是严格 token 计数；如果后续确认模型上下文窗口更大，可以调高。
6. 输出文件可能较大。当前 full AMI 输出目录约数百 MB。

## 11. 新数据集接入方式

接入新数据集时，不需要重写 tag tools，只需要新增 dataset adapter。

新 adapter 要输出同样的 manifest schema：

```text
corpus.dataset_name
sample.sample_id
sample.audio.path
sample.audio.start_sec
sample.audio.end_sec
sample.text.transcript
sample.native_metadata
sample.provenance
```

建议步骤：

1. 在 `sure_tagger/datasets/` 下新增 `<dataset>.py`。
2. 实现数据集原始结构到 manifest 的转换。
3. 在 `sure_tagger/cli.py` 的 `build-manifest` 分支注册该 dataset。
4. 确保 segment manifest 中有稳定的 `meeting_id`。
5. 用 `run-meeting-pipeline` 先跑一个 meeting ID。
6. 抽样跑 meeting topic。
7. 人工 QA 后再全量跑。

## 12. 推荐执行顺序

第一次完整执行建议：

```bash
# 1. 单场会议，不调用 API
python3 -m sure_tagger.cli run-meeting-pipeline --dataset ami --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI --meetings ES2002a --run-name es2002a.deterministic

# 2. 单场会议 topic heuristic，不调用 API
python3 -m sure_tagger.cli run-meeting-pipeline --dataset ami --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI --meetings ES2002a --run-name es2002a.topic.heuristic --include-topic --topic-provider heuristic

# 3. 使用 api.txt 中的 API key，单场会议 topic gpt-5.5
python3 -m sure_tagger.cli run-meeting-pipeline --dataset ami --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI --meetings ES2002a --run-name es2002a.topic.gpt55 --include-topic

# 4. 全量 deterministic tags，不调用 API
python3 -m sure_tagger.cli run-meeting-pipeline --dataset ami --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI --run-name full.deterministic
```

topic 全量应在会议级抽样 QA 通过后再执行。
