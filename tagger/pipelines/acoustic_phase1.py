"""Phase 1 deterministic acoustic tagging pipeline.

Input records must match the closed raw-only schema in AGENTS.md. The output
JSONL is tags-only: no sample id, evidence, confidence, warnings, or tool data.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from tagger.input_schema import InputSchemaError, validate_input_record
from tagger.tools.acoustic_tags.registry import PHASE1_ACOUSTIC_TOOLS
from tagger.tools.base import ToolResult


ACOUSTIC_FIELDS = {
    "duration_sec": None,
    "sample_rate_hz": None,
    "channels": None,
    "silence_ratio": None,
    "speaker_count": None,
    "snr_db": None,
    "c60": None,
    "far_field": None,
    "bgm": None,
}


def run_manifest(manifest_path, output_path):
    # type: (Union[str, Path], Union[str, Path]) -> Dict[str, Any]
    manifest = Path(manifest_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    internal_warning_count = 0
    with manifest.open("r", encoding="utf-8") as source, output.open(
        "w", encoding="utf-8"
    ) as sink:
        for row_index, line in enumerate(source, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            try:
                internal = _tag_record_internal(record, manifest_dir=manifest.parent)
            except InputSchemaError as exc:
                raise InputSchemaError("line %s: %s" % (row_index, exc))
            internal_warning_count += len(internal["warnings"])
            sink.write(
                json.dumps(internal["tags"], ensure_ascii=False, sort_keys=True) + "\n"
            )
            count += 1

    return {
        "manifest_path": str(manifest),
        "output_path": str(output),
        "sample_count": count,
        "internal_warning_count": internal_warning_count,
    }


def tag_record(record, manifest_dir):
    # type: (Dict[str, Any], Union[str, Path]) -> Dict[str, Any]
    return _tag_record_internal(record, manifest_dir)["tags"]


def _tag_record_internal(record, manifest_dir):
    # type: (Dict[str, Any], Union[str, Path]) -> Dict[str, Any]
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
        tool_context = {}  # type: Dict[str, Any]
        for tool in PHASE1_ACOUSTIC_TOOLS:
            try:
                result = tool["run"](audio_path, context=tool_context)
                apply_result(tags, internal_results, result)
            except Exception as exc:  # noqa: BLE001 - tool failures become internal warnings.
                warnings.append(
                    {
                        "type": "acoustic_tool_error",
                        "message": str(exc),
                        "sample_id": sample_id,
                        "audio_path": str(audio_path),
                        "tag_path": tool["tag_path"],
                        "tool_name": tool["tool_name"],
                    }
                )

    warnings.extend(compare_native_metadata_audio_fields(sample, tags["acoustic"]))

    return {
        "tags": tags,
        "internal_results": internal_results,
        "warnings": warnings,
    }


def empty_tags():
    # type: () -> Dict[str, Any]
    return {
        "acoustic": dict(ACOUSTIC_FIELDS),
        "language": {
            "topic": [],
            "languages": [],
            "word_count": None,
            "punctuation": {
                "has_punctuation": None,
                "punctuation_count": None,
                "punctuation_types": [],
            },
            "repetition": {
                "filler_words": [],
                "filler_count": None,
                "repeated_tokens": [],
                "repetition_count": None,
            },
        },
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


def compare_native_metadata_audio_fields(sample, observed_acoustic):
    # type: (Dict[str, Any], Dict[str, Any]) -> List[Dict[str, Any]]
    native_metadata = sample.get("native_metadata", {})
    warnings = []  # type: List[Dict[str, Any]]
    comparisons = [
        ("duration_sec", 1e-3),
        ("sample_rate_hz", 0),
        ("channels", 0),
    ]
    for field, tolerance in comparisons:
        native_value = native_metadata.get(field)
        observed_value = observed_acoustic.get(field)
        if native_value is None or observed_value is None:
            continue
        if isinstance(native_value, (int, float)) and isinstance(
            observed_value, (int, float)
        ):
            mismatch = abs(float(native_value) - float(observed_value)) > tolerance
        else:
            mismatch = native_value != observed_value
        if mismatch:
            warnings.append(
                {
                    "type": "native_metadata_audio_mismatch",
                    "field": field,
                    "native_metadata_value": native_value,
                    "observed_value": observed_value,
                    "message": "file-probed value differs from native metadata",
                }
            )
    return warnings


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
        default="phase1_asr_samples/outputs/acoustic_phase1_tags.jsonl",
        help="Output tags-only JSONL path for phase1 acoustic tags.",
    )
    return parser


def main(argv=None):
    # type: (Optional[List[str]]) -> int
    args = build_arg_parser().parse_args(argv)
    summary = run_manifest(args.manifest, args.output)
    public_summary = {
        "output_path": summary["output_path"],
        "sample_count": summary["sample_count"],
    }
    print(json.dumps(public_summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
