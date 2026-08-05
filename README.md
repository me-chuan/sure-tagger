# sure-tagger

ASR dataset sample-level tagging toolkit. The project currently focuses on
acoustic, signal, sound-field, speaker, and language-content tags from raw-only
sample inputs.

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

Run the sample-level signal pipeline on the bundled sample manifest:

```bash
python3 scripts/run_signal.py
```

Run with MOSS diarization enabled for mixed/mono recordings:

```bash
python3 scripts/run_signal.py \
  --manifest phase1_asr_samples/manifest.jsonl \
  --output phase1_asr_samples/outputs/sample_tags.jsonl \
  --moss-diarize-enable \
  --moss-diarize-endpoint http://localhost:8000/v1/audio/transcriptions \
  --moss-diarize-model /hpc_stor03/sjtu_home/huifei.wang/models/moss_td_model
```

Multi-channel separated-headset WAV inputs use merged-headset MOSS when
`--moss-diarize-enable` is set: the pipeline first downmixes the headset
channels into a temporary mono WAV, then runs one MOSS diarization request.
Without MOSS, or when merged-headset MOSS fails, the speaker layer can fall
back to the channel-activity baseline.
For the local endpoint, `--moss-diarize-model` must match the model path served
by the endpoint.

Model-backed tools require local model directories/checkpoints configured in
`tagger/local_config.py`.

## Speaker Pipeline

Speaker layer supports two routes:

- Mix-Headset / mono mixed recording: MOSS diarize.
- Multi-channel separated headset: downmix headset channels, then run one MOSS
  diarize request. Channel activity is only a fallback/baseline.

Pipeline details and metadata examples live in `tagger/tools/speaker/README.md`
and `tagger/tools/speaker/speaker_metadata_standard.md`.
