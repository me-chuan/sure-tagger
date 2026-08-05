"""Sample-level signal and sound-field tagging pipeline.

Input records must match the closed raw-only schema in development.md. Public
output is tags-only and contains only tag values.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union

from tagger.input_schema import InputSchemaError, validate_input_record
from tagger.tools.base import ToolResult
from tagger.tools.subprocess_runner import close_subprocess_workers
from tagger.tools.basic_acoustic.brouhaha_signal_estimator import BrouhahaConfig
from tagger.tools.basic_acoustic.dnsmos_quality_estimator import DnsmosConfig
from tagger.tools.basic_acoustic.firered_vad_silence_detector import FireRedVadConfig
from tagger.tools.basic_acoustic.registry import (
    AUDIO_PROBE_TOOL,
    BROUHAHA_ACOUSTIC_TOOL,
    DNSMOS_QUALITY_TOOL,
    FIRERED_VAD_SILENCE_TOOL,
    SILENCE_RATIO_TOOL,
)
from tagger.tools.sound_field_scene.registry import (
    C50_TOOL,
    FIRERED_AED_TOOL,
    RECRIR_RIR_TOOL,
    RT60_TOOL,
)
from tagger.tools.sound_field_scene.firered_aed_detector import FireRedAedConfig
from tagger.tools.sound_field_scene.rir_estimator import (
    RecRirConfig,
    validate_rir_payload,
)


BASIC_ACOUSTIC_FIELDS = {
    "duration_sec": None,
    "sample_rate_hz": None,
    "channels": None,
    "silence_ratio": None,
    "silence_segments": None,
    "snr_db": None,
    "c50": None,
    "dnsmos_sig": None,
    "dnsmos_bak": None,
    "dnsmos_ovrl": None,
    "dnsmos_p808": None,
}

SOUND_FIELD_SCENE_FIELDS = {
    "far_field": None,
    "rt60": None,
    "c50": None,
    "music": None,
    "sound": None,
}

SPEAKER_FIELDS = {
    "multi_speaker": None,
    "speaker_change": None,
    "speaker_overlap": None,
}

LANGUAGE_CONTENT_FIELDS = {
    "topic": None,
    "language": None,
    "word_count": None,
    "punctuation": None,
    "repetition": None,
    "filler": None,
}

def run_manifest(
    manifest_path,
    output_path,
    firered_vad_config=None,
    brouhaha_config=None,
    recrir_config=None,
    artifact_dir=None,
    dnsmos_config=None,
    firered_aed_config=None,
):
    # type: (Union[str, Path], Union[str, Path], Optional[FireRedVadConfig], Optional[BrouhahaConfig], Optional[RecRirConfig], Optional[Union[str, Path]], Optional[DnsmosConfig], Optional[FireRedAedConfig]) -> Dict[str, Any]
    manifest = Path(manifest_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    artifact_root = _resolve_artifact_root(output, artifact_dir)

    count = 0
    internal_warning_count = 0
    tool_context = {}  # type: Dict[str, Any]
    try:
        with manifest.open("r", encoding="utf-8") as source, output.open(
            "w", encoding="utf-8"
        ) as sink:
            for row_index, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                try:
                    internal = _tag_record_internal(
                        record,
                        manifest_dir=manifest.parent,
                        firered_vad_config=firered_vad_config,
                        brouhaha_config=brouhaha_config,
                        recrir_config=recrir_config,
                        dnsmos_config=dnsmos_config,
                        firered_aed_config=firered_aed_config,
                        artifact_dir=artifact_root,
                        artifact_record_index=row_index,
                        tool_context=tool_context,
                    )
                except InputSchemaError as exc:
                    raise InputSchemaError("line %s: %s" % (row_index, exc))
                internal_warning_count += len(internal["warnings"])
                sink.write(
                    json.dumps(internal["tags"], ensure_ascii=False, sort_keys=True)
                    + "\n"
                )
                count += 1
    finally:
        close_subprocess_workers(tool_context)

    return {
        "manifest_path": str(manifest),
        "output_path": str(output),
        "artifact_dir": str(artifact_root),
        "sample_count": count,
        "internal_warning_count": internal_warning_count,
    }


def tag_record(
    record,
    manifest_dir,
    firered_vad_config=None,
    brouhaha_config=None,
    recrir_config=None,
    recrir_client=None,
    artifact_dir=None,
    dnsmos_config=None,
    dnsmos_client=None,
    firered_aed_config=None,
    firered_aed_client=None,
):
    # type: (Dict[str, Any], Union[str, Path], Optional[FireRedVadConfig], Optional[BrouhahaConfig], Optional[RecRirConfig], Any, Optional[Union[str, Path]], Optional[DnsmosConfig], Any, Optional[FireRedAedConfig], Any) -> Dict[str, Any]
    return _tag_record_internal(
        record,
        manifest_dir,
        firered_vad_config=firered_vad_config,
        brouhaha_config=brouhaha_config,
        recrir_config=recrir_config,
        recrir_client=recrir_client,
        artifact_dir=artifact_dir,
        dnsmos_config=dnsmos_config,
        dnsmos_client=dnsmos_client,
        firered_aed_config=firered_aed_config,
        firered_aed_client=firered_aed_client,
    )["tags"]


def _tag_record_internal(
    record,
    manifest_dir,
    firered_vad_config=None,
    brouhaha_config=None,
    recrir_config=None,
    recrir_client=None,
    artifact_dir=None,
    artifact_record_index=None,
    tool_context=None,
    dnsmos_config=None,
    dnsmos_client=None,
    firered_aed_config=None,
    firered_aed_client=None,
):
    # type: (Dict[str, Any], Union[str, Path], Optional[FireRedVadConfig], Optional[BrouhahaConfig], Optional[RecRirConfig], Any, Optional[Union[str, Path]], Optional[int], Optional[Dict[str, Any]], Optional[DnsmosConfig], Any, Optional[FireRedAedConfig], Any) -> Dict[str, Any]
    validate_input_record(record)
    sample = record["sample"]
    sample_id = sample["sample_id"]
    audio_path = resolve_audio_path(sample, manifest_dir)

    tags = empty_tags()
    internal_results = []  # type: List[Dict[str, Any]]
    warnings = []  # type: List[Dict[str, Any]]

    if audio_path is None:
        warnings.append(
            {
                "type": "missing_audio_path",
                "message": "sample.audio.path is empty",
                "sample_id": sample_id,
            }
        )
    elif not audio_path.exists():
        warnings.append(
            {
                "type": "missing_audio_file",
                "message": "audio file does not exist",
                "sample_id": sample_id,
                "audio_path": str(audio_path),
            }
        )
    else:
        tool_context = tool_context if tool_context is not None else {}
        _run_signal_probe(
            audio_path,
            tool_context,
            tags,
            internal_results,
            warnings,
            sample_id,
        )
        _run_silence_tools(
            audio_path,
            tool_context,
            tags,
            internal_results,
            warnings,
            sample_id,
            firered_vad_config=firered_vad_config,
        )
        _run_brouhaha_tool(
            audio_path,
            tool_context,
            tags,
            internal_results,
            warnings,
            sample_id,
            brouhaha_config=brouhaha_config,
        )
        _run_dnsmos_tool(
            audio_path,
            tool_context,
            tags,
            internal_results,
            warnings,
            sample_id,
            dnsmos_config=dnsmos_config,
            dnsmos_client=dnsmos_client,
        )
        _run_firered_aed_tool(
            audio_path,
            tool_context,
            tags,
            internal_results,
            warnings,
            sample_id,
            firered_aed_config=firered_aed_config,
            firered_aed_client=firered_aed_client,
        )
        _run_recrir_tools(
            audio_path,
            tool_context,
            tags,
            internal_results,
            warnings,
            sample_id,
            recrir_config=recrir_config,
            recrir_client=recrir_client,
            artifact_dir=artifact_dir,
            artifact_record_index=artifact_record_index,
        )

    warnings.extend(
        compare_native_metadata_basic_acoustic_fields(sample, tags["basic_acoustic"])
    )
    warnings.extend(
        compare_native_metadata_sound_field_scene_fields(
            sample,
            tags["sound_field_scene"],
        )
    )
    warnings.extend(audit_basic_acoustic(tags["basic_acoustic"]))
    warnings.extend(audit_sound_field_scene(tags["sound_field_scene"]))

    return {
        "tags": tags,
        "internal_results": internal_results,
        "warnings": warnings,
    }


def empty_tags():
    # type: () -> Dict[str, Any]
    return {
        "basic_acoustic": dict(BASIC_ACOUSTIC_FIELDS),
        "sound_field_scene": dict(SOUND_FIELD_SCENE_FIELDS),
        "speaker": dict(SPEAKER_FIELDS),
        "language_content": dict(LANGUAGE_CONTENT_FIELDS),
    }


def resolve_audio_path(sample, manifest_dir):
    # type: (Dict[str, Any], Union[str, Path]) -> Optional[Path]
    raw_path = sample["audio"]["path"]
    if not raw_path:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path

    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path

    manifest_path = Path(manifest_dir) / path
    if manifest_path.exists():
        return manifest_path

    return cwd_path


def apply_result(tags, internal_results, result):
    # type: (Dict[str, Any], List[Dict[str, Any]], ToolResult) -> None
    prefix, field = result.tag_path.split(".", 1)
    tags[prefix][field] = result.value
    internal_results.append(result.to_record())


def _run_signal_probe(
    audio_path,
    tool_context,
    tags,
    internal_results,
    warnings,
    sample_id,
):
    try:
        results = AUDIO_PROBE_TOOL["run"](audio_path, context=tool_context)
        for result in results:
            apply_result(tags, internal_results, result)
    except Exception as exc:  # noqa: BLE001 - tool failures become internal warnings.
        warnings.append(
            {
                "type": "basic_acoustic_tool_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": AUDIO_PROBE_TOOL["tool_name"],
            }
        )
        for field in ("duration_sec", "sample_rate_hz", "channels"):
            tags["basic_acoustic"][field] = None


def _run_silence_tools(
    audio_path,
    tool_context,
    tags,
    internal_results,
    warnings,
    sample_id,
    firered_vad_config=None,
):
    duration_sec = tags["basic_acoustic"]["duration_sec"]
    if duration_sec is None or duration_sec <= 0:
        warnings.append(
            {
                "type": "invalid_duration_for_silence",
                "message": "duration_sec must be positive before FireRed VAD",
                "sample_id": sample_id,
                "audio_path": str(audio_path),
            }
        )
        tags["basic_acoustic"]["silence_segments"] = None
        tags["basic_acoustic"]["silence_ratio"] = None
        return

    try:
        silence_result = FIRERED_VAD_SILENCE_TOOL["run"](
            audio_path,
            duration_sec=duration_sec,
            context=tool_context,
            config=firered_vad_config,
        )
        apply_result(tags, internal_results, silence_result)
    except Exception as exc:  # noqa: BLE001 - no non-FireRed fallback is allowed.
        warnings.append(
            {
                "type": "firered_vad_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": FIRERED_VAD_SILENCE_TOOL["tool_name"],
            }
        )
        tags["basic_acoustic"]["silence_segments"] = None
        tags["basic_acoustic"]["silence_ratio"] = None
        return

    try:
        ratio_result = SILENCE_RATIO_TOOL["run"](
            tags["basic_acoustic"]["silence_segments"],
            duration_sec=duration_sec,
        )
        apply_result(tags, internal_results, ratio_result)
    except Exception as exc:  # noqa: BLE001 - invalid FireRed output nulls both silence tags.
        warnings.append(
            {
                "type": "silence_ratio_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": SILENCE_RATIO_TOOL["tool_name"],
            }
        )
        tags["basic_acoustic"]["silence_segments"] = None
        tags["basic_acoustic"]["silence_ratio"] = None


def _run_brouhaha_tool(
    audio_path,
    tool_context,
    tags,
    internal_results,
    warnings,
    sample_id,
    brouhaha_config=None,
):
    try:
        results = BROUHAHA_ACOUSTIC_TOOL["run"](
            audio_path,
            context=tool_context,
            config=brouhaha_config,
        )
        for result in results:
            apply_result(tags, internal_results, result)
            if result.status != "estimated":
                warnings.append(
                    {
                        "type": "brouhaha_output_invalid",
                        "message": result.evidence.get("error", "invalid output"),
                        "sample_id": sample_id,
                        "audio_path": str(audio_path),
                        "tool_name": BROUHAHA_ACOUSTIC_TOOL["tool_name"],
                        "field": result.tag_path,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - no non-Brouhaha fallback is allowed.
        warnings.append(
            {
                "type": "brouhaha_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": BROUHAHA_ACOUSTIC_TOOL["tool_name"],
            }
        )
        tags["basic_acoustic"]["snr_db"] = None
        tags["basic_acoustic"]["c50"] = None


def _run_dnsmos_tool(
    audio_path,
    tool_context,
    tags,
    internal_results,
    warnings,
    sample_id,
    dnsmos_config=None,
    dnsmos_client=None,
):
    try:
        results = DNSMOS_QUALITY_TOOL["run"](
            audio_path,
            context=tool_context,
            config=dnsmos_config,
            client=dnsmos_client,
        )
        for result in results:
            apply_result(tags, internal_results, result)
            if result.status != "estimated":
                warnings.append(
                    {
                        "type": "dnsmos_output_invalid",
                        "message": result.evidence.get("error", "invalid output"),
                        "sample_id": sample_id,
                        "audio_path": str(audio_path),
                        "tool_name": DNSMOS_QUALITY_TOOL["tool_name"],
                        "field": result.tag_path,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - no non-DNSMOS fallback is allowed.
        warnings.append(
            {
                "type": "dnsmos_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": DNSMOS_QUALITY_TOOL["tool_name"],
            }
        )
        _null_dnsmos_tags(tags)


def _run_firered_aed_tool(
    audio_path,
    tool_context,
    tags,
    internal_results,
    warnings,
    sample_id,
    firered_aed_config=None,
    firered_aed_client=None,
):
    duration_sec = tags["basic_acoustic"]["duration_sec"]
    if duration_sec is None or duration_sec <= 0:
        warnings.append(
            {
                "type": "invalid_duration_for_firered_aed",
                "message": "duration_sec must be positive before FireRed AED",
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": FIRERED_AED_TOOL["tool_name"],
            }
        )
        _null_firered_aed_tags(tags)
        return

    try:
        results = FIRERED_AED_TOOL["run"](
            audio_path,
            duration_sec=duration_sec,
            context=tool_context,
            config=firered_aed_config,
            client=firered_aed_client,
        )
        for result in results:
            apply_result(tags, internal_results, result)
    except Exception as exc:  # noqa: BLE001 - no non-FireRed fallback is allowed.
        warnings.append(
            {
                "type": "firered_aed_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": FIRERED_AED_TOOL["tool_name"],
            }
        )
        _null_firered_aed_tags(tags)


def _run_recrir_tools(
    audio_path,
    tool_context,
    tags,
    internal_results,
    warnings,
    sample_id,
    recrir_config=None,
    recrir_client=None,
    artifact_dir=None,
    artifact_record_index=None,
):
    try:
        rir_result = RECRIR_RIR_TOOL["run"](
            audio_path,
            context=tool_context,
            config=recrir_config,
            client=recrir_client,
        )
        internal_results.append(rir_result.to_record())
        if rir_result.status != "estimated" or rir_result.value is None:
            warnings.append(
                {
                    "type": "recrir_output_invalid",
                    "message": rir_result.evidence.get("error", "invalid output"),
                    "sample_id": sample_id,
                    "audio_path": str(audio_path),
                    "tool_name": RECRIR_RIR_TOOL["tool_name"],
                    "field": rir_result.tag_path,
                }
            )
            _null_rir_related_tags(tags)
            return
    except Exception as exc:  # noqa: BLE001 - no non-Rec-RIR fallback is allowed.
        warnings.append(
            {
                "type": "recrir_error",
                "message": str(exc),
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "tool_name": RECRIR_RIR_TOOL["tool_name"],
            }
        )
        _null_rir_related_tags(tags)
        return

    rir_payload = rir_result.value
    if artifact_dir is not None:
        try:
            artifact_path = write_rir_artifact(
                rir_payload,
                Path(artifact_dir) / "rir",
                _artifact_sample_key(sample_id, artifact_record_index),
            )
            internal_results[-1]["evidence"]["artifact_path"] = str(artifact_path)
            internal_results[-1]["evidence"]["artifact_format"] = "json.gz"
        except Exception as exc:  # noqa: BLE001 - artifact failure is internal.
            warnings.append(
                {
                    "type": "rir_artifact_write_error",
                    "message": str(exc),
                    "sample_id": sample_id,
                    "audio_path": str(audio_path),
                    "tool_name": RECRIR_RIR_TOOL["tool_name"],
                }
            )

    for tool, field in ((RT60_TOOL, "rt60"), (C50_TOOL, "c50")):
        try:
            result = tool["run"](
                rir_payload,
                context=tool_context,
            )
            apply_result(tags, internal_results, result)
        except Exception as exc:  # noqa: BLE001 - derived RIR tag failure is internal.
            warnings.append(
                {
                    "type": "rir_derived_tool_error",
                    "message": str(exc),
                    "sample_id": sample_id,
                    "audio_path": str(audio_path),
                    "tool_name": tool["tool_name"],
                    "field": tool["tag_path"],
                }
            )
            tags["sound_field_scene"][field] = None


def _null_rir_related_tags(tags):
    tags["sound_field_scene"]["rt60"] = None
    tags["sound_field_scene"]["c50"] = None


def _null_dnsmos_tags(tags):
    for field in ("dnsmos_sig", "dnsmos_bak", "dnsmos_ovrl", "dnsmos_p808"):
        tags["basic_acoustic"][field] = None


def _null_firered_aed_tags(tags):
    tags["sound_field_scene"]["music"] = None
    tags["sound_field_scene"]["sound"] = None


def write_rir_artifact(rir_payload, artifact_dir, sample_key):
    # type: (Dict[str, Any], Union[str, Path], str) -> Path
    payload = validate_rir_payload(rir_payload)
    directory = Path(artifact_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("%s.rir.json.gz" % _safe_artifact_stem(sample_key))
    with gzip.open(str(path), "wt", encoding="utf-8") as sink:
        json.dump(payload, sink, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return path


def _resolve_artifact_root(output_path, artifact_dir):
    # type: (Path, Optional[Union[str, Path]]) -> Path
    if artifact_dir is not None:
        return Path(artifact_dir)
    return output_path.parent / "artifacts"


def _artifact_sample_key(sample_id, record_index):
    # type: (str, Optional[int]) -> str
    if record_index is None:
        return sample_id
    return "%06d_%s" % (record_index, sample_id)


def _safe_artifact_stem(value):
    # type: (str) -> str
    raw = str(value)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._-")
    if not stem:
        stem = "sample"
    if len(stem) > 160:
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
        stem = "%s_%s" % (stem[:147].rstrip("._-"), digest)
    return stem


def compare_native_metadata_basic_acoustic_fields(sample, observed_basic_acoustic):
    # type: (Dict[str, Any], Dict[str, Any]) -> List[Dict[str, Any]]
    native_metadata = sample.get("native_metadata", {})
    warnings = []  # type: List[Dict[str, Any]]
    comparisons = [
        ("duration_sec", 1e-3),
        ("sample_rate_hz", 0),
        ("channels", 0),
        ("silence_ratio", 1e-6),
        ("silence_segments", None),
        ("snr_db", 1e-6),
        ("c50", 1e-6),
        ("dnsmos_sig", 1e-6),
        ("dnsmos_bak", 1e-6),
        ("dnsmos_ovrl", 1e-6),
        ("dnsmos_p808", 1e-6),
    ]
    for field, tolerance in comparisons:
        native_value = native_metadata.get(field)
        observed_value = observed_basic_acoustic.get(field)
        if native_value is None or observed_value is None:
            continue
        if (
            tolerance is not None
            and isinstance(native_value, (int, float))
            and isinstance(observed_value, (int, float))
        ):
            mismatch = abs(float(native_value) - float(observed_value)) > tolerance
        else:
            mismatch = native_value != observed_value
        if mismatch:
            warnings.append(
                {
                    "type": "native_metadata_basic_acoustic_mismatch",
                    "field": field,
                    "native_metadata_value": native_value,
                    "observed_value": observed_value,
                    "message": "observed basic acoustic value differs from native metadata",
                }
            )
    return warnings


def compare_native_metadata_sound_field_scene_fields(sample, observed_sound_field):
    # type: (Dict[str, Any], Dict[str, Any]) -> List[Dict[str, Any]]
    native_metadata = sample.get("native_metadata", {})
    warnings = []  # type: List[Dict[str, Any]]
    comparisons = [
        ("far_field", None),
        ("rt60", 1e-6),
        ("c50", 1e-6),
        ("music", None),
        ("sound", None),
    ]
    for field, tolerance in comparisons:
        native_value = native_metadata.get(field)
        observed_value = observed_sound_field.get(field)
        if native_value is None or observed_value is None:
            continue
        if (
            tolerance is not None
            and isinstance(native_value, (int, float))
            and isinstance(observed_value, (int, float))
        ):
            mismatch = abs(float(native_value) - float(observed_value)) > tolerance
        else:
            mismatch = native_value != observed_value
        if mismatch:
            warnings.append(
                {
                    "type": "native_metadata_sound_field_scene_mismatch",
                    "field": field,
                    "native_metadata_value": native_value,
                    "observed_value": observed_value,
                    "message": "observed sound-field value differs from native metadata",
                }
            )
    return warnings


def audit_basic_acoustic(basic_acoustic):
    # type: (Dict[str, Any]) -> List[Dict[str, Any]]
    warnings = []  # type: List[Dict[str, Any]]
    duration_sec = basic_acoustic.get("duration_sec")
    sample_rate_hz = basic_acoustic.get("sample_rate_hz")
    channels = basic_acoustic.get("channels")
    silence_ratio = basic_acoustic.get("silence_ratio")
    silence_segments = basic_acoustic.get("silence_segments")
    snr_db = basic_acoustic.get("snr_db")
    c50 = basic_acoustic.get("c50")

    if duration_sec is not None and (
        isinstance(duration_sec, bool)
        or not isinstance(duration_sec, (int, float))
        or not _is_finite_number(duration_sec)
        or duration_sec < 0
    ):
        basic_acoustic["duration_sec"] = None
        warnings.append(
            {"type": "invalid_basic_acoustic_value", "field": "duration_sec"}
        )

    if sample_rate_hz is not None and (
        isinstance(sample_rate_hz, bool)
        or not isinstance(sample_rate_hz, int)
        or sample_rate_hz <= 0
    ):
        basic_acoustic["sample_rate_hz"] = None
        warnings.append(
            {"type": "invalid_basic_acoustic_value", "field": "sample_rate_hz"}
        )

    if channels is not None and (
        isinstance(channels, bool) or not isinstance(channels, int) or channels <= 0
    ):
        basic_acoustic["channels"] = None
        warnings.append(
            {"type": "invalid_basic_acoustic_value", "field": "channels"}
        )

    if silence_ratio is not None and (
        isinstance(silence_ratio, bool)
        or not isinstance(silence_ratio, (int, float))
        or not _is_finite_number(silence_ratio)
        or silence_ratio < 0
        or silence_ratio > 1
    ):
        basic_acoustic["silence_ratio"] = None
        basic_acoustic["silence_segments"] = None
        warnings.append(
            {"type": "invalid_basic_acoustic_value", "field": "silence_ratio"}
        )

    if silence_segments is not None:
        if not _is_valid_silence_segments(
            silence_segments,
            basic_acoustic.get("duration_sec"),
        ):
            basic_acoustic["silence_ratio"] = None
            basic_acoustic["silence_segments"] = None
            warnings.append(
                {
                    "type": "invalid_basic_acoustic_value",
                    "field": "silence_segments",
                }
            )

    if snr_db is not None and (
        isinstance(snr_db, bool)
        or not isinstance(snr_db, (int, float))
        or not _is_finite_number(snr_db)
    ):
        basic_acoustic["snr_db"] = None
        warnings.append({"type": "invalid_basic_acoustic_value", "field": "snr_db"})

    if c50 is not None and (
        isinstance(c50, bool)
        or not isinstance(c50, (int, float))
        or not _is_finite_number(c50)
    ):
        basic_acoustic["c50"] = None
        warnings.append({"type": "invalid_basic_acoustic_value", "field": "c50"})

    for field in ("dnsmos_sig", "dnsmos_bak", "dnsmos_ovrl", "dnsmos_p808"):
        value = basic_acoustic.get(field)
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not _is_finite_number(value)
            or value < 1.0
            or value > 5.0
        ):
            basic_acoustic[field] = None
            warnings.append(
                {"type": "invalid_basic_acoustic_value", "field": field}
            )

    return warnings


def audit_sound_field_scene(sound_field_scene):
    # type: (Dict[str, Any]) -> List[Dict[str, Any]]
    warnings = []  # type: List[Dict[str, Any]]

    for field in ("far_field", "music", "sound"):
        value = sound_field_scene.get(field)
        if value is not None and not isinstance(value, bool):
            sound_field_scene[field] = None
            warnings.append(
                {"type": "invalid_sound_field_scene_value", "field": field}
            )

    rt60 = sound_field_scene.get("rt60")
    if rt60 is not None and (
        isinstance(rt60, bool)
        or not isinstance(rt60, (int, float))
        or not _is_finite_number(rt60)
        or rt60 < 0
    ):
        sound_field_scene["rt60"] = None
        warnings.append({"type": "invalid_sound_field_scene_value", "field": "rt60"})

    c50 = sound_field_scene.get("c50")
    if c50 is not None and (
        isinstance(c50, bool)
        or not isinstance(c50, (int, float))
        or not _is_finite_number(c50)
    ):
        sound_field_scene["c50"] = None
        warnings.append({"type": "invalid_sound_field_scene_value", "field": "c50"})

    return warnings


def _is_valid_silence_segments(segments, duration_sec):
    if (
        duration_sec is None
        or duration_sec <= 0
        or not _is_finite_number(duration_sec)
        or not isinstance(segments, list)
    ):
        return False

    previous_end = None
    for segment in segments:
        if not isinstance(segment, dict):
            return False
        if set(segment.keys()) != set(["start_sec", "end_sec"]):
            return False
        start_sec = segment["start_sec"]
        end_sec = segment["end_sec"]
        if isinstance(start_sec, bool) or isinstance(end_sec, bool):
            return False
        if not isinstance(start_sec, (int, float)) or not isinstance(
            end_sec, (int, float)
        ):
            return False
        if not _is_finite_number(start_sec) or not _is_finite_number(end_sec):
            return False
        if start_sec < 0 or start_sec >= end_sec or end_sec > duration_sec:
            return False
        if previous_end is not None and start_sec < previous_end:
            return False
        previous_end = end_sec
    return True


def _is_finite_number(value):
    return value == value and value not in (float("inf"), float("-inf"))


def build_arg_parser():
    # type: () -> argparse.ArgumentParser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="phase1_asr_samples/manifest.jsonl",
        help="Input JSONL manifest using the closed raw-only schema.",
    )
    parser.add_argument(
        "--output",
        default="phase1_asr_samples/outputs/sample_tags.jsonl",
        help="Output tags-only JSONL path for sample tags.",
    )
    parser.add_argument(
        "--firered-vad-use-gpu",
        action="store_true",
        help="Use GPU in FireRedVAD config. Defaults to CPU.",
    )
    parser.add_argument(
        "--firered-aed-use-gpu",
        action="store_true",
        help="Use GPU in FireRed AED config. Defaults to CPU.",
    )
    parser.add_argument(
        "--brouhaha-use-gpu",
        action="store_true",
        help="Use GPU in Brouhaha config. Defaults to CPU when supported.",
    )
    parser.add_argument(
        "--recrir-use-gpu",
        action="store_true",
        help="Use GPU in Rec-RIR config. Defaults to CPU when supported.",
    )
    parser.add_argument(
        "--firered-vad-python",
        default=None,
        help="Python executable for FireRed VAD subprocess. Defaults to local_config.py.",
    )
    parser.add_argument(
        "--firered-aed-python",
        default=None,
        help="Python executable for FireRed AED subprocess. Defaults to local_config.py.",
    )
    parser.add_argument(
        "--brouhaha-python",
        default=None,
        help="Python executable for Brouhaha subprocess. Defaults to local_config.py.",
    )
    parser.add_argument(
        "--recrir-python",
        default=None,
        help="Python executable for Rec-RIR subprocess. Defaults to local_config.py.",
    )
    parser.add_argument(
        "--dnsmos-python",
        default=None,
        help="Python executable for DNSMOS subprocess. Defaults to local_config.py.",
    )
    parser.add_argument(
        "--dnsmos-personalized",
        action="store_true",
        help="Use the personalized DNSMOS primary model. Defaults to regular DNSMOS.",
    )
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help=(
            "Directory for non-public artifacts such as Rec-RIR waveforms. "
            "Defaults to OUTPUT_PARENT/artifacts."
        ),
    )
    return parser


def main(argv=None):
    # type: (Optional[List[str]]) -> int
    args = build_arg_parser().parse_args(argv)
    firered_vad_config = FireRedVadConfig(
        use_gpu=args.firered_vad_use_gpu,
        subprocess_python=args.firered_vad_python,
    )
    firered_aed_config = FireRedAedConfig(
        use_gpu=args.firered_aed_use_gpu,
        subprocess_python=args.firered_aed_python,
    )
    brouhaha_config = BrouhahaConfig(
        use_gpu=args.brouhaha_use_gpu,
        subprocess_python=args.brouhaha_python,
    )
    recrir_config = RecRirConfig(
        use_gpu=args.recrir_use_gpu,
        subprocess_python=args.recrir_python,
    )
    dnsmos_config = DnsmosConfig(
        personalized=args.dnsmos_personalized,
        subprocess_python=args.dnsmos_python,
    )
    summary = run_manifest(
        args.manifest,
        args.output,
        firered_vad_config=firered_vad_config,
        brouhaha_config=brouhaha_config,
        recrir_config=recrir_config,
        artifact_dir=args.artifact_dir,
        dnsmos_config=dnsmos_config,
        firered_aed_config=firered_aed_config,
    )
    public_summary = {
        "output_path": summary["output_path"],
        "sample_count": summary["sample_count"],
    }
    print(json.dumps(public_summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
