"""Tool for tag `acoustic.channels`."""

from tagger.tools.acoustic_io import get_audio_info
from tagger.tools.base import ToolResult


TAG_PATH = "acoustic.channels"
TOOL_NAME = "acoustic_channels"


def run(audio_path, context=None, **_kwargs):
    info = get_audio_info(audio_path, context)
    return ToolResult(
        tag_path=TAG_PATH,
        value=info.channels,
        tool_name=TOOL_NAME,
        method=info.method,
        evidence=info.base_evidence(),
    )
