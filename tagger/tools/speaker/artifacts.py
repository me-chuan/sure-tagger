"""Internal speaker artifact helpers."""

import gzip
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional, Union


def write_speaker_artifact(metadata, artifact_dir, sample_key, route=None):
    # type: (Dict[str, Any], Union[str, Path], str, Optional[str]) -> Path
    directory = Path(artifact_dir)
    directory.mkdir(parents=True, exist_ok=True)
    suffix = route or metadata.get("primary_route") or "speaker"
    path = directory / ("%s.%s.json.gz" % (_safe_artifact_stem(sample_key), _safe_artifact_stem(suffix)))
    with gzip.open(str(path), "wt", encoding="utf-8") as sink:
        json.dump(metadata, sink, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return path


def _safe_artifact_stem(value):
    raw = str(value)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._-")
    if not stem:
        return "sample"
    return stem[:160]
