# sure-tagger

ASR dataset sample-level tagging toolkit. The project currently focuses on
acoustic, sound-field, speaker, and language-content tags from raw-only
sample inputs.

## Repository Layout

- `tagger/`: core schemas, tag tools, and pipelines.
- `docs/`: user-facing documentation, including the
  [tag definitions, methods, and JSON examples](docs/tags-and-methods.md).
- `scripts/`: runnable pipeline entry points.
- `tests/`: unit and smoke tests.
- `phase1_asr_samples/`: small local demo samples and manifests.
- `ami_en2001a_utterances/`: utterance-level AMI multi-speaker test manifest
  and locally generated audio cuts.
- `bridge/sure-tagger/`: language-layer prototype and related notes.
- `development.md`: current development constraints and public input/output
  schema.

## Git-ignored Local Artifacts

Large or machine-local files are intentionally not tracked:

- `.runtime/`: local Python/runtime environments.
- `models/`: third-party model repositories and checkpoints.
- `data`: shared dataset symlink.
- `outputs/`, `bridge/sure-tagger/outputs/`,
  `phase1_asr_samples/outputs/`,
  `ami_en2001a_utterances/outputs/`: generated run outputs.
- `ami_en2001a_utterances/audio/`: generated EN2001a utterance WAV files.
- Rec-RIR waveform artifacts are written under the selected output directory's
  `artifacts/rir/` subdirectory by default.
- Speaker diarization metadata artifacts are written under
  `artifacts/speaker/` when speaker tools produce a valid timeline.
- `api.txt`, `.env*`, `.codex/`: local secrets and private config.

## Quick Commands

Run tests:

```bash
python3 -m unittest discover -s tests
```

Run the sample-level tagging pipeline on the bundled sample manifest:

```bash
python3 scripts/run_tagger.py
```

Run the full pipeline for one sample only:

```bash
python3 scripts/run_tagger.py \
  --manifest phase2_asr_sample/manifest.jsonl \
  --output outputs/one_sample_tags.jsonl \
  --sample-id EN2001a_utterance_00000
```

Supplement selected tags into an existing tags-only output:

```bash
python3 scripts/run_tagger.py \
  --manifest phase2_asr_sample/manifest.jsonl \
  --input-tags outputs/phase2_full_pipeline_tags.jsonl \
  --output outputs/phase2_topic_patch.jsonl \
  --sample-id EN2001a_utterance_00000 \
  --only-tags language_content.topic \
  --topic-enable \
  --topic-model gpt-5.5 \
  --topic-api-key-path api.txt
```

Compare Brouhaha C50 against Rec-RIR-derived C50 on the bundled manifest:

```bash
python3 scripts/run_c50_method_comparison.py
```

Run with MOSS diarization enabled for mixed/mono recordings:

```bash
python3 scripts/run_tagger.py \
  --manifest phase1_asr_samples/manifest.jsonl \
  --output phase1_asr_samples/outputs/sample_tags.jsonl \
  --moss-diarize-enable \
  --moss-diarize-python .runtime/moss_transcribe_diarize_py312/bin/python \
  --moss-diarize-model OpenMOSS-Team/MOSS-Transcribe-Diarize
```

Multi-channel separated-headset WAV inputs use merged-headset MOSS when
`--moss-diarize-enable` is set and MOSS cannot confirm that every channel has
exactly one speaker. If MOSS confirms one speaker per channel, the pipeline uses
the channel-activity route; if the check fails or detects mixed speakers, it
downmixes headset channels into a temporary mono WAV and runs MOSS diarization.
Without MOSS, channel activity only runs when the dataset is explicitly asserted
to have one speaker per channel.

Model-backed tools require local model directories/checkpoints configured in
`tagger/local_config.py`.

OpenAI Responses topic classification reads credentials in this order:
`OPENAI_API_KEY`, `--topic-api-key`, `api.txt` or `--topic-api-key-path`, then
the selected provider env in `~/.codex/config.toml`. Do not commit secrets;
`api.txt`, `.env*`, and `.codex/` are git-ignored.

See [the tag and method documentation](docs/tags-and-methods.md) for the public
fields, preprocessing, and JSON examples. Tool-specific setup details are kept
in `tagger/tools/basic_acoustic/README.md`,
`tagger/tools/sound_field_scene/README.md`,
`tagger/tools/speaker/README.md`, and
`tagger/tools/language_content/README.md`.

## Speaker Pipeline

Speaker layer supports two routes:

- Mix-Headset / mono mixed recording: MOSS diarize.
- Multi-channel separated headset: downmix headset channels, then run one MOSS
  diarize request. Channel activity is only a fallback/baseline.

Pipeline details and metadata examples live in `tagger/tools/speaker/README.md`
and `tagger/tools/speaker/speaker_metadata_standard.md`.
