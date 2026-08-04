"""Registry of sound-field and acoustic-scene tag tools."""

from tagger.tools.sound_field_scene_tags import c50_estimator
from tagger.tools.sound_field_scene_tags import rir_estimator
from tagger.tools.sound_field_scene_tags import rt60_estimator


RECRIR_RIR_TOOL = {
    "tag_path": "sound_field_scene.rir",
    "tool_name": rir_estimator.TOOL_NAME,
    "run": rir_estimator.run,
}

RT60_TOOL = {
    "tag_path": "sound_field_scene.rt60",
    "tool_name": rt60_estimator.TOOL_NAME,
    "run": rt60_estimator.run,
}

C50_TOOL = {
    "tag_path": "sound_field_scene.c50",
    "tool_name": c50_estimator.TOOL_NAME,
    "run": c50_estimator.run,
}

RIR_RELATED_TOOLS = [
    RECRIR_RIR_TOOL,
    RT60_TOOL,
    C50_TOOL,
]

