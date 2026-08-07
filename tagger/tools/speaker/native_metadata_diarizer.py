"""Deterministic speaker timeline from native metadata segments."""

from typing import Any, Dict, List

from tagger.tools.base import ToolResult
from tagger.tools.speaker.metrics import normalize_segments


TOOL_NAME = "native_metadata_speaker_diarizer"
TOOL_VERSION = "native_metadata_speaker_diarizer_v0.1.0"
METHOD = "native_metadata_speaker_segments"


class NativeMetadataSpeakerError(ValueError):
    pass


def run(sample, duration_sec, context=None, config=None, **_kwargs):
    # type: (Dict[str, Any], float, object, object) -> ToolResult
    del context
    if duration_sec is None or duration_sec <= 0:
        raise NativeMetadataSpeakerError("duration_sec must be positive")
    segments, source_key = speaker_segments_from_native_metadata(
        sample,
        duration_sec,
        config=config,
    )
    if not segments:
        raise NativeMetadataSpeakerError("no native metadata speaker segments found")
    return ToolResult(
        tag_path="speaker.diarization_timeline",
        value={
            "metadata_version": "native_metadata_speaker_timeline_v0.1",
            "segments": segments,
            "source_key": source_key,
        },
        tool_name=TOOL_NAME,
        method=METHOD,
        status="observed",
        confidence=1.0,
        tool_type="deterministic",
        tool_version=TOOL_VERSION,
        evidence={
            "source": "sample.native_metadata.%s" % source_key,
            "segment_count": len(segments),
        },
    )


def speaker_segments_from_native_metadata(sample, duration_sec, config=None):
    native_metadata = sample.get("native_metadata", {})
    if not isinstance(native_metadata, dict):
        raise NativeMetadataSpeakerError("sample.native_metadata must be an object")

    for key in (
        "speaker_segments",
        "diarization_segments",
        "segments",
        "utterances",
    ):
        value = native_metadata.get(key)
        if not isinstance(value, list):
            continue
        raw_segments = _segments_from_list(value, native_metadata, key)
        if not raw_segments:
            continue
        segments = normalize_segments(raw_segments, duration_sec, config=config)
        if segments:
            return segments, key

    raise NativeMetadataSpeakerError("no native metadata speaker segments found")


def _segments_from_list(items, native_metadata, key):
    parsed = []
    for item in items:
        segment = _parse_segment(item)
        if segment is None:
            continue
        parsed.append(segment)
    if not parsed:
        return []

    parent_start = _as_float(native_metadata.get("start_sec", native_metadata.get("start")))
    sample_duration = _sample_duration(native_metadata)
    if sample_duration is not None and parent_start is not None:
        if not _segments_fit_duration(parsed, sample_duration):
            shifted = []
            for item in parsed:
                shifted_item = dict(item)
                shifted_item["start_sec"] = item["start_sec"] - parent_start
                shifted_item["end_sec"] = item["end_sec"] - parent_start
                shifted.append(shifted_item)
            if _segments_fit_duration(shifted, sample_duration):
                parsed = shifted

    if key == "utterances":
        return _merge_adjacent_same_speaker(parsed)
    return parsed


def _parse_segment(item):
    if not isinstance(item, dict):
        return None
    speaker_id = (
        item.get("speaker_id")
        or item.get("speaker")
        or item.get("label")
        or item.get("spk")
    )
    if speaker_id is None:
        return None
    start = _as_float(item.get("start_sec", item.get("start")))
    end = _as_float(item.get("end_sec", item.get("end")))
    if start is None or end is None or end <= start:
        return None
    segment = {
        "start_sec": start,
        "end_sec": end,
        "speaker_id": speaker_id,
    }
    if item.get("source_channel_id") is not None:
        segment["source_channel_id"] = str(item.get("source_channel_id"))
    if item.get("text"):
        segment["text"] = str(item.get("text"))
    return segment


def _merge_adjacent_same_speaker(segments):
    result = []  # type: List[Dict[str, Any]]
    for item in sorted(segments, key=lambda row: (row["start_sec"], row["end_sec"])):
        if (
            result
            and str(result[-1]["speaker_id"]) == str(item["speaker_id"])
            and item["start_sec"] <= result[-1]["end_sec"]
        ):
            result[-1]["end_sec"] = max(result[-1]["end_sec"], item["end_sec"])
            if item.get("text"):
                result[-1]["text"] = " ".join(
                    [result[-1].get("text", ""), item.get("text", "")]
                ).strip()
        else:
            result.append(dict(item))
    return result


def _sample_duration(native_metadata):
    start = _as_float(native_metadata.get("start_sec", native_metadata.get("start")))
    end = _as_float(native_metadata.get("end_sec", native_metadata.get("end")))
    if start is not None and end is not None and end > start:
        return end - start
    duration = _as_float(native_metadata.get("duration_sec", native_metadata.get("duration")))
    if duration is not None and duration > 0:
        return duration
    return None


def _segments_fit_duration(segments, duration_sec):
    for item in segments:
        if item["start_sec"] < -1e-6 or item["end_sec"] > duration_sec + 1e-6:
            return False
    return True


def _as_float(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result or result in (float("inf"), float("-inf")):
        return None
    return result
