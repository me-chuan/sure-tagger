# Language Content Tools

Language-content tools run inside the root tagging pipeline. Deterministic tools
use `sample.text.transcript`, or the speaker-v2 MOSS ASR transcript when the input
text is empty.

Implemented fields:

- `language_content.language`: Unicode script heuristic language ID for the
  speaker-v2 ASR fallback; non-empty input uses FireRed LID audio detection.
- `language_content.word_count`: simple multilingual token word count.
- `language_content.punctuation`: punctuation count and terminal punctuation flag.
- `language_content.repetition`: consecutive repeated word/ngram detection.
- `language_content.filler`: lexicon count for fillers such as `uh`, `um`, `hmm`,
  and `yeah`.

The MOSS transcript is published separately as
`speaker.asr_transcript`. It is built from MOSS timeline segment text in time
order, without timestamps or speaker IDs, and is `null` when MOSS has no valid
text. A non-empty `sample.text.transcript` is still the preferred input for the
five language-content fields, but it never populates `speaker.asr_transcript`.

`language_content.topic` is not registered or emitted by sure-tagger. Topic is
an open descriptive phrase inferred by the downstream language model from the
deterministic tags and ASR text; it has no fixed taxonomy in this layer. The
legacy `topic.py` module remains only for historical pipeline reproducibility.
