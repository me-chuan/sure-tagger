# Sound-Field And Scene Tools

## FireRed AED

The FireRed AED adapter uses the official non-streaming AED model at
`models/FireRedVAD/pretrained_models/FireRedVAD/AED` in the configured
FireRed Python runtime. The upstream model recognizes exactly three overlapping
event classes: `speech`, `singing`, and `music`.

The public schema keeps boolean scene tags:

| FireRed AED result | Public tag |
| --- | --- |
| At least one `music` segment | `sound_field_scene.music = true` |
| At least one `singing` or `music` segment | `sound_field_scene.sound = true` |
| Neither corresponding event is present | The tag is `false` |
| Model, dependency, inference, or validation failure | Both tags are `null` |

Validated `speech`/`singing`/`music` segments and upstream thresholded-frame
ratios are retained as internal tool evidence and do not enter the tags-only
public output. FireRed AED is not a general-purpose environmental sound model;
it does not identify traffic, applause, alarms, or other event classes.

Run an AED-only smoke test:

```bash
python3 - <<'PY'
from tagger.tools.sound_field_scene.firered_aed_detector import run

for result in run("models/FireRedVAD/assets/event.wav", duration_sec=22.016):
    print(result.tag_path, result.value)
    print(result.evidence["event_segments"])
PY
```

The full signal pipeline enables AED by default. Use
`--firered-aed-use-gpu` to select GPU inference or `--firered-aed-python` to
override the configured subprocess interpreter.
