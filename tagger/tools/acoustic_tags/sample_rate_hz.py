"""Tool for tag `acoustic.sample_rate_hz`."""

from tagger.tools.acoustic_io import get_audio_info
from tagger.tools.base import ToolResult


TAG_PATH = "acoustic.sample_rate_hz"
TOOL_NAME = "acoustic_sample_rate_hz"


def run(audio_path, context=None, **_kwargs):
    info = get_audio_info(audio_path, context)
    return ToolResult(
        tag_path=TAG_PATH,
        value=info.sample_rate_hz,
        tool_name=TOOL_NAME,
        method=info.method,
        evidence=info.base_evidence(),
    )
