# 语言层 Tagging Pipeline 可执行计划

## 1. 目标

搭建一个面向 ASR 会议级数据的语言层 tagging pipeline。输入仍使用统一的 `corpus + sample(audio, text, metadata, provenance)` 容器，但最终 tag 粒度是一整场会议，而不是单个 segment。输出是可追溯、可复现、可增量重跑的会议级语言层 tags。

语言层 pipeline 不预设数据领域。金融只是一个可能场景，实际输入可能来自会议、课堂、访谈、客服、播客、学术讨论、医疗、法律、工程、日常对话等多种数据源。因此 topic tag 必须使用通用、可扩展的层级标签体系，而不是绑定到单一行业。

AMI 数据集作为第一个样板数据集，用来验证：

- 能否从真实复杂数据集结构中抽取底层 segment manifest。
- 能否把同一 `meeting_id` 下的所有 segment 聚合成 meeting manifest。
- 能否在 meeting 粒度上稳定生成语言层 tags。
- 能否把确定性脚本、文本模型、LLM/API 类工具纳入同一个 pipeline。

当前语言层 MVP tags：

- `language`
- `word_count`
- `punctuation`
- `filler`
- `repetition`
- `topic`

其中 `topic` 使用层级结构：

- `major_topic`: 大类，例如 `academic_research`。
- `minor_topic`: 小类，例如 `computer_science`。
- `topic_keywords`: 支撑判断的关键词。
- `proper_nouns`: 支撑判断的专有名词，例如机构、产品、理论、人物、地点、论文名、课程名等。

不在 MVP 范围内：

- 音频层 tags。
- ASR 解码或标点恢复。
- 音频切片物理落盘。
- 视频、多模态手势标注处理。

## 2. 成功标准

完成后应满足：

- 能从 AMI 原始目录生成 `segment_manifest.jsonl`。
- 能从 `segment_manifest.jsonl` 聚合生成 `meeting_manifest.jsonl`。
- 每条 meeting manifest 记录都有稳定 `sample_id = AMI:{meeting_id}`、整场会议音频路径、起止时间、转录文本、speaker-labeled 转录、元数据和 provenance。
- 能对 meeting manifest 中每场会议生成语言层 tag 结果。
- 每个 tag 结果都包含 `value`、`confidence`、`method`、`tool_version`、`reliability`。
- `topic` 必须输出会议级大类、小类、关键词、专有名词和证据范围。
- `topic` 在整场会议文本不超过上下文预算时只调用一次大模型；超长会议才分块调用，并本地合并。
- 同一输入和同一配置重复运行，确定性 tags 输出一致。
- 非确定性或大模型类 tags 记录模型名、prompt/config 版本、上下文范围、cache key。
- 失败样本不会中断全局任务，会进入 `bad_samples.jsonl`。
- 最终生成 `run_report.json`，包含样本数、成功数、失败数、tag 分布和运行配置。

## 3. 目录约定

项目根目录：

```text
/hpc_stor03/sjtu_home/huifei.wang/sure-tagger
```

AMI 数据路径：

```text
/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI
```

建议新增代码结构：

```text
sure_tagger/
  __init__.py
  cli.py
  schemas.py
  datasets/
    __init__.py
    ami.py
  text/
    __init__.py
    normalize.py
    tokenizer.py
    context.py
    key_terms.py
  llm/
    __init__.py
    client.py
    cache.py
    prompts.py
  tags/
    __init__.py
    language.py
    word_count.py
    punctuation.py
    filler.py
    repetition.py
    topic.py
  io/
    __init__.py
    jsonl.py
  report.py
configs/
  ami.yaml
  tags_language_mvp.yaml
  topic_taxonomy_general.yaml
outputs/
  ami/
```

如果暂时不搭完整 Python package，可以先以脚本形式落地，但输入输出格式必须和本文档保持一致。

## 4. 数据接口

### 4.1 Manifest 输入结构

每行一个 JSON sample：

```json
{
  "corpus": {
    "dataset_name": "AMI",
    "source_urls": {
      "article": [],
      "github": [],
      "huggingface": [],
      "dataset_card": []
    },
    "native_metadata": {
      "annotation_release": "AMI Manual Annotations 1.7"
    }
  },
  "sample": {
    "sample_id": "AMI:ES2002a:A:ES2002a.sync.4",
    "audio": {
      "path": "/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI/amicorpus-Mix-Headset/ES2002a/audio/ES2002a.Mix-Headset.wav",
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
      "source_words_file": "annotations/words/ES2002a.A.words.xml",
      "source_segments_file": "annotations/segments/ES2002a.A.segments.xml",
      "nonword_events": []
    },
    "provenance": {
      "source_path": "/hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI/amicorpus/annotations/segments/ES2002a.A.segments.xml",
      "source_split": ""
    }
  }
}
```

### 4.2 Tag 输出结构

每行一个 JSON sample tagging result。最终 tag 文件使用 meeting-level `sample_id`，segment-level 示例只用于说明底层 manifest 结构。

