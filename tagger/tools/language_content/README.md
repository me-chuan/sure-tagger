# Language Content Tools

Deterministic language-content tools run inside the root signal pipeline and
only require `sample.text.transcript`.

Implemented fields:

- `language_content.language`: Unicode script heuristic language ID.
- `language_content.word_count`: simple multilingual token word count.
- `language_content.punctuation`: punctuation count and terminal punctuation flag.
- `language_content.repetition`: consecutive repeated word/ngram detection.
- `language_content.filler`: lexicon count for fillers such as `uh`, `um`, `hmm`,
  and `yeah`.

`language_content.topic` is intentionally not connected here yet. Topic and
context logic remain in `bridge/sure-tagger` until the model-backed language
layer is promoted into the root runtime.

These tools do not need audio files or external model dependencies.
