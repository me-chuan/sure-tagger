"""Compatibility entry point for the v3 signal pipeline."""

from tagger.pipelines.signal_v2 import (  # noqa: F401
    audit_signal_tags,
    build_arg_parser,
    empty_tags,
    main,
    resolve_audio_path,
    run_manifest,
    tag_record,
)