```json
{
  "sample_id": "AMI:ES2002a",
  "tags": {
    "language": {
      "value": "en",
      "confidence": 0.99,
      "method": "unicode_script_heuristic",
      "tool_version": "language_v0.1.0",
      "reliability": "L1"
    },
    "word_count": {
      "value": 11,
      "details": {
        "character_count": 62,
        "token_count": 13
      },
      "confidence": 1.0,
      "method": "deterministic_tokenizer",
      "tool_version": "word_count_v0.1.0",
      "reliability": "L0"
    },
    "topic": {
      "value": {
        "major_topic": "technology_engineering",
        "minor_topic": "product_design"
      },
      "confidence": 0.84,
      "details": {
        "taxonomy": "general_topic_v0.1.0",
        "topic_keywords": ["remote control", "design", "industrial designer"],
        "proper_nouns": [],
        "evidence_scope": "meeting",
        "evidence_sample_count": 843
      },
      "method": "llm_hierarchical_classification",
      "tool_version": "topic_v0.3.0",
      "reliability": "L2"
    }
  },
  "pipeline": {
    "run_id": "20260721_ami_language_mvp",
    "config_hash": "",
    "created_at": "2026-07-21T00:00:00+08:00"
  }
}
```

### 4.3 错误样本结构

```json
{
  "sample_id": "AMI:ES2002a:A:ES2002a.sync.4",
  "stage": "build_manifest",
  "error_type": "missing_word_id",
  "message": "Cannot resolve ES2002a.A.words999",
  "source_path": ".../ES2002a.A.segments.xml"
}
```

## 5. AMI Adapter 设计

### 5.1 样本粒度

使用两级粒度：

- `segment`: 底层解析粒度。AMI adapter 从 `segments/*.segments.xml` 和 `words/*.words.xml` 恢复每个话语片段。
- `meeting`: 最终打标粒度。pipeline 按 `meeting_id` 把所有 segment 聚合成一条 meeting record，然后对整场会议打 tag。

理由：

- `words` 粒度太细，很多 topic/language 标签不稳定。
- `segments` 适合做 XML 解析、时间戳恢复和 provenance 追踪，但不适合作为最终 topic 打标单位。
- 任务要求是一整场会议一个 tag，因此最终输出必须是 meeting-level。
- meeting-level topic 可以显著减少 LLM 调用次数；正常情况下每场会议只调用一次模型，超长会议才分块调用。

### 5.2 输入文件

主要输入：

```text
AMI/amicorpus/annotations/words/*.words.xml
AMI/amicorpus/annotations/segments/*.segments.xml
AMI/amicorpus-Mix-Headset/<meeting_id>/audio/<meeting_id>.Mix-Headset.wav
AMI/amicorpus/beamformed/<meeting_id>/<meeting_id>_MDM8.wav
AMI/amicorpus/annotations/AMI-metadata.xml
```

音频路径优先级：

1. `amicorpus-Mix-Headset/<meeting_id>/audio/<meeting_id>.Mix-Headset.wav`
2. `amicorpus/beamformed/<meeting_id>/<meeting_id>_MDM8.wav`
3. `amicorpus/<meeting_id>/audio/<meeting_id>.Headset-<n>.wav`

MVP 使用第 1 项即可。找不到时再 fallback。

### 5.3 解析步骤

1. 扫描 `words/*.words.xml`。
2. 解析每个 `w` 节点：
   - `nite:id`
   - `starttime`
   - `endtime`
   - text
   - attributes such as `punc`, `mispronounced`
3. 解析 `vocalsound`、`nonvocalsound` 等非词事件，保存到 `nonword_events`。
4. 扫描 `segments/*.segments.xml`。
5. 解析每个 `segment`：
   - `nite:id`
   - `transcriber_start`
   - `transcriber_end`
   - child `href`
6. 展开 `href`：
   - 单个词：`#id(ES2002a.A.words49)`
   - 范围：`#id(ES2002a.A.words0)..id(ES2002a.A.words12)`
7. 用词序列恢复 transcript。
8. 用 segment 时间作为 `start_sec/end_sec`，缺失时 fallback 到词级首尾时间。
9. 生成 `sample_id = AMI:{meeting_id}:{speaker_id}:{segment_id}`。
10. 写出 `manifest.jsonl`。

### 5.4 AMI 已知问题处理

AMI README 中说明：

- `IS1002a` 和 `IS1005d` 因音频问题从 corpus 中移除。
- 少量词没有 forced alignment timing。
- `TS3009c`, `EN2002a`, `EN2002c`, `EN2003a` 可能存在 timing 不完整或不准确。

处理策略：

- 对缺失 timing 的 segment 记录 warning。
- 如果 transcript 可恢复但时间不可用，保留文本样本，并将 `audio.start_sec/end_sec` 设为 `null`。
- 如果词 id 无法解析，样本进入 `bad_samples.jsonl`。
- `run_report.json` 统计 warning 数量。

## 6. 语言层 Tags 定义

### 6.1 `language`

目标：识别 transcript 的语言。

方法：

- 先做 Unicode script 统计。
- 再使用 fastText LID、CLD3 或 langid。
- 文本过短时降低 confidence。

输出字段：

```json
{
  "value": "en",
  "confidence": 0.99,
  "details": {
    "script_distribution": {"latin": 1.0},
    "text_length": 62
  },
  "method": "unicode_script_heuristic",
  "tool_version": "language_v0.1.0",
  "reliability": "L1"
}
```

