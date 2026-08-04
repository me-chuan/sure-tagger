"""Registry of v3 signal tag tools."""

from tagger.tools.signal_tags import audio_probe
from tagger.tools.signal_tags import brouhaha_signal_estimator
from tagger.tools.signal_tags import firered_vad_silence_detector
from tagger.tools.signal_tags import silence_ratio_calculator


SIGNAL_PROBE_TOOL = {
    "tag_path": "signal",
    "tool_name": audio_probe.TOOL_NAME,
    "run": audio_probe.run,
}

FIRERED_VAD_SILENCE_TOOL = {
    "tag_path": "signal.silence_segments",
    "tool_name": firered_vad_silence_detector.TOOL_NAME,
    "run": firered_vad_silence_detector.run,
}

SILENCE_RATIO_TOOL = {
    "tag_path": "signal.silence_ratio",
    "tool_name": silence_ratio_calculator.TOOL_NAME,
    "run": silence_ratio_calculator.run,
}

BROUHAHA_SIGNAL_TOOL = {
    "tag_path": "signal",
    "tool_name": brouhaha_signal_estimator.TOOL_NAME,
    "run": brouhaha_signal_estimator.run,
}

V2_SIGNAL_TOOLS = [
    SIGNAL_PROBE_TOOL,
    FIRERED_VAD_SILENCE_TOOL,
    SILENCE_RATIO_TOOL,
]

V3_SIGNAL_TOOLS = V2_SIGNAL_TOOLS + [
    BROUHAHA_SIGNAL_TOOL,
]
