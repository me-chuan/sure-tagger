"""Registry of basic acoustic tag tools."""

from tagger.tools.basic_acoustic import audio_probe
from tagger.tools.basic_acoustic import brouhaha_signal_estimator
from tagger.tools.basic_acoustic import dnsmos_quality_estimator
from tagger.tools.basic_acoustic import firered_vad_silence_detector
from tagger.tools.basic_acoustic import silence_ratio_calculator


AUDIO_PROBE_TOOL = {
    "tag_path": "basic_acoustic",
    "tool_name": audio_probe.TOOL_NAME,
    "run": audio_probe.run,
}

FIRERED_VAD_SILENCE_TOOL = {
    "tag_path": "basic_acoustic.silence_segments",
    "tool_name": firered_vad_silence_detector.TOOL_NAME,
    "run": firered_vad_silence_detector.run,
}

SILENCE_RATIO_TOOL = {
    "tag_path": "basic_acoustic.silence_ratio",
    "tool_name": silence_ratio_calculator.TOOL_NAME,
    "run": silence_ratio_calculator.run,
}

BROUHAHA_ACOUSTIC_TOOL = {
    "tag_path": "basic_acoustic",
    "tool_name": brouhaha_signal_estimator.TOOL_NAME,
    "run": brouhaha_signal_estimator.run,
}

DNSMOS_QUALITY_TOOL = {
    "tag_path": "basic_acoustic",
    "tool_name": dnsmos_quality_estimator.TOOL_NAME,
    "run": dnsmos_quality_estimator.run,
}

BASIC_ACOUSTIC_TOOLS = [
    AUDIO_PROBE_TOOL,
    FIRERED_VAD_SILENCE_TOOL,
    SILENCE_RATIO_TOOL,
    BROUHAHA_ACOUSTIC_TOOL,
    DNSMOS_QUALITY_TOOL,
]