验收：

- AMI 大多数样本输出 `en`。
- 空文本输出 `unknown`。
- 少于 3 个有效词的样本 confidence 不应盲目给满。

### 6.2 `word_count`

目标：统计文本长度。

方法：

- 英文按 word tokenizer 统计。
- 中文后续接 jieba 或其他分词器。
- 同时输出字符数和 token 数。

输出字段：

```json
{
  "value": 11,
  "details": {
    "word_count": 11,
    "character_count": 62,
    "token_count": 13
  },
  "confidence": 1.0,
  "method": "deterministic_tokenizer",
  "tool_version": "word_count_v0.1.0",
  "reliability": "L0"
}
```

验收：

- 标点不计入 word count。
- `I'm` 作为一个词还是两个词必须由 tokenizer 配置固定。
- 空文本输出 0。

### 6.3 `punctuation`

目标：统计已有 transcript 标点情况，不做标点恢复。

方法：

- Unicode/regex 统计标点。
- 区分 terminal punctuation 和 inner punctuation。

输出字段：

```json
{
  "value": {
    "punctuation_count": 2,
    "has_terminal_punctuation": true
  },
  "details": {
    "comma": 1,
    "period": 1,
    "question_mark": 0,
    "exclamation_mark": 0
  },
  "confidence": 1.0,
  "method": "unicode_punctuation_counter",
  "tool_version": "punctuation_v0.1.0",
  "reliability": "L0"
}
```

验收：

- 不根据模型补标点。
- 原文没有标点则输出 0。

### 6.4 `filler`

目标：统计填充词和语气词，不与 repetition 混用。

默认英文词表：

```text
uh, um, erm, er, ah, oh, hmm, mm, yeah
```

注意：

- `yeah` 在不同任务中可能是普通词，也可能近似 backchannel。先保留在词表中，但在配置里可关闭。
- AMI XML 中 `vocalsound type="laugh"` 不算 filler，进入 `nonword_events`。

输出字段：

```json
{
  "value": 1,
  "details": {
    "filler_count": 1,
    "filler_ratio": 0.09,
    "items": [{"token": "Um", "normalized": "um"}]
  },
  "confidence": 1.0,
  "method": "lexicon_rule",
  "tool_version": "filler_v0.1.0",
  "reliability": "L0"
}
```

验收：

- 大小写不影响统计。
- 词表版本写入结果。
- 空文本输出 0。

### 6.5 `repetition`

目标：检测连续重复词和短 ngram 重复。

方法：

- 连续 unigram 重复：`I I think`
- 连续 bigram/trigram 重复：`we need we need`
- 不把 filler 直接等同于 repetition。

输出字段：

```json
{
  "value": {
    "has_repetition": true,
    "repetition_count": 1
  },
  "details": {
    "repeated_spans": [
      {"type": "unigram", "text": "I I", "start_token": 0, "end_token": 2}
    ]
  },
  "confidence": 1.0,
  "method": "token_ngram_rule",
  "tool_version": "repetition_v0.1.0",
  "reliability": "L0"
}
```

验收：

- 连续重复必须被识别。
- 非连续同词反复暂不作为 MVP 硬规则。
- 输出 repeated spans 便于人工检查。

### 6.6 `topic`

目标：给样本打层级主题标签，覆盖通用领域，并为后续垂直领域扩展保留接口。

原则：

- `topic` 必须基于可信 transcript。
- 短样本不能只看当前 sample，要使用上下文。
- topic taxonomy 必须版本化。
- 默认使用通用层级 taxonomy，不绑定金融或 AMI。
- 输出必须包含一个大标签和一个小标签。
- 专有名词可以作为判断依据，但不直接替代 `major_topic/minor_topic`。
- 大模型/API 可以用于 topic 判断、关键词抽取和专有名词抽取，但必须记录模型、prompt 版本和 cache key。

输出结构：

```json
{
  "value": {
    "major_topic": "academic_research",
    "minor_topic": "computer_science"
  },
  "confidence": 0.87,
  "details": {
    "taxonomy": "general_topic_v0.1.0",
    "topic_keywords": ["speech recognition", "tagging pipeline", "taxonomy"],
    "proper_nouns": ["AMI", "NITE", "OpenAI"],
    "evidence_scope": "meeting_window",
    "evidence_sample_count": 8,
    "reason_short": "The segment and context discuss ASR data tagging and pipeline design."
  },
  "method": "llm_hierarchical_classification",
  "tool_version": "topic_v0.3.0",
  "reliability": "L2"
}
```

### 6.6.1 通用层级 taxonomy

第一版 taxonomy 使用两层结构：

- `major_topic`: 粗粒度大类。
- `minor_topic`: 大类下面的小类。

大类必须覆盖常见 ASR 数据来源，包括会议、课程、访谈、播客、客服、讲座、新闻和日常对话。

建议 `general_topic_v0.1.0`：

