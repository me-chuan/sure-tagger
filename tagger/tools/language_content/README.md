# Language Content Tools

Language-content tools run inside the root signal pipeline. Deterministic tools
only require `sample.text.transcript`; topic classification is optional and uses
an OpenAI-compatible Responses API when enabled.

Implemented fields:

- `language_content.language`: Unicode script heuristic language ID.
- `language_content.word_count`: simple multilingual token word count.
- `language_content.punctuation`: punctuation count and terminal punctuation flag.
- `language_content.repetition`: consecutive repeated word/ngram detection.
- `language_content.filler`: lexicon count for fillers such as `uh`, `um`, `hmm`,
  and `yeah`.
- `language_content.topic`: optional hierarchical topic label as
  `major_topic/minor_topic`.

Topic classification is disabled by default so normal pipeline runs do not make
external API calls. Enable it with:

```bash
python3 scripts/run_signal.py \
  --manifest path/to/manifest.jsonl \
  --output outputs/tags.jsonl \
  --topic-enable \
  --topic-model gpt-5.5 \
  --topic-api-key-path api.txt
```

Provider settings can also come from `OPENAI_API_KEY`, `OPENAI_MODEL`,
`OPENAI_BASE_URL`, `tagger/local_config.py`, or `~/.codex/config.toml` when
`--topic-model-provider` is set. `api.txt` is git-ignored.

API key lookup order:

1. `OPENAI_API_KEY`
2. `--topic-api-key`
3. `--topic-api-key-path`, defaulting to `api.txt`
4. selected provider env in `~/.codex/config.toml`

The public topic value is a string such as
`technology_engineering/artificial_intelligence`. Model confidence, keywords,
proper nouns, prompt version, taxonomy version, and failure details are kept only
in internal tool evidence. Short non-content utterances such as `yeah` are
guarded deterministically as `other/insufficient_context` without an API call.

These tools do not need audio files. Only the optional topic tool needs external
API access.
