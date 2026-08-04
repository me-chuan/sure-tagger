# sure-tagger

ASR dataset sample-level tagging toolkit. The project currently focuses on
acoustic, signal, sound-field, and language-content tags from raw-only sample
inputs.

## Repository Layout

- `tagger/`: core schemas, tag tools, and pipelines.
- `scripts/`: runnable pipeline entry points.
- `tests/`: unit and smoke tests.
- `phase1_asr_samples/`: small local demo samples and manifests.
- `bridge/sure-tagger/`: language-layer prototype and related notes.
- `development.md`: current development constraints and public input/output
  schema.

## Git-ignored Local Artifacts

Large or machine-local files are intentionally not tracked:

- `.runtime/`: local Python/runtime environments.
- `models/`: third-party model repositories and checkpoints.
- `data`: shared dataset symlink.
- `outputs/`, `bridge/sure-tagger/outputs/`,
  `phase1_asr_samples/outputs/`: generated run outputs.
- `api.txt`, `.env*`, `.codex/`: local secrets and private config.

## Quick Commands

Run tests:

```bash
python3 -m pytest tests
```

Run the acoustic phase-1 sample pipeline:

```bash
python3 scripts/run_phase1_acoustic.py
```

Run signal pipelines on the bundled sample manifest:

```bash
python3 scripts/run_signal_v2.py
python3 scripts/run_signal_v3.py
```

Model-backed tools require local model directories/checkpoints configured in
`tagger/local_config.py`.