```yaml
academic_research:
  description: 学术、科研、理论讨论、论文、课程中的专业知识
  minors:
    - mathematics
    - physics
    - chemistry
    - biology
    - computer_science
    - engineering
    - medicine
    - economics
    - psychology
    - philosophy
    - linguistics
    - history
    - interdisciplinary

technology_engineering:
  description: 技术、工程、产品、系统、软件硬件实现
  minors:
    - artificial_intelligence
    - software_engineering
    - data_science
    - cybersecurity
    - hardware
    - robotics
    - telecommunications
    - product_design
    - user_experience
    - manufacturing

business_management:
  description: 商业、组织管理、市场、运营、项目推进
  minors:
    - strategy
    - marketing_sales
    - finance_accounting
    - operations
    - human_resources
    - entrepreneurship
    - project_management
    - customer_success
    - procurement

law_policy_government:
  description: 法律、政策、政府、公共事务和合规
  minors:
    - law
    - regulation
    - public_policy
    - government_services
    - compliance
    - international_relations
    - public_safety

health_medicine:
  description: 医疗、健康、临床、公共卫生
  minors:
    - clinical_medicine
    - public_health
    - pharmacy
    - mental_health
    - fitness
    - nutrition
    - healthcare_operations

education_training:
  description: 教学、培训、考试、学习辅导
  minors:
    - lecture
    - tutorial
    - exam_preparation
    - classroom_discussion
    - language_learning
    - professional_training
    - mentoring

culture_media_arts:
  description: 文化、媒体、娱乐、艺术、人文表达
  minors:
    - literature
    - music
    - film_tv
    - gaming
    - visual_art
    - religion
    - media_production
    - pop_culture

news_current_events:
  description: 新闻、时事、社会事件和公共议题
  minors:
    - politics
    - economy
    - local_news
    - international_news
    - climate_environment
    - social_issues
    - breaking_news

daily_life_social:
  description: 日常生活、人际交流、家庭、消费和闲聊
  minors:
    - family
    - food
    - shopping
    - housing
    - travel_transportation
    - interpersonal_chat
    - personal_experience
    - small_talk

customer_service_support:
  description: 客服、售后、咨询、投诉、工单处理
  minors:
    - product_inquiry
    - troubleshooting
    - complaint
    - billing
    - account_support
    - appointment
    - refund_exchange

meeting_workflow:
  description: 会议组织过程，而不是会议讨论的业务主题本身
  minors:
    - agenda
    - scheduling
    - status_update
    - decision
    - action_item
    - brainstorming
    - coordination
    - opening_closing

other:
  description: 无法归入上述类别或信息不足
  minors:
    - unknown
    - insufficient_context
    - mixed_topics
    - non_speech
```

注意：

- `meeting_workflow` 只用于会议流程本身，例如开场、排期、行动项、决策记录。
- 如果会议中讨论的是遥控器设计，应标为 `technology_engineering/product_design`，不是 `meeting_workflow`。
- 如果样本只是 "okay", "yeah", "next" 这类低信息文本，应输出 `other/insufficient_context` 或使用上下文判断。

### 6.6.2 专有名词和关键词

topic 判断可以使用专有名词，但要把专有名词作为证据字段单独输出。

专有名词包括：

- 人名：`Albert Einstein`
- 组织：`OpenAI`, `Stanford University`
- 产品/系统：`CosyVoice`, `AMI Corpus`, `NITE`
- 理论/方法：`Transformer`, `Bayes theorem`
- 地点：`Shanghai`, `United States`
- 论文/书名/课程名：`Attention Is All You Need`
- 数据集/benchmark：`AMI`, `LibriSpeech`, `Common Voice`

关键词包括：

- 领域词：`speech recognition`, `remote control`, `budget`
- 任务词：`classification`, `summarization`, `debugging`
- 语义线索：`diagnosis`, `legal contract`, `course exam`

输出要求：

- `proper_nouns`: 去重后的专有名词列表。
- `topic_keywords`: 去重后的主题关键词列表。
- `reason_short`: 一句话解释，不超过 30 个英文词或 50 个中文字符。
- 专有名词抽取不要求 100% 完整，但不能凭空编造。

### 6.6.3 上下文构造

最终 topic 输入是一整场会议，因此默认不再对每个 segment 单独构造上下文窗口。meeting record 直接提供：

- `text.transcript`: 纯会议文本。
- `text.speaker_labeled_transcript`: 带时间戳和 speaker 的会议文本，优先用于 LLM prompt。
- `native_metadata.source_sample_count`: 该会议聚合了多少个 segment。
- `native_metadata.speaker_ids`: 该会议包含哪些 speaker。

默认策略：

1. 如果会议文本不超过 `single_call_max_chars`，一次调用大模型判断整场会议 topic。
2. 如果会议文本超过 `single_call_max_chars`，按 `chunk_chars` 切成多个 chunk，分别调用大模型。
3. chunk 结果在本地按 `chunk 字符数 * confidence` 加权投票，得到最终 `major_topic/minor_topic`。
4. 如果不同 chunk 明显包含多个主题，最终输出最主要主题，并在 `details.secondary_topics` 中保留次要主题。
5. 只有当输入仍是旧的 segment manifest 时，才使用 `speaker_window_text` 和 `meeting_window_text` 兼容旧流程。

### 6.6.4 大模型 topic tool

使用当前可用 API 做结构化输出。建议 prompt 固定为：

