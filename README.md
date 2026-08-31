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
- Speaker v2 evidence, alignment, and fusion artifacts are written under
  `artifacts/speaker_v2/<row-key>/`.
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
  --output outputs/phase2_asr_patch.jsonl \
  --sample-id EN2001a_utterance_00000 \
  --only-tags speaker.asr_transcript \
  --missing-only
```

Compare Brouhaha C50 against Rec-RIR-derived C50 on the bundled manifest:

```bash
python3 scripts/run_c50_method_comparison.py
```

Run only the speaker stage with the default `quality-shadow` profile:

```bash
python3 scripts/run_tagger.py \
  --manifest phase1_asr_samples/manifest.jsonl \
  --output phase1_asr_samples/outputs/sample_tags.jsonl \
  --only-tags speaker \
  --speaker-profile quality-shadow
```

The main pipeline calls speaker v2 directly; there is no legacy MOSS enable gate,
native-metadata speaker route, or channel-activity fallback. The default profile
uses MOSS, FireRed VAD, Sortformer, Pyannote, ECAPA, and Brouhaha as configured by
`tagger/pipelines/speaker_evidence.py`. `--speaker-profile lean-shadow` selects
the lower-cost profile. `--speaker-v2-skip-model-verification` only skips pinned
asset hash checks; it does not download models or disable inference.

Model-backed tools require local model directories/checkpoints. General acoustic
tools read `tagger/local_config.py`; speaker v2 defaults are defined in
`tagger/pipelines/speaker_evidence.py`.

`language_content.topic` and its API/CLI integration are no longer part of
sure-tagger. A downstream language model may generate an open descriptive
`topic` phrase from the deterministic tags and `speaker.asr_transcript`.

See [the tag and method documentation](docs/tags-and-methods.md) for the public
fields, preprocessing, and JSON examples. Tool-specific setup details are kept
in `tagger/tools/basic_acoustic/README.md`,
`tagger/tools/sound_field_scene/README.md`,
`tagger/tools/speaker_v2/docs/direct_public_output_20260820.md`, and
`tagger/tools/language_content/README.md`.

## Speaker Pipeline

The `speaker` stage directly runs speaker v2 and publishes seven scalar fields:
`speaker_count`, derived `speaker_present`, `multi_speaker`,
`speaker_change_count`, `speaker_change`, `overlap_ratio`, and
`speaker_overlap`, plus the `profiles` array and `asr_transcript` string. The
ASR value is the full-sample MOSS timeline text joined in time order; it never
comes from `sample.text.transcript`. Model evidence and claim routing remain
internal under `artifacts/speaker_v2/<row-key>/`.
