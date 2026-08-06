"""Runtime configuration for speaker tag tools."""

from tagger import local_config
from tagger.tools.speaker.channel_activity import ChannelActivityConfig
from tagger.tools.speaker.moss_diarizer import MossDiarizeConfig


class SpeakerLayerConfig:
    """Configuration for speaker diarization routing."""

    def __init__(
        self,
        enable_moss=False,
        enable_channel_activity=True,
        force_channel_activity=False,
        prefer_channel_activity=False,
        run_moss_for_channel_qa=True,
        moss_config=None,
        channel_activity_config=None,
    ):
        self.enable_moss = bool(enable_moss)
        self.enable_channel_activity = bool(enable_channel_activity)
        self.force_channel_activity = bool(force_channel_activity or prefer_channel_activity)
        # Kept as an attribute for callers that still inspect the legacy option.
        self.prefer_channel_activity = self.force_channel_activity
        self.run_moss_for_channel_qa = bool(run_moss_for_channel_qa)
        self.moss_config = moss_config or MossDiarizeConfig()
        self.channel_activity_config = channel_activity_config or ChannelActivityConfig()


def default_speaker_layer_config(
    enable_moss=False,
    moss_endpoint=None,
    moss_model=None,
    moss_timeout_sec=None,
    moss_max_new_tokens=None,
    moss_api_key=None,
):
    moss_config = MossDiarizeConfig(
        endpoint=moss_endpoint
        if moss_endpoint is not None
        else getattr(local_config, "MOSS_DIARIZE_ENDPOINT", ""),
        model=moss_model
        if moss_model is not None
        else getattr(local_config, "MOSS_DIARIZE_MODEL", ""),
        timeout_sec=moss_timeout_sec
        if moss_timeout_sec is not None
        else getattr(local_config, "MOSS_DIARIZE_TIMEOUT_SEC", 900),
        max_new_tokens=moss_max_new_tokens
        if moss_max_new_tokens is not None
        else getattr(local_config, "MOSS_DIARIZE_MAX_NEW_TOKENS", 65536),
        api_key=moss_api_key
        if moss_api_key is not None
        else getattr(local_config, "MOSS_DIARIZE_API_KEY", ""),
    )
    channel_config = ChannelActivityConfig(
        window_sec=getattr(local_config, "SPEAKER_CHANNEL_WINDOW_SEC", 0.05),
        energy_threshold=getattr(local_config, "SPEAKER_CHANNEL_ENERGY_THRESHOLD", 200.0),
        leakage_relative_db=getattr(local_config, "SPEAKER_CHANNEL_LEAKAGE_RELATIVE_DB", -18.0),
        min_segment_duration_sec=getattr(local_config, "SPEAKER_MIN_SEGMENT_DURATION_SEC", 0.10),
        merge_gap_sec=getattr(local_config, "SPEAKER_MERGE_SAME_SPEAKER_GAP_SEC", 0.30),
    )
    return SpeakerLayerConfig(
        enable_moss=enable_moss,
        enable_channel_activity=True,
        force_channel_activity=False,
        prefer_channel_activity=False,
        run_moss_for_channel_qa=True,
        moss_config=moss_config,
        channel_activity_config=channel_config,
    )