```text
You are a data tagging tool for ASR transcripts.
Classify the transcript into exactly one major_topic and one minor_topic
from the provided taxonomy. Extract topic_keywords and proper_nouns only
from the transcript/context. If evidence is insufficient, use
other/insufficient_context. Return strict JSON only.
```

输入给模型：

- taxonomy version 和可选标签列表。
- 当前 meeting transcript；如果输入仍是旧 segment manifest，才使用上下文窗口文本。
- 数据集元数据。
- 输出 schema。

模型输出必须经过本地结构和 taxonomy 校验：

- `major_topic` 必须在 taxonomy 中。
- `minor_topic` 必须属于该 `major_topic`。
- `confidence` 在 `[0, 1]`。
- `topic_keywords` 和 `proper_nouns` 必须是数组。
- 非法输出进入 retry；retry 仍失败进入 `bad_samples.jsonl`。

当前网关对 Responses API 的远端 `json_schema` 格式返回 `502 Upstream request failed`，所以默认使用 `json_object` 请求，并在本地完成上述校验。若后续确认网关支持，可把 `use_json_schema` 改为 `true`。

### 6.6.5 topic 质量分层

建议 reliability：

- `L0`: 无需模型的确定性标签，不适用于 topic。
- `L1`: 规则/embedding 分类器，taxonomy 固定，可复现。
- `L2`: 大模型结构化分类，使用 cache、本地结构校验和 taxonomy 校验。
- `L3`: 人工复核后的 topic。

AMI MVP 使用 `L2`，后续可用人工复核样本训练轻量分类器，把高频主题降到 `L1`。

验收：

- 每个 topic 结果都记录 taxonomy。
- 每个 topic 结果都记录 evidence scope。
- 每个 topic 结果都包含 `major_topic` 和 `minor_topic`。
- 每个 topic 结果都包含 `topic_keywords` 和 `proper_nouns` 字段。
- 低信息样本允许输出 `other/insufficient_context`。
- 大模型/API 调用必须支持 cache。
- 抽样检查时，topic 不应明显偏向 AMI 会议本身，应该优先识别实际讨论内容。

### 6.7 大模型/API 工具层

语言层允许使用当前可用 API 调用大模型，适用范围：

- `topic` 层级分类。
- `topic_keywords` 抽取。
- `proper_nouns` 抽取。
- 可选的 `language` 兜底判断。
- 可选的疑难样本解释和 QA 抽样。

实现约束：

- 所有大模型 tool 必须是独立模块，不能散落在业务逻辑里。
- 每次调用必须写入 `model`、`prompt_version`、`taxonomy/schema` 信息、`temperature`、`cache_key`。
- 默认 `temperature=0` 或接近 0。
- 必须启用 cache，同一输入不能重复花费 API。
- 必须支持 dry-run，只构造请求不发送。
- 必须支持 sample limit，先抽样跑再全量跑。
- 必须做本地结构校验和 taxonomy 合法性校验；远端 JSON Schema 作为可选能力。
- 大模型输出不能覆盖原始 transcript，只能作为 tag result。

API 环境变量：

```bash
export OPENAI_API_KEY=...
# 可选：如果使用兼容 OpenAI API 的内部网关
export OPENAI_BASE_URL=https://api.openai.com/v1
# 可选：覆盖配置中的模型名
export OPENAI_MODEL=gpt-5.5
```

MVP 默认使用 OpenAI Responses API provider：

```yaml
provider: openai_responses
name: gpt-5.5
```

如果没有 API key，topic tool 会记录 `llm_error` 并按配置 fallback 到 heuristic，用于验证 pipeline 其他部分；正式打标时应确保 API 调用成功，避免大量 topic 结果退化为 `L1` heuristic。

## 7. Pipeline 命令设计

### 7.1 一条命令执行全流程

推荐入口：

```bash
python3 -m sure_tagger.cli run-meeting-pipeline \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output-dir outputs/ami \
  --run-name full.deterministic
```

该命令自动执行：

1. 构建 `segment_manifest.<run-name>.jsonl`。
2. 聚合 `meeting_manifest.<run-name>.jsonl`。
3. 生成 `meeting_tags.<run-name>.jsonl`。
4. 生成 `meeting_qa_samples.<run-name>.jsonl`。
5. 写出 `pipeline.<run-name>.report.json` 总报告。

默认只跑确定性 tags，不调用大模型。如果要包含 topic：

```bash
python3 -m sure_tagger.cli run-meeting-pipeline \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --run-name full.topic.heuristic \
  --include-topic \
  --topic-provider heuristic
```

不传 `--topic-provider` 时，topic 按配置调用 `gpt-5.5`。

### 7.2 构建 segment manifest

```bash
python3 -m sure_tagger.cli build-manifest \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output outputs/ami/segment_manifest.full.jsonl \
  --bad-samples outputs/ami/bad_samples.build_segment_manifest.full.jsonl \
  --report outputs/ami/build_segment_manifest.full.report.json
```

产物：

```text
outputs/ami/segment_manifest.full.jsonl
outputs/ami/bad_samples.build_segment_manifest.full.jsonl
outputs/ami/build_segment_manifest.full.report.json
```

### 7.3 聚合 meeting manifest

