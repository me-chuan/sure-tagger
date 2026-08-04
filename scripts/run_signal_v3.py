#!/usr/bin/env python3
"""Run v3 signal tagging on a raw-only manifest."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tagger.pipelines.signal_v3 import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
