"""JSONL worker entry point for subprocess-backed model tools."""

import contextlib
import json
import sys
import traceback


_CLIENTS = {}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        sys.stderr.write("usage: subprocess_worker <tool_name>\n")
        return 2
    tool_name = argv[0]

    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        if request.get("_command") == "close":
            return 0
        try:
            with contextlib.redirect_stdout(sys.stderr):
                result = dispatch(tool_name, request)
            response = {"status": "ok", "result": _jsonable(result)}
        except Exception as exc:  # noqa: BLE001 - returned to parent as tool failure.
            traceback.print_exc(file=sys.stderr)
            response = {
                "status": "error",
                "error_type": exc.__class__.__name__,
                "message": str(exc),
            }
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


def dispatch(tool_name, request):
    if tool_name == "firered_vad_detect":
        return _run_firered_vad_detect(request)
    if tool_name == "firered_aed_detect":
        return _run_firered_aed_detect(request)
    if tool_name == "panns_background_estimate":
        return _run_panns_background_estimate(request)
    if tool_name == "brouhaha_estimate":
        return _run_brouhaha_estimate(request)
    if tool_name == "dnsmos_estimate":
        return _run_dnsmos_estimate(request)
    if tool_name == "recrir_estimate":
        return _run_recrir_estimate(request)
    if tool_name == "moss_diarize_estimate":
        return _run_moss_diarize_estimate(request)
    raise ValueError("unknown subprocess tool: %s" % tool_name)


def _run_firered_vad_detect(request):
    from tagger.tools.basic_acoustic.firered_vad_silence_detector import (
        FireRedVadClient,
        FireRedVadConfig,
    )

    config = FireRedVadConfig(**request["config"])
    client = _cached_client("firered_vad_detect", request["config"], FireRedVadClient, config)
    return {
        "speech_segments": client.detect_speech_segments(
            request["audio_path"],
            context=None,
        )
    }


def _run_firered_aed_detect(request):
    from tagger.tools.sound_field_scene.firered_aed_detector import (
        FireRedAedClient,
        FireRedAedConfig,
    )

    config = FireRedAedConfig(**request["config"])
    client = _cached_client(
        "firered_aed_detect",
        request["config"],
        FireRedAedClient,
        config,
    )
    return {
        "output": client.detect_audio_events(
            request["audio_path"],
            context=None,
        )
    }


def _run_panns_background_estimate(request):
    from tagger.tools.sound_field_scene.panns_background_detector import (
        PannsBackgroundClient,
        PannsBackgroundConfig,
    )

    config = PannsBackgroundConfig(**request["config"])
    client = _cached_client(
        "panns_background_estimate",
        request["config"],
        PannsBackgroundClient,
        config,
    )
    return {"output": client.estimate(request["audio_path"], context=None)}


def _run_brouhaha_estimate(request):
    from tagger.tools.basic_acoustic.brouhaha_signal_estimator import (
        BrouhahaClient,
        BrouhahaConfig,
    )

    config = BrouhahaConfig(**request["config"])
    client = _cached_client("brouhaha_estimate", request["config"], BrouhahaClient, config)
    return {"output": client.estimate(request["audio_path"], context=None)}


def _run_recrir_estimate(request):
    from tagger.tools.sound_field_scene.rir_estimator import RecRirClient, RecRirConfig

    config = RecRirConfig(**request["config"])
    client = _cached_client("recrir_estimate", request["config"], RecRirClient, config)
    return {"output": client.estimate_rir(request["audio_path"], context=None)}


def _run_dnsmos_estimate(request):
    from tagger.tools.basic_acoustic.dnsmos_quality_estimator import (
        DnsmosClient,
        DnsmosConfig,
    )

    config = DnsmosConfig(**request["config"])
    client = _cached_client("dnsmos_estimate", request["config"], DnsmosClient, config)
    return {"output": client.estimate(request["audio_path"], context=None)}


def _run_moss_diarize_estimate(request):
    from tagger.tools.speaker.moss_diarizer import (
        MossDiarizeClient,
        MossDiarizeConfig,
    )

    config = MossDiarizeConfig(**request["config"])
    client = _cached_client(
        "moss_diarize_estimate",
        request["config"],
        MossDiarizeClient,
        config,
    )
    return {"output": client.diarize(request["audio_path"], context=None)}


def _cached_client(tool_name, config_record, client_class, config):
    key = (tool_name, json.dumps(config_record, sort_keys=True))
    if key not in _CLIENTS:
        _CLIENTS[key] = client_class(config)
    return _CLIENTS[key]


def _jsonable(value):
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    if hasattr(value, "tolist"):
        value = value.tolist()
    if hasattr(value, "itertracks"):
        return [
            {
                "start_sec": float(segment.start),
                "end_sec": float(segment.end),
                "track": str(track),
            }
            for segment, track in value.itertracks()
        ]
    if hasattr(value, "itersegments"):
        return [
            {
                "start_sec": float(segment.start),
                "end_sec": float(segment.end),
            }
            for segment in value.itersegments()
        ]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    try:
        json.dumps(value)
    except TypeError:
        return str(value)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