```bash
python3 -m sure_tagger.cli build-meeting-manifest \
  --manifest outputs/ami/segment_manifest.full.jsonl \
  --output outputs/ami/meeting_manifest.full.jsonl \
  --bad-samples outputs/ami/bad_samples.build_meeting_manifest.full.jsonl \
  --report outputs/ami/build_meeting_manifest.full.report.json
```

### 7.4 运行会议级语言层 tags

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --config configs/tags_language_mvp.yaml \
  --output outputs/ami/meeting_language_tags.full.jsonl \
  --bad-samples outputs/ami/bad_samples.tag.meeting.full.jsonl \
  --report outputs/ami/tag.meeting.full.report.json
```

### 7.5 只重跑某些 tags

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --tags language,word_count,punctuation \
  --output outputs/ami/meeting_language_tags.basic.jsonl
```

### 7.6 抽样 QA

```bash
python3 -m sure_tagger.cli inspect \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --tags-file outputs/ami/meeting_language_tags.full.jsonl \
  --sample-size 100 \
  --output outputs/ami/meeting_qa_samples.jsonl
```

## 8. 配置文件建议

`configs/tags_language_mvp.yaml`：

```yaml
run:
  run_name: ami_language_mvp
  random_seed: 42
  cache_dir: outputs/cache

tags:
  language:
    enabled: true
    method: unicode_script_heuristic
    min_chars_for_confident_prediction: 10

  word_count:
    enabled: true
    tokenizer: simple_multilingual_v0
    contractions: keep

  punctuation:
    enabled: true

  filler:
    enabled: true
    lexicon_version: filler_en_v0
    words:
      - uh
      - um
      - erm
      - er
      - ah
      - oh
      - hmm
      - mm
      - yeah

  repetition:
    enabled: true
    max_ngram: 3
    consecutive_only: true

  topic:
    enabled: true
    method: llm_hierarchical_classification
    taxonomy: general_topic_v0.1.0
    taxonomy_path: configs/topic_taxonomy_general.yaml
    schema_path: configs/topic_response_schema.json
    use_json_schema: false
    model:
      provider: openai_responses
      name: gpt-5.5
      temperature: 0
      prompt_version: topic_hierarchical_v0.3.0
    context:
      meeting_window_sec: 120
      speaker_neighbor_segments: 3
      max_context_chars: 6000
    unknown_confidence_threshold: 0.5
    cache:
      enabled: true
      path: outputs/cache/topic_llm_cache.jsonl
```

`configs/topic_taxonomy_general.yaml`：

```yaml
version: general_topic_v0.1.0
labels:
  academic_research:
    description: 学术、科研、理论讨论、论文、课程中的专业知识
    minors:
      - mathematics
      - physics
      - chemistry
      - biology
      - computer_science
      - engineering
      - medicine
      - economics
      - psychology
      - philosophy
      - linguistics
      - history
      - interdisciplinary

  technology_engineering:
    description: 技术、工程、产品、系统、软件硬件实现
    minors:
      - artificial_intelligence
      - software_engineering
      - data_science
      - cybersecurity
      - hardware
      - robotics
      - telecommunications
      - product_design
      - user_experience
      - manufacturing

  business_management:
    description: 商业、组织管理、市场、运营、项目推进
    minors:
      - strategy
      - marketing_sales
      - finance_accounting
      - operations
      - human_resources
      - entrepreneurship
      - project_management
      - customer_success
      - procurement

  law_policy_government:
    description: 法律、政策、政府、公共事务和合规
    minors:
      - law
      - regulation
      - public_policy
      - government_services
      - compliance
      - international_relations
      - public_safety

  health_medicine:
    description: 医疗、健康、临床、公共卫生
    minors:
      - clinical_medicine
      - public_health
      - pharmacy
      - mental_health
      - fitness
      - nutrition
      - healthcare_operations

  education_training:
    description: 教学、培训、考试、学习辅导
    minors:
      - lecture
      - tutorial
      - exam_preparation
      - classroom_discussion
      - language_learning
      - professional_training
      - mentoring

  culture_media_arts:
    description: 文化、媒体、娱乐、艺术、人文表达
    minors:
      - literature
      - music
      - film_tv
      - gaming
      - visual_art
      - religion
      - media_production
      - pop_culture

  news_current_events:
    description: 新闻、时事、社会事件和公共议题
    minors:
      - politics
      - economy
      - local_news
      - international_news
      - climate_environment
      - social_issues
      - breaking_news

  daily_life_social:
    description: 日常生活、人际交流、家庭、消费和闲聊
    minors:
      - family
      - food
      - shopping
      - housing
      - travel_transportation
      - interpersonal_chat
      - personal_experience
      - small_talk

  customer_service_support:
    description: 客服、售后、咨询、投诉、工单处理
    minors:
      - product_inquiry
      - troubleshooting
      - complaint
      - billing
      - account_support
      - appointment
      - refund_exchange

  meeting_workflow:
    description: 会议组织过程，而不是会议讨论的业务主题本身
    minors:
      - agenda
      - scheduling
      - status_update
      - decision
      - action_item
      - brainstorming
      - coordination
      - opening_closing

  other:
    description: 无法归入上述类别或信息不足
    minors:
      - unknown
      - insufficient_context
      - mixed_topics
      - non_speech
```

`configs/ami.yaml`：

