# Sound-Field And Scene Tools

## FireRed AED Event Detection

The FireRed AED adapter uses the official non-streaming AED model at
`models/FireRedVAD/pretrained_models/FireRedVAD/AED` in the configured
FireRed Python runtime. The upstream model recognizes exactly three overlapping
event classes: `speech`, `singing`, and `music`. This registered tool publishes
the detected class names and a backward-compatible music decision.

The public schema exposes detected event names and keeps the existing music
boolean for compatibility:

| FireRed AED result | Public tag |
| --- | --- |
| Detected classes in fixed `speech`, `singing`, `music` order | `sound_field_scene.audio_events` |
| No detected class | `sound_field_scene.audio_events = []` |
| At least one `music` segment | `sound_field_scene.music = true` |
| No `music` segment | `sound_field_scene.music = false` |
| Model, dependency, inference, or validation failure | Both fields are `null` |

Validated `speech`/`singing`/`music` segments and upstream thresholded-frame
ratios are retained as internal tool evidence and do not enter the tags-only
public output. PANNs separately owns the general background-sound tag.

Run an AED-only smoke test:

```bash
python3 - <<'PY'
from tagger.tools.sound_field_scene.firered_aed_detector import run

for result in run("models/FireRedVAD/assets/event.wav", duration_sec=22.016):
    print(result.tag_path, result.value)
    print(result.evidence["event_segments"])
PY
```

## PANNs Background-Sound Detection

The PANNs adapter uses the upstream AudioSet Cnn14 model pinned at commit
`d2f4b8c18eab44737fcc0de1248ae21eb43f6aa4`. It normalizes audio to 32 kHz
mono, runs non-overlapping 10-second chunks, and takes the maximum eligible
event probability across the sample.

`sound_field_scene.sound` is a score-ranked list of eligible AudioSet display
names whose maximum clip probability is at least `0.30`. At most ten names are
published. Music, singing, chatter, animals, natural sounds, vehicles,
mechanisms, and noise are eligible. Primary speech, silence, room/outdoor scene
labels, reverberation, and echo are excluded. A successful inference with no
class at the threshold produces `[]`; model failure produces `null`. Scores,
AudioSet IDs, and chunk details remain internal evidence.

Set up the pinned source and dedicated environment:

```bash
bash scripts/setup_panns_background.sh
```

The official checkpoint host is not reachable from this server. Manually
upload `Cnn14_mAP=0.431.pth` to
`models/audioset_tagging_cnn/checkpoints/Cnn14_mAP=0.431.pth`, then rerun the
setup command so the checkpoint is validated.

Run a detector-only smoke test after the checkpoint is present:

```bash
python3 - <<'PY'
from tagger.tools.sound_field_scene.panns_background_detector import run

result = run("phase1_asr_samples/audio/wham_noise_only_011a010d_mix.wav")
print(result.tag_path, result.value)
print(result.evidence["winning_event"])
PY
```

The full signal pipeline enables both tools by default. Use
`--firered-aed-use-gpu` or `--panns-use-gpu` for GPU inference, and
`--panns-threshold` to override the default PANNs threshold.
