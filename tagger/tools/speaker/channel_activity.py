"""Channel-aware speech activity for separated-headset audio."""

import math
import struct
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from tagger.tools.base import ToolResult


TOOL_NAME = "channel_speech_activity_detector"
TOOL_VERSION = "channel_activity_v0.1.0"


class ChannelActivityError(RuntimeError):
    pass


class ChannelActivityConfig:
    def __init__(
        self,
        window_sec=0.05,
        energy_threshold=500.0,
        leakage_relative_db=-18.0,
        min_segment_duration_sec=0.10,
        merge_gap_sec=0.30,
    ):
        self.window_sec = float(window_sec)
        self.energy_threshold = float(energy_threshold)
        self.leakage_relative_db = float(leakage_relative_db)
        self.min_segment_duration_sec = float(min_segment_duration_sec)
        self.merge_gap_sec = float(merge_gap_sec)


def run(audio_path, duration_sec=None, context=None, config=None, client=None, **_kwargs):
    # type: (Union[str, Path], Optional[float], Optional[Dict[str, Any]], Optional[ChannelActivityConfig], Any, Any) -> ToolResult
    config = config or ChannelActivityConfig()
    if client is not None:
        value = client.detect_channel_activity(audio_path, context=context)
    else:
        value = detect_channel_activity(audio_path, duration_sec=duration_sec, config=config)
    value = validate_channel_activity(value)
    return ToolResult(
        tag_path="speaker.channel_activity",
        value=value,
        tool_name=TOOL_NAME,
        method="per_channel_energy_vad",
        status="estimated",
        confidence=0.8,
        tool_type="deterministic",
        tool_version=TOOL_VERSION,
        evidence={
            "channel_count": len(value.get("channels", [])),
            "duration_sec": value.get("duration_sec"),
        },
    )


def detect_channel_activity(audio_path, duration_sec=None, config=None):
    # type: (Union[str, Path], Optional[float], Optional[ChannelActivityConfig]) -> Dict[str, Any]
    config = config or ChannelActivityConfig()
    path = Path(audio_path)
    try:
        wav = wave.open(str(path), "rb")
    except wave.Error as exc:
        raise ChannelActivityError("channel activity supports PCM WAV input") from exc
    with wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()
        if channels < 2:
            raise ChannelActivityError("channel activity requires at least two channels")
        if sample_width not in (1, 2, 4):
            raise ChannelActivityError("unsupported sample width: %s" % sample_width)
        raw = wav.readframes(frame_count)

    values = _decode_pcm(raw, sample_width)
    if len(values) < channels:
        raise ChannelActivityError("audio contains no samples")
    frames = len(values) // channels
    actual_duration = float(frames) / float(sample_rate)
    duration = float(duration_sec) if duration_sec is not None else actual_duration
    duration = min(duration, actual_duration)
    window_frames = max(1, int(round(sample_rate * config.window_sec)))
    active_windows = [[] for _ in range(channels)]  # type: List[List[Dict[str, float]]]
    relative_threshold = math.pow(10.0, config.leakage_relative_db / 20.0)

    start_frame = 0
    while start_frame < frames:
        end_frame = min(frames, start_frame + window_frames)
        start_sec = float(start_frame) / float(sample_rate)
        end_sec = float(end_frame) / float(sample_rate)
        if start_sec >= duration:
            break
        end_sec = min(end_sec, duration)
        rms_values = []
        for channel_index in range(channels):
            rms_values.append(_window_rms(values, channels, channel_index, start_frame, end_frame))
        max_rms = max(rms_values) if rms_values else 0.0
        for channel_index, rms in enumerate(rms_values):
            active = rms >= config.energy_threshold
            if max_rms > 0:
                active = active and (rms / max_rms >= relative_threshold)
            if active:
                active_windows[channel_index].append({
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                })
        start_frame = end_frame

    channels_out = []
    for channel_index, windows in enumerate(active_windows):
        segments = _merge_segments(
            windows,
            merge_gap_sec=config.merge_gap_sec,
            min_segment_duration_sec=config.min_segment_duration_sec,
            duration_sec=duration,
        )
        channels_out.append({
            "channel_id": "ch%s" % channel_index,
            "speaker_id": "spk_%03d" % channel_index,
            "speech_segments": segments,
        })

    return {
        "metadata_version": "channel_activity_v0.1",
        "duration_sec": round(duration, 6),
        "sample_rate_hz": sample_rate,
        "channels": channels_out,
    }


def validate_channel_activity(value):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    if not isinstance(value, dict):
        raise ChannelActivityError("channel activity must be an object")
    channels = value.get("channels")
    if not isinstance(channels, list) or not channels:
        raise ChannelActivityError("channel activity must contain channels")
    duration_sec = _as_float(value.get("duration_sec"))
    if duration_sec is not None and duration_sec <= 0:
        raise ChannelActivityError("duration_sec must be positive")
    normalized = dict(value)
    normalized_channels = []
    for index, channel in enumerate(channels):
        if not isinstance(channel, dict):
            raise ChannelActivityError("channel must be an object")
        channel_id = str(channel.get("channel_id", "ch%s" % index))
        speaker_id = str(channel.get("speaker_id", "spk_%03d" % index))
        segments = []
        previous_end = None
        for item in channel.get("speech_segments", []):
            start = _as_float(item.get("start_sec", item.get("start")))
            end = _as_float(item.get("end_sec", item.get("end")))
            if start is None or end is None or end <= start:
                raise ChannelActivityError("invalid channel speech segment")
            if duration_sec is not None and (start < 0 or end > duration_sec):
                raise ChannelActivityError("channel speech segment out of bounds")
            if previous_end is not None and start < previous_end:
                raise ChannelActivityError("channel speech segments must be sorted and non-overlapping")
            previous_end = end
            segments.append({
                "start_sec": round(start, 6),
                "end_sec": round(end, 6),
            })
        normalized_channels.append({
            "channel_id": channel_id,
            "speaker_id": speaker_id,
            "speech_segments": segments,
        })
    normalized["channels"] = normalized_channels
    return normalized


def _decode_pcm(raw, sample_width):
    if sample_width == 1:
        return [byte - 128 for byte in bytearray(raw)]
    if sample_width == 2:
        count = len(raw) // 2
        return list(struct.unpack("<%sh" % count, raw))
    if sample_width == 4:
        count = len(raw) // 4
        return list(struct.unpack("<%si" % count, raw))
    raise ChannelActivityError("unsupported sample width: %s" % sample_width)


def _window_rms(values, channels, channel_index, start_frame, end_frame):
    total = 0.0
    count = 0
    for frame_index in range(start_frame, end_frame):
        value = values[frame_index * channels + channel_index]
        total += float(value) * float(value)
        count += 1
    if count <= 0:
        return 0.0
    return math.sqrt(total / float(count))


def _merge_segments(segments, merge_gap_sec, min_segment_duration_sec, duration_sec):
    merged = []
    for item in segments:
        start = max(0.0, float(item["start_sec"]))
        end = min(float(duration_sec), float(item["end_sec"]))
        if end <= start:
            continue
        if not merged or start - merged[-1]["end_sec"] > merge_gap_sec:
            merged.append({"start_sec": start, "end_sec": end})
        else:
            merged[-1]["end_sec"] = max(merged[-1]["end_sec"], end)
    filtered = []
    for item in merged:
        if item["end_sec"] - item["start_sec"] >= min_segment_duration_sec:
            filtered.append({
                "start_sec": round(item["start_sec"], 6),
                "end_sec": round(item["end_sec"], 6),
            })
    return filtered


def _as_float(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result or result in (float("inf"), float("-inf")):
        return None
    return result
