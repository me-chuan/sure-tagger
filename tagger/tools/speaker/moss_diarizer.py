"""MOSS-Transcribe-Diarize adapter."""

import json
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
from typing import Any, Dict, List, Optional, Union
import urllib.error
import urllib.request
import wave

from tagger.tools.base import ToolResult
from tagger.tools.speaker.metrics import normalize_segments


TOOL_NAME = "moss_diarizer"
TOOL_VERSION = "moss_diarizer_v0.1.0"


class MossDiarizeError(RuntimeError):
    pass


class MossDiarizeConfig:
    def __init__(
        self,
        endpoint="",
        model="OpenMOSS-Team/MOSS-Transcribe-Diarize",
        timeout_sec=900,
        max_new_tokens=65536,
        api_key="",
    ):
        self.endpoint = endpoint or ""
        self.model = model or "OpenMOSS-Team/MOSS-Transcribe-Diarize"
        self.timeout_sec = int(timeout_sec)
        self.max_new_tokens = int(max_new_tokens)
        self.api_key = api_key or ""


def run(audio_path, duration_sec=None, context=None, config=None, client=None, **_kwargs):
    # type: (Union[str, Path], Optional[float], Optional[Dict[str, Any]], Optional[MossDiarizeConfig], Any, Any) -> ToolResult
    config = config or MossDiarizeConfig()
    if client is not None:
        payload = client.diarize(audio_path, context=context)
    else:
        payload = call_moss_http(audio_path, config)
    segments = parse_moss_output(payload)
    if duration_sec is None:
        duration_sec = _duration_from_payload(payload)
    if duration_sec is not None:
        segments = normalize_segments(segments, float(duration_sec))
    if not segments:
        raise MossDiarizeError("MOSS diarize returned no speaker segments")
    value = {
        "metadata_version": "moss_diarize_timeline_v0.1",
        "segments": segments,
        "raw_text": payload.get("text", "") if isinstance(payload, dict) else "",
    }
    return ToolResult(
        tag_path="speaker.diarization_timeline",
        value=value,
        tool_name=TOOL_NAME,
        method="moss_transcribe_diarize",
        status="estimated",
        confidence=0.85,
        tool_type="model",
        tool_version=TOOL_VERSION,
        evidence={
            "segment_count": len(segments),
            "model": config.model,
        },
    )


def run_merged_channels(audio_path, duration_sec=None, context=None, config=None, client=None, **_kwargs):
    # type: (Union[str, Path], Optional[float], Optional[Dict[str, Any]], Optional[MossDiarizeConfig], Any, Any) -> ToolResult
    config = config or MossDiarizeConfig()
    path = Path(audio_path)
    with tempfile.TemporaryDirectory(prefix="sure_tagger_moss_headset_mix_") as tmpdir:
        mixed = mixdown_multichannel_wav(path, Path(tmpdir))
        result = run(
            mixed["path"],
            duration_sec=duration_sec,
            context=context,
            config=config,
            client=client,
        )
    value = dict(result.value)
    value["metadata_version"] = "moss_diarize_merged_headset_timeline_v0.1"
    return ToolResult(
        tag_path="speaker.diarization_timeline",
        value=value,
        tool_name=TOOL_NAME,
        method="moss_transcribe_diarize_merged_headset",
        status="estimated",
        confidence=result.confidence,
        tool_type="model",
        tool_version=TOOL_VERSION,
        evidence={
            "input_channel_count": mixed["channel_count"],
            "mixdown_method": mixed["method"],
            "segment_count": len(value.get("segments", [])),
            "model": config.model,
        },
    )


