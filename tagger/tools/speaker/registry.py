"""Registry of speaker tag tools."""

from tagger.tools.speaker import channel_activity
from tagger.tools.speaker import metrics
from tagger.tools.speaker import moss_diarizer


MOSS_DIARIZE_TOOL = {
    "tag_path": "speaker.diarization_timeline",
    "tool_name": moss_diarizer.TOOL_NAME,
    "run": moss_diarizer.run,
    "run_channel_purity_check": moss_diarizer.run_channel_purity_check,
    "run_merged_channels": moss_diarizer.run_merged_channels,
}

CHANNEL_ACTIVITY_TOOL = {
    "tag_path": "speaker.channel_activity",
    "tool_name": channel_activity.TOOL_NAME,
    "run": channel_activity.run,
}

SPEAKER_METRICS_TOOL = {
    "tag_path": "speaker",
    "tool_name": "speaker_metrics",
    "run": metrics.public_results_from_metadata,
}

SPEAKER_TOOLS = [
    MOSS_DIARIZE_TOOL,
    CHANNEL_ACTIVITY_TOOL,
    SPEAKER_METRICS_TOOL,
]