```yaml
dataset:
  name: AMI
  root: /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI
  annotation_release: "AMI Manual Annotations 1.7"

adapter:
  parse_granularity: segment
  tag_granularity: meeting
  sample_granularity: segment
  audio_preference:
    - mix_headset
    - beamformed_mdm8
    - headset
  include_nonword_events: true
  allow_null_audio_times: true
```

## 9. 模块任务拆解

### Task 1: 建立 schema

产出：

- `sure_tagger/schemas.py`
- manifest sample schema
- tag result schema
- bad sample schema

完成标准：

- 能 validate 单条 AMI 示例 sample。
- 必填字段缺失时报清晰错误。

### Task 2: 实现 JSONL IO

产出：

- `sure_tagger/io/jsonl.py`

完成标准：

- 支持流式读取和写入。
- 遇到坏 JSON 能定位行号。

### Task 3: 实现 AMI words parser

产出：

- `sure_tagger/datasets/ami.py`
- `parse_words_file(path)`

完成标准：

- 返回按 `nite:id` 索引的 word/event 字典。
- 正确处理 XML namespace。
- 正确处理 `w`、`vocalsound`。

### Task 4: 实现 AMI segments parser

产出：

- `parse_segments_file(path)`
- `resolve_nite_href(href, words_index)`

完成标准：

- 正确展开单 id 和 id range。
- 恢复 transcript。
- 失败引用进入 bad samples。

### Task 5: 实现 build-manifest CLI

产出：

- `sure_tagger/cli.py build-manifest`

完成标准：

- 输入 AMI root，输出 manifest。
- 输出 build report。
- 不因单条坏样本中断全局。

### Task 6: 实现文本 normalize/tokenizer

产出：

- `sure_tagger/text/normalize.py`
- `sure_tagger/text/tokenizer.py`

完成标准：

- XML 文本 unescape。
- 标点 spacing 合理。
- tokenizer 行为可配置。

### Task 7: 实现确定性 tags

产出：

- `word_count.py`
- `punctuation.py`
- `filler.py`
- `repetition.py`

完成标准：

- 每个 tool 可单独调用。
- 每个输出符合 tag schema。
- 单元测试覆盖空文本、短文本、带标点、重复词、filler。

### Task 8: 实现 language tag

产出：

- `language.py`

完成标准：

- 支持至少一种本地语言识别工具。
- 短文本输出 confidence 降权。
- AMI 抽样大部分为 `en`。

### Task 9: 实现 context builder

产出：

- `sure_tagger/text/context.py`

完成标准：

- 能按 meeting_id 聚合样本。
- 能按时间窗口取上下文。
- 能按 speaker 取邻近 segment。

### Task 10: 实现 topic tag

产出：

- `topic.py`
- `sure_tagger/llm/client.py`
- `sure_tagger/llm/cache.py`
- `sure_tagger/llm/prompts.py`
- `sure_tagger/text/key_terms.py`
- `configs/topic_taxonomy_general.yaml`
- topic 返回结构定义
- prompt/config version

完成标准：

- 支持 `general_topic_v0.1.0` 通用层级 taxonomy。
- 输出 `major_topic` 和 `minor_topic`。
- 输出 `topic_keywords` 和 `proper_nouns`。
- 校验 `minor_topic` 必须属于对应 `major_topic`。
- 记录 `evidence_scope` 和 `evidence_sample_count`。
- 支持当前 API 调用大模型。
- 支持 cache，避免重复 API 调用。
- 支持 dry-run 和 sample limit。

### Task 11: 实现 tag CLI 和 report

产出：

- `sure_tagger/cli.py tag`
- `sure_tagger/report.py`

完成标准：

- 支持选择 tags。
- 输出 tag results。
- 输出 bad samples。
- 输出 run report。

### Task 12: 抽样 QA

产出：

- `outputs/ami/meeting_qa_samples.jsonl`
- `outputs/ami/qa_report.md`

完成标准：

- 抽样检查文本恢复是否正确。
- 检查 language/topic 的低置信样本。
- 检查空文本和非词事件处理。

## 10. 推荐开发顺序

第 1 阶段：Manifest 优先

- Task 1
- Task 2
- Task 3
- Task 4
- Task 5

验收命令：

```bash
python3 -m sure_tagger.cli build-manifest \
  --dataset ami \
  --root /hpc_stor03/sjtu_home/huifei.wang/sure-tagger/AMI \
  --output outputs/ami/segment_manifest.full.jsonl

python3 -m sure_tagger.cli build-meeting-manifest \
  --manifest outputs/ami/segment_manifest.full.jsonl \
  --output outputs/ami/meeting_manifest.full.jsonl
```

第 2 阶段：确定性语言 tags

- Task 6
- Task 7
- Task 11 的基础部分

验收命令：

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --tags word_count,punctuation,filler,repetition \
  --output outputs/ami/meeting_language_tags.deterministic.jsonl
```

第 3 阶段：模型类 tags

- Task 8
- Task 9
- Task 10
- Task 11 的 report/cache 部分

验收命令：

```bash
python3 -m sure_tagger.cli tag \
  --manifest outputs/ami/meeting_manifest.full.jsonl \
  --config configs/tags_language_mvp.yaml \
  --output outputs/ami/meeting_language_tags.jsonl \
  --report outputs/ami/tag.meeting.report.json