def call_moss_http(audio_path, config):
    # type: (Union[str, Path], MossDiarizeConfig) -> Dict[str, Any]
    if not config.endpoint:
        raise MossDiarizeError("MOSS diarize endpoint is not configured")
    path = Path(audio_path)
    if not path.exists():
        raise MossDiarizeError("audio file does not exist: %s" % path)
    boundary = "----suretagger%s" % uuid.uuid4().hex
    fields = {
        "model": config.model,
        "response_format": "verbose_json",
        "max_new_tokens": str(config.max_new_tokens),
    }
    with path.open("rb") as source:
        file_bytes = source.read()
    body = _multipart_body(boundary, fields, "file", path.name, file_bytes)
    headers = {
        "Content-Type": "multipart/form-data; boundary=%s" % boundary,
    }
    if config.api_key:
        headers["Authorization"] = "Bearer %s" % config.api_key
    request = urllib.request.Request(
        config.endpoint,
        data=body,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_sec) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:2000]
        raise MossDiarizeError("MOSS diarize HTTP %s: %s" % (exc.code, detail))
    except urllib.error.URLError as exc:
        raise MossDiarizeError("MOSS diarize request failed: %s" % exc)
    except ValueError as exc:
        raise MossDiarizeError("MOSS diarize returned invalid JSON") from exc


def parse_moss_output(payload):
    # type: (Any) -> List[Dict[str, Any]]
    if isinstance(payload, dict):
        for key in ("segments", "speaker_segments", "diarization_segments"):
            segments = _segments_from_list(payload.get(key))
            if segments:
                return segments
        for key in ("chunks", "words"):
            segments = _segments_from_list(payload.get(key))
            if segments:
                return segments
        text = payload.get("text") or payload.get("transcript") or payload.get("output_text")
        if text:
            segments = parse_moss_text(str(text))
            if segments:
                return segments
    if isinstance(payload, list):
        segments = _segments_from_list(payload)
        if segments:
            return segments
    if isinstance(payload, str):
        return parse_moss_text(payload)
    return []


def parse_moss_text(text):
    # type: (str) -> List[Dict[str, Any]]
    text = text or ""
    patterns = [
        re.compile(
            r"\[(?P<start>[0-9:.]+)\]\s*\[(?P<speaker>[A-Za-z_]*\d+|S\d+)\]\s*(?P<text>.*?)\s*\[(?P<end>[0-9:.]+)\]",
            re.DOTALL,
        ),
        re.compile(
            r"\[(?P<start>[0-9:.]+)\s*[-,]\s*(?P<end>[0-9:.]+)\]\s*\[(?P<speaker>[A-Za-z_]*\d+|S\d+)\]\s*(?P<text>.*?)(?=\n|\Z)",
            re.DOTALL,
        ),
    ]
    segments = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            start = parse_time(match.group("start"))
            end = parse_time(match.group("end"))
            if start is None or end is None or end <= start:
                continue
            segments.append({
                "start_sec": start,
                "end_sec": end,
                "speaker_id": match.group("speaker"),
                "text": match.group("text").strip(),
            })
        if segments:
            return segments
    return []


def parse_time(value):
    # type: (str) -> Optional[float]
    raw = str(value).strip()
    if not raw:
        return None
    parts = raw.split(":")
    try:
        if len(parts) == 1:
            return float(parts[0])
        if len(parts) == 2:
            return float(parts[0]) * 60.0 + float(parts[1])
        if len(parts) == 3:
            return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
    except ValueError:
        return None
    return None


def _segments_from_list(items):
    segments = []
    if not isinstance(items, list):
        return segments
    for item in items:
        if not isinstance(item, dict):
            continue
        speaker = (
            item.get("speaker_id")
            or item.get("speaker")
            or item.get("label")
            or item.get("speaker_label")
        )
        start = item.get("start_sec", item.get("start"))
        end = item.get("end_sec", item.get("end"))
        if speaker is None or start is None or end is None:
            continue
        segment = {
            "start_sec": start,
            "end_sec": end,
            "speaker_id": speaker,
        }
        if item.get("text"):
            segment["text"] = item.get("text")
        segments.append(segment)
    return segments


def _duration_from_payload(payload):
    if not isinstance(payload, dict):
        return None
    for key in ("duration_sec", "duration"):
        try:
            value = payload.get(key)
            if value is not None:
                return float(value)
        except (TypeError, ValueError):
            return None
    return None


