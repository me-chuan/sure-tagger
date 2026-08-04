"""Tool for `signal.silence_ratio` derived from FireRed VAD silence segments."""

from tagger.tools.base import ToolResult
from tagger.tools.signal_tags.firered_vad_silence_detector import (
    METHOD,
    validate_silence_segments,
)


TOOL_NAME = "silence_ratio_calculator"


def run(silence_segments, duration_sec, **_kwargs):
    if duration_sec is None or duration_sec <= 0:
        raise ValueError("duration_sec must be positive before silence ratio")
    validate_silence_segments(silence_segments, duration_sec)
    silence_total = sum(
        segment["end_sec"] - segment["start_sec"] for segment in silence_segments
    )
    ratio = silence_total / duration_sec
    if ratio < 0 or ratio > 1:
        raise ValueError("silence_ratio is outside [0, 1]")
    return ToolResult(
        tag_path="signal.silence_ratio",
        value=round(ratio, 6),
        tool_name=TOOL_NAME,
        method=METHOD,
        evidence={"silence_segments": silence_segments, "duration_sec": duration_sec},
    )