```

第 4 阶段：QA 和文档

- Task 12
- 补充 README usage
- 固化 AMI demo 结果

## 11. 测试计划

### 单元测试

覆盖：

- XML namespace 解析。
- `href` 单 id 解析。
- `href` range 解析。
- transcript 拼接。
- tokenizer 行为。
- filler 词表匹配。
- repetition spans。
- punctuation counts。

### 集成测试

使用少量 AMI 会议：

```text
ES2002a
EN2001a
IS1000a
```

验证：

- manifest 能生成。
- tags 能生成。
- bad sample 不影响主流程。
- report 中计数正确。

### 全量测试

对完整 AMI 跑：

- manifest generation
- deterministic tags
- language tag
- topic tag 先抽样，不建议第一版直接全量 API 调用
- topic 本地结构校验
- taxonomy 合法性校验
- cache 命中率统计

## 12. 风险和决策

### 风险 1: Topic 对短样本不稳定

处理：

- 默认使用上下文窗口。
- 输出 evidence scope。
- 低置信度输出 `other/insufficient_context`。

### 风险 2: AMI 的 XML standoff 引用复杂

处理：

- 优先实现可靠 parser。
- 保留 source path 和原始 href。
- 失败样本单独记录。

### 风险 3: 通用 taxonomy 覆盖不足

处理：

- Topic tool 必须从配置加载 taxonomy，不在代码里硬编码。
- 第一版使用 `general_topic_v0.1.0`，覆盖学术、技术、商业、法律、医疗、教育、文化、新闻、日常、客服、会议流程等大类。
- 每次 QA 记录无法覆盖的样本，进入 taxonomy revision backlog。
- 新增领域时扩展 taxonomy config，而不是改 parser 或 tagger 主逻辑。

### 风险 4: 模型/API 成本和不可复现

处理：

- 大模型/API tags 必须 cache。
- 记录 prompt/config/model/schema version。
- MVP 阶段 topic 先抽样跑，再全量。
- 默认 `temperature=0`，输出通过本地结构校验和 taxonomy 校验。

## 13. 交付物清单

- [ ] `language_layer_pipeline_execution_plan.md`
- [ ] `sure_tagger/schemas.py`
- [ ] `sure_tagger/datasets/ami.py`
- [ ] `sure_tagger/cli.py`
- [ ] `sure_tagger/text/normalize.py`
- [ ] `sure_tagger/text/tokenizer.py`
- [ ] `sure_tagger/text/context.py`
- [ ] `sure_tagger/text/key_terms.py`
- [ ] `sure_tagger/llm/client.py`
- [ ] `sure_tagger/llm/cache.py`
- [ ] `sure_tagger/llm/prompts.py`
- [ ] `sure_tagger/tags/language.py`
- [ ] `sure_tagger/tags/word_count.py`
- [ ] `sure_tagger/tags/punctuation.py`
- [ ] `sure_tagger/tags/filler.py`
- [ ] `sure_tagger/tags/repetition.py`
- [ ] `sure_tagger/tags/topic.py`
- [ ] `configs/ami.yaml`
- [ ] `configs/tags_language_mvp.yaml`
- [ ] `configs/topic_taxonomy_general.yaml`
- [ ] `outputs/ami/segment_manifest.full.jsonl`
- [ ] `outputs/ami/meeting_manifest.full.jsonl`
- [ ] `outputs/ami/meeting_language_tags.jsonl`
- [ ] `outputs/ami/tag.meeting.report.json`
- [ ] `outputs/ami/bad_samples.jsonl`
- [ ] `outputs/ami/qa_report.md`

## 14. 第一周执行排期

Day 1:

- 固化 schema。
- 实现 JSONL IO。
- 实现 AMI words parser。

Day 2:

- 实现 AMI segments parser。
- 实现 standoff href 展开。
- 生成小规模 manifest。

Day 3:

- 实现 build-manifest CLI。
- 跑 AMI 小样本集成测试。
- 修复文本恢复和时间边界问题。

Day 4:

- 实现 normalize/tokenizer。
- 实现 `word_count`、`punctuation`。

Day 5:

- 实现 `filler`、`repetition`。
- 实现 tag CLI 基础版本。

Day 6:

- 实现 `language`。
- 实现 context builder。
- 实现 `configs/topic_taxonomy_general.yaml`。
- 实现大模型 client/cache/prompt skeleton。

Day 7:

- 实现 topic MVP：层级分类、关键词、专有名词、schema 校验。
- 对 AMI 抽样跑 topic，不直接全量 API 调用。
- 抽样 QA，重点检查大类/小类是否合理。
- 生成 demo report。

## 15. 下一步

立即开始的最小闭环：

1. 创建 package skeleton。
2. 实现 AMI adapter。
3. 从 AMI 生成 meeting manifest，并抽取 20 场会议。
4. 对这 20 场会议跑确定性 tags。
5. 对这 20 场会议抽样跑大模型 topic。
6. 人工检查 transcript 恢复质量、`major_topic/minor_topic`、`topic_keywords/proper_nouns`。

这个闭环通过后，再跑完整 AMI。