def _multipart_body(boundary, fields, file_field, filename, file_bytes):
    parts = []
    for name, value in fields.items():
        parts.append("--%s\r\n" % boundary)
        parts.append('Content-Disposition: form-data; name="%s"\r\n\r\n' % name)
        parts.append(str(value))
        parts.append("\r\n")
    parts.append("--%s\r\n" % boundary)
    parts.append(
        'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
        % (file_field, filename)
    )
    parts.append("Content-Type: audio/wav\r\n\r\n")
    prefix = "".join(parts).encode("utf-8")
    suffix = ("\r\n--%s--\r\n" % boundary).encode("utf-8")
    return prefix + file_bytes + suffix


def _ffprobe_audio_info(path):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=sample_rate,channels",
        "-of",
        "json",
        str(path),
    ]
    try:
        output = subprocess.check_output(command)
    except OSError as exc:
        raise MossDiarizeError("ffprobe is required for non-PCM channel split") from exc
    except subprocess.CalledProcessError as exc:
        raise MossDiarizeError("ffprobe failed for %s" % path) from exc
    payload = json.loads(output.decode("utf-8"))
    streams = payload.get("streams") or []
    if not streams:
        raise MossDiarizeError("ffprobe found no audio stream: %s" % path)
    return streams[0]


def mixdown_multichannel_wav(audio_path, output_dir):
    # type: (Union[str, Path], Path) -> Dict[str, Any]
    path = Path(audio_path)
    try:
        return _mixdown_multichannel_wav_python(path, output_dir)
    except wave.Error:
        return _mixdown_multichannel_wav_ffmpeg(path, output_dir)


def _mixdown_multichannel_wav_python(path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / ("%s.merged_mono.wav" % path.stem)
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        if channels < 2:
            raise MossDiarizeError("merged-headset MOSS requires at least two channels")
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        if sample_width not in (1, 2, 4):
            raise MossDiarizeError("unsupported sample width for headset mixdown: %s" % sample_width)
        with wave.open(str(output_path), "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(sample_width)
            writer.setframerate(sample_rate)
            frame_size = channels * sample_width
            while True:
                raw = source.readframes(16000)
                if not raw:
                    break
                frame_count = len(raw) // frame_size
                out = bytearray(frame_count * sample_width)
                for frame_index in range(frame_count):
                    total = 0
                    for channel_index in range(channels):
                        offset = frame_index * frame_size + channel_index * sample_width
                        total += _read_pcm_sample(raw, offset, sample_width)
                    mixed = int(round(float(total) / float(channels)))
                    target = frame_index * sample_width
                    out[target:target + sample_width] = _write_pcm_sample(mixed, sample_width)
                writer.writeframes(out)
    return {
        "path": output_path,
        "channel_count": channels,
        "sample_rate_hz": sample_rate,
        "method": "mean_channels_python_wave",
    }


def _mixdown_multichannel_wav_ffmpeg(path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    info = _ffprobe_audio_info(path)
    channels = int(info["channels"])
    sample_rate = int(info["sample_rate"])
    if channels < 2:
        raise MossDiarizeError("merged-headset MOSS requires at least two channels")
    output_path = output_dir / ("%s.merged_mono.wav" % path.stem)
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(path),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(output_path),
    ]
    try:
        subprocess.check_call(command)
    except OSError as exc:
        raise MossDiarizeError("ffmpeg is required for non-PCM headset mixdown") from exc
    except subprocess.CalledProcessError as exc:
        raise MossDiarizeError("ffmpeg headset mixdown failed for %s" % path) from exc
    return {
        "path": output_path,
        "channel_count": channels,
        "sample_rate_hz": sample_rate,
        "method": "ffmpeg_downmix_mono",
    }


def _read_pcm_sample(raw, offset, sample_width):
    if sample_width == 1:
        return int(raw[offset]) - 128
    return int.from_bytes(raw[offset:offset + sample_width], "little", signed=True)


def _write_pcm_sample(value, sample_width):
    if sample_width == 1:
        value = max(-128, min(127, int(value)))
        return bytes([value + 128])
    if sample_width == 2:
        value = max(-32768, min(32767, int(value)))
        return int(value).to_bytes(2, "little", signed=True)
    if sample_width == 4:
        value = max(-2147483648, min(2147483647, int(value)))
        return int(value).to_bytes(4, "little", signed=True)
    raise MossDiarizeError("unsupported sample width for headset mixdown: %s" % sample_width)
