"""Tool for v2 base signal tags read from the audio file."""

from tagger.tools.acoustic_io import get_audio_info
from tagger.tools.base import ToolResult


TOOL_NAME = "audio_probe"


def run(audio_path, context=None, **_kwargs):
    info = get_audio_info(audio_path, context)
    evidence = info.base_evidence()
    return [
        ToolResult(
            tag_path="signal.duration_sec",
            value=round(info.duration_sec, 6),
            tool_name=TOOL_NAME,
            method=info.method,
            evidence=evidence,
        ),
        ToolResult(
            tag_path="signal.sample_rate_hz",
            value=info.sample_rate_hz,
            tool_name=TOOL_NAME,
            method=info.method,
            evidence=evidence,
        ),
        ToolResult(
            tag_path="signal.channels",
            value=info.channels,
            tool_name=TOOL_NAME,
            method=info.method,
            evidence=evidence,
        ),
    ]

