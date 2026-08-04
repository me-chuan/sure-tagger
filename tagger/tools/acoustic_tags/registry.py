"""Registry of phase1 acoustic tag tools."""

from tagger.tools.acoustic_tags import channels
from tagger.tools.acoustic_tags import duration_sec
from tagger.tools.acoustic_tags import sample_rate_hz


PHASE1_ACOUSTIC_TOOLS = [
    {
        "tag_path": duration_sec.TAG_PATH,
        "tool_name": duration_sec.TOOL_NAME,
        "run": duration_sec.run,
    },
    {
        "tag_path": sample_rate_hz.TAG_PATH,
        "tool_name": sample_rate_hz.TOOL_NAME,
        "run": sample_rate_hz.run,
    },
    {
        "tag_path": channels.TAG_PATH,
        "tool_name": channels.TOOL_NAME,
        "run": channels.run,
    },
]
