"""Tool for tag `acoustic.duration_sec`."""

from tagger.tools.acoustic_io import get_audio_info
from tagger.tools.base import ToolResult


TAG_PATH = "acoustic.duration_sec"
TOOL_NAME = "acoustic_duration_sec"


def run(audio_path, context=None, **_kwargs):
    info = get_audio_info(audio_path, context)
    return ToolResult(
        tag_path=TAG_PATH,
        value=round(info.duration_sec, 6),
        tool_name=TOOL_NAME,
        method=info.method,
        evidence=info.base_evidence(),
    )
