import gzip
import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
import wave

from scripts.run_c50_method_comparison import compare_record as compare_c50_record
from tagger.input_schema import InputSchemaError, validate_input_record
from tagger.pipelines.signal import (
    audit_basic_acoustic,
    audit_sound_field_scene,
    resolve_audio_path,
    tag_record as tag_signal_record,
)
from tagger.tools.acoustic_io import probe_audio_info
from tagger.tools.basic_acoustic.brouhaha_signal_estimator import (
    BrouhahaConfig,
    run as run_brouhaha_signal_estimator,
)
from tagger.tools.basic_acoustic.brouhaha_vad_silence_detector import (
    run as run_brouhaha_vad_silence_detector,
)
from tagger.tools.basic_acoustic.dnsmos_quality_estimator import (
    DnsmosConfig,
    run as run_dnsmos_quality_estimator,
)
from tagger.tools.basic_acoustic.firered_vad_silence_detector import (
    FireRedVadConfig,
    FireRedVadError,
    run as run_firered_vad_silence_detector,
    speech_segments_to_silence_segments,
    validate_silence_segments,
)
from tagger.tools.basic_acoustic.silence_ratio_calculator import run as run_silence_ratio
from tagger.tools.sound_field_scene.c50_estimator import (
    run as run_c50_estimator,
)
from tagger.tools.sound_field_scene.firered_aed_detector import (
    FireRedAedConfig,
    FireRedAedError,
    run as run_firered_aed_detector,
    validate_aed_output,
)
from tagger.tools.sound_field_scene.rir_estimator import (
    RecRirConfig,
    RecRirError,
    run as run_recrir_rir_estimator,
)
from tagger.tools.sound_field_scene.rt60_estimator import (
    run as run_rt60_estimator,
)


class AcousticToolsTest(unittest.TestCase):
    def test_probe_audio_info_reads_header_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=8000, channels=1, duration_sec=1.0)

            info = probe_audio_info(path)

            self.assertEqual(info.sample_rate_hz, 8000)
            self.assertEqual(info.channels, 1)
            self.assertEqual(info.frame_count, 8000)
            self.assertAlmostEqual(info.duration_sec, 1.0)

    def test_closed_input_schema_accepts_raw_only_record(self):
        record = make_record("audio.wav")
        validate_input_record(record)

    def test_closed_input_schema_rejects_extra_fields(self):
        record = make_record("audio.wav")
        record["sample"]["audio"]["uri"] = "derived"
        with self.assertRaises(InputSchemaError):
            validate_input_record(record)

    def test_resolve_audio_path_prefers_existing_cwd_relative_path(self):
        sample = {"audio": {"path": "phase1_asr_samples/manifest.jsonl"}}
        resolved = resolve_audio_path(sample, "phase1_asr_samples")
        self.assertEqual(resolved, Path.cwd() / "phase1_asr_samples/manifest.jsonl")

    def test_signal_tag_record_returns_signal_and_sound_field_tags_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)
            config = FireRedVadConfig(
                model_dir=str(Path(tmpdir) / "missing_model"),
                subprocess_python="",
            )
            brouhaha_config = BrouhahaConfig(
                model_path=str(Path(tmpdir) / "missing_brouhaha.ckpt"),
                repo_dir=str(Path(tmpdir) / "missing_brouhaha_repo"),
                subprocess_python="",
            )
            recrir_config = RecRirConfig(
                repo_dir=str(Path(tmpdir) / "missing_recrir_repo"),
                config_path=str(Path(tmpdir) / "missing_recrir.toml"),
                checkpoint_path=str(Path(tmpdir) / "missing_recrir.tar"),
                subprocess_python="",
            )

            tags = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                config,
                brouhaha_config,
                recrir_config,
                dnsmos_config=DnsmosConfig(subprocess_python=""),
                dnsmos_client=FakeDnsmosClient(
                    {"sig": 4.1, "bak": 3.2, "ovrl": 3.5, "p808": 3.8}
                ),
                firered_aed_config=FireRedAedConfig(
                    model_dir=str(Path(tmpdir) / "missing_aed_model"),
                    subprocess_python="",
                ),
                firered_aed_client=FakeFireRedAedClient(
                    {
                        "event2timestamps": {
                            "speech": [[0.1, 0.9]],
                            "singing": [],
                            "music": [[0.2, 0.8]],
                        },
                        "event2ratio": {
                            "speech": 0.8,
                            "singing": 0.0,
                            "music": 0.6,
                        },
                    }
                ),
            )

            self.assertEqual(
                set(tags.keys()),
                set(
                    [
                        "basic_acoustic",
                        "sound_field_scene",
                        "speaker",
                        "language_content",
                    ]
                ),
            )
            self.assertEqual(
                set(tags["basic_acoustic"].keys()),
                set(
                    [
                        "duration_sec",
                        "sample_rate_hz",
                        "channels",
                        "silence_ratio",
                        "silence_segments",
                        "snr_db",
                        "c50",
                        "dnsmos_sig",
                        "dnsmos_bak",
                        "dnsmos_ovrl",
                        "dnsmos_p808",
                    ]
                ),
            )
            self.assertEqual(tags["basic_acoustic"]["duration_sec"], 1.0)
            self.assertEqual(tags["basic_acoustic"]["sample_rate_hz"], 16000)
            self.assertEqual(tags["basic_acoustic"]["channels"], 1)
            self.assertIsNone(tags["basic_acoustic"]["silence_ratio"])
            self.assertIsNone(tags["basic_acoustic"]["silence_segments"])
            self.assertIsNone(tags["basic_acoustic"]["snr_db"])
            self.assertIsNone(tags["basic_acoustic"]["c50"])
            self.assertEqual(tags["basic_acoustic"]["dnsmos_sig"], 4.1)
            self.assertEqual(tags["basic_acoustic"]["dnsmos_bak"], 3.2)
            self.assertEqual(tags["basic_acoustic"]["dnsmos_ovrl"], 3.5)
            self.assertEqual(tags["basic_acoustic"]["dnsmos_p808"], 3.8)
            self.assertEqual(
                set(tags["sound_field_scene"].keys()),
                set(["far_field", "rt60", "c50", "music", "sound"]),
            )
            self.assertIsNone(tags["sound_field_scene"]["rt60"])
            self.assertIsNone(tags["sound_field_scene"]["c50"])
            self.assertTrue(tags["sound_field_scene"]["music"])
            self.assertTrue(tags["sound_field_scene"]["sound"])

    def test_fire_red_speech_segments_convert_to_silence_segments(self):
        segments = speech_segments_to_silence_segments(
            [[0.44, 1.82]],
            duration_sec=2.32,
        )

        self.assertEqual(
            segments,
            [
                {"start_sec": 0.0, "end_sec": 0.44},
                {"start_sec": 1.82, "end_sec": 2.32},
            ],
        )

    def test_fire_red_silence_detector_accepts_injected_fire_red_client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=2.0)

            result = run_firered_vad_silence_detector(
                path,
                duration_sec=2.0,
                context={},
                config=FireRedVadConfig(model_dir=str(Path(tmpdir) / "model")),
                client=FakeFireRedClient([[0.5, 1.25], [1.5, 2.0]]),
            )

            self.assertEqual(result.tag_path, "basic_acoustic.silence_segments")
            self.assertEqual(result.tool_name, "firered_vad_silence_detector")
            self.assertEqual(
                result.value,
                [
                    {"start_sec": 0.0, "end_sec": 0.5},
                    {"start_sec": 1.25, "end_sec": 1.5},
                ],
            )

    def test_fire_red_aed_maps_validated_events_to_public_booleans(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=2.0)

            results = run_firered_aed_detector(
                path,
                duration_sec=2.0,
                context={},
                config=FireRedAedConfig(
                    model_dir=str(Path(tmpdir) / "model"),
                    subprocess_python="",
                ),
                client=FakeFireRedAedClient(
                    {
                        "event2timestamps": {
                            "speech": [[0.1, 1.8]],
                            "singing": [[0.5, 1.0]],
                            "music": [],
                        },
                        "event2ratio": {
                            "speech": 0.85,
                            "singing": 0.25,
                            "music": 0.0,
                        },
                    }
                ),
            )

            by_path = {result.tag_path: result for result in results}
            self.assertFalse(by_path["sound_field_scene.music"].value)
            self.assertTrue(by_path["sound_field_scene.sound"].value)
            self.assertEqual(
                by_path["sound_field_scene.sound"].evidence["event_segments"][
                    "singing"
                ],
                [{"start_sec": 0.5, "end_sec": 1.0}],
            )
            self.assertEqual(
                by_path["sound_field_scene.music"].evidence["event_ratios"][
                    "speech"
                ],
                0.85,
            )

    def test_fire_red_aed_rejects_invalid_event_output(self):
        with self.assertRaises(FireRedAedError):
            validate_aed_output(
                {
                    "event2timestamps": {
                        "speech": [[0.0, 1.1]],
                        "singing": [],
                        "music": [],
                    },
                    "event2ratio": {
                        "speech": 1.1,
                        "singing": 0.0,
                        "music": 0.0,
                    },
                },
                duration_sec=1.0,
            )

    def test_silence_ratio_is_calculated_from_segments_and_duration(self):
        result = run_silence_ratio(
            [
                {"start_sec": 0.0, "end_sec": 0.5},
                {"start_sec": 1.5, "end_sec": 2.0},
            ],
            duration_sec=2.0,
        )

        self.assertEqual(result.tag_path, "basic_acoustic.silence_ratio")
        self.assertEqual(result.value, 0.5)

    def test_silence_segments_reject_overlap(self):
        with self.assertRaises(FireRedVadError):
            validate_silence_segments(
                [
                    {"start_sec": 0.0, "end_sec": 0.7},
                    {"start_sec": 0.6, "end_sec": 1.0},
                ],
                duration_sec=1.0,
            )

    def test_silence_segments_reject_out_of_bounds(self):
        with self.assertRaises(FireRedVadError):
            validate_silence_segments(
                [{"start_sec": 0.0, "end_sec": 1.1}],
                duration_sec=1.0,
            )

    def test_brouhaha_estimator_aggregates_snr_and_c50(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            results = run_brouhaha_signal_estimator(
                path,
                context={},
                config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "best.ckpt"),
                    repo_dir=str(Path(tmpdir) / "repo"),
                ),
                client=FakeBrouhahaClient({"snr": [10.0, 14.0], "c50": [2.0, 4.0]}),
            )

            values = {result.tag_path: result.value for result in results}
            self.assertEqual(values["basic_acoustic.snr_db"], 12.0)
            self.assertEqual(values["basic_acoustic.c50"], 3.0)

    def test_brouhaha_estimator_allows_partial_missing_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            results = run_brouhaha_signal_estimator(
                path,
                context={},
                config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "best.ckpt"),
                    repo_dir=str(Path(tmpdir) / "repo"),
                ),
                client=FakeBrouhahaClient({"c50": [5.0]}),
            )

            by_path = {result.tag_path: result for result in results}
            self.assertIsNone(by_path["basic_acoustic.snr_db"].value)
            self.assertEqual(by_path["basic_acoustic.snr_db"].status, "failed")
            self.assertEqual(by_path["basic_acoustic.c50"].value, 5.0)
            self.assertEqual(by_path["basic_acoustic.c50"].status, "estimated")

    def test_brouhaha_estimator_rejects_nan_and_inf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            results = run_brouhaha_signal_estimator(
                path,
                context={},
                config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "best.ckpt"),
                    repo_dir=str(Path(tmpdir) / "repo"),
                ),
                client=FakeBrouhahaClient(
                    {"snr": [10.0, float("inf")], "c50": [float("nan")]}
                ),
            )

            values = {result.tag_path: result.value for result in results}
            self.assertIsNone(values["basic_acoustic.snr_db"])
            self.assertIsNone(values["basic_acoustic.c50"])

    def test_dnsmos_estimator_maps_all_official_scores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            results = run_dnsmos_quality_estimator(
                path,
                context={},
                config=DnsmosConfig(subprocess_python=""),
                client=FakeDnsmosClient(
                    {
                        "sig": 4.1256789,
                        "bak": 3.25,
                        "ovrl": 3.75,
                        "p808": 4.0,
                        "num_hops": 1,
                        "audio_length_sec": 1.0,
                    }
                ),
            )

            by_path = {result.tag_path: result for result in results}
            self.assertEqual(by_path["basic_acoustic.dnsmos_sig"].value, 4.125679)
            self.assertEqual(by_path["basic_acoustic.dnsmos_bak"].value, 3.25)
            self.assertEqual(by_path["basic_acoustic.dnsmos_ovrl"].value, 3.75)
            self.assertEqual(by_path["basic_acoustic.dnsmos_p808"].value, 4.0)
            self.assertTrue(all(result.status == "estimated" for result in results))

    def test_dnsmos_estimator_nulls_missing_and_out_of_range_scores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            results = run_dnsmos_quality_estimator(
                path,
                config=DnsmosConfig(subprocess_python=""),
                client=FakeDnsmosClient(
                    {"sig": 5.1, "bak": float("nan"), "ovrl": 3.0}
                ),
            )

            by_path = {result.tag_path: result for result in results}
            self.assertIsNone(by_path["basic_acoustic.dnsmos_sig"].value)
            self.assertIsNone(by_path["basic_acoustic.dnsmos_bak"].value)
            self.assertEqual(by_path["basic_acoustic.dnsmos_ovrl"].value, 3.0)
            self.assertIsNone(by_path["basic_acoustic.dnsmos_p808"].value)
            self.assertEqual(by_path["basic_acoustic.dnsmos_p808"].status, "failed")

    def test_brouhaha_vad_silence_detector_converts_annotation_to_silence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=2.0)

            result = run_brouhaha_vad_silence_detector(
                path,
                duration_sec=2.0,
                context={},
                config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "best.ckpt"),
                    repo_dir=str(Path(tmpdir) / "repo"),
                ),
                client=FakeBrouhahaClient(
                    {
                        "annotation": [
                            {"start_sec": 0.4, "end_sec": 1.0},
                            {"start_sec": 1.25, "end_sec": 2.0},
                        ]
                    }
                ),
            )

            self.assertEqual(result.tag_path, "diagnostic.brouhaha_silence_segments")
            self.assertEqual(
                result.value,
                [
                    {"start_sec": 0.0, "end_sec": 0.4},
                    {"start_sec": 1.0, "end_sec": 1.25},
                ],
            )

    def test_brouhaha_vad_silence_detector_clips_annotation_to_duration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=2.0)

            result = run_brouhaha_vad_silence_detector(
                path,
                duration_sec=2.0,
                context={},
                config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "best.ckpt"),
                    repo_dir=str(Path(tmpdir) / "repo"),
                ),
                client=FakeBrouhahaClient(
                    {"annotation": [{"start_sec": -0.05, "end_sec": 2.2}]}
                ),
            )

            self.assertEqual(result.value, [])

    def test_recrir_rir_estimator_accepts_injected_client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            result = run_recrir_rir_estimator(
                path,
                context={},
                config=RecRirConfig(max_rir_seconds=1.0),
                client=FakeRecRirClient(
                    {"sample_rate_hz": 16000, "samples": [0.0, 2.0, -1.0]}
                ),
            )

            self.assertEqual(result.tag_path, "sound_field_scene.rir")
            self.assertEqual(result.tool_name, "rir_estimator")
            self.assertEqual(result.value["sample_rate_hz"], 16000)
            self.assertEqual(result.value["samples"], [0.0, 1.0, -0.5])

    def test_recrir_rir_estimator_rejects_nan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            with self.assertRaises(RecRirError):
                run_recrir_rir_estimator(
                    path,
                    context={},
                    config=RecRirConfig(max_rir_seconds=1.0),
                    client=FakeRecRirClient(
                        {"sample_rate_hz": 16000, "samples": [float("nan")]}
                    ),
                )

    def test_rt60_estimator_derives_value_from_rir(self):
        sample_rate_hz = 1000
        tau = 0.2
        samples = [
            math.exp(-float(index) / (sample_rate_hz * tau))
            for index in range(2000)
        ]

        result = run_rt60_estimator(
            {"sample_rate_hz": sample_rate_hz, "samples": samples}
        )

        self.assertEqual(result.tag_path, "sound_field_scene.rt60")
        self.assertGreater(result.value, 1.0)
        self.assertLess(result.value, 1.7)

    def test_c50_estimator_derives_value_from_rir(self):
        result = run_c50_estimator(
            {"sample_rate_hz": 1000, "samples": [1.0] * 50 + [0.5] * 50}
        )

        self.assertEqual(result.tag_path, "sound_field_scene.c50")
        self.assertAlmostEqual(result.value, 6.0206, places=4)

    def test_sound_field_auditor_rejects_invalid_rt60_and_c50(self):
        sound_field_scene = {
            "far_field": None,
            "rt60": -1.0,
            "c50": float("nan"),
            "music": None,
            "sound": None,
        }

        warnings = audit_sound_field_scene(sound_field_scene)

        self.assertIsNone(sound_field_scene["rt60"])
        self.assertIsNone(sound_field_scene["c50"])
        self.assertEqual(
            warnings,
            [
                {"type": "invalid_sound_field_scene_value", "field": "rt60"},
                {"type": "invalid_sound_field_scene_value", "field": "c50"},
            ],
        )

    def test_basic_acoustic_auditor_rejects_invalid_dnsmos_scores(self):
        basic_acoustic = {
            "dnsmos_sig": 0.9,
            "dnsmos_bak": 5.1,
            "dnsmos_ovrl": float("nan"),
            "dnsmos_p808": 4.0,
        }

        warnings = audit_basic_acoustic(basic_acoustic)

        self.assertIsNone(basic_acoustic["dnsmos_sig"])
        self.assertIsNone(basic_acoustic["dnsmos_bak"])
        self.assertIsNone(basic_acoustic["dnsmos_ovrl"])
        self.assertEqual(basic_acoustic["dnsmos_p808"], 4.0)
        self.assertEqual(
            [warning["field"] for warning in warnings],
            ["dnsmos_sig", "dnsmos_bak", "dnsmos_ovrl"],
        )

    def test_signal_pipeline_uses_injected_recrir_client_for_non_model_input_audio(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=1.0)
            rir_samples = [
                math.exp(-float(index) / (16000 * 0.2))
                for index in range(16000)
            ]
            artifact_dir = Path(tmpdir) / "artifacts"

            tags = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                firered_vad_config=FireRedVadConfig(
                    model_dir=str(Path(tmpdir) / "missing_model"),
                    subprocess_python="",
                ),
                brouhaha_config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "missing_brouhaha.ckpt"),
                    repo_dir=str(Path(tmpdir) / "missing_brouhaha_repo"),
                    subprocess_python="",
                ),
                recrir_config=RecRirConfig(max_rir_seconds=1.0),
                recrir_client=FakeRecRirClient(
                    {"sample_rate_hz": 16000, "samples": rir_samples}
                ),
                artifact_dir=artifact_dir,
                dnsmos_config=DnsmosConfig(subprocess_python=""),
                dnsmos_client=FakeDnsmosClient(
                    {"sig": 4.0, "bak": 3.0, "ovrl": 3.5, "p808": 3.75}
                ),
                firered_aed_config=FireRedAedConfig(
                    model_dir=str(Path(tmpdir) / "missing_aed_model"),
                    subprocess_python="",
                ),
                firered_aed_client=FakeFireRedAedClient(
                    {
                        "event2timestamps": {
                            "speech": [[0.1, 0.9]],
                            "singing": [],
                            "music": [],
                        },
                        "event2ratio": {
                            "speech": 0.8,
                            "singing": 0.0,
                            "music": 0.0,
                        },
                    }
                ),
            )

            self.assertEqual(tags["basic_acoustic"]["sample_rate_hz"], 8000)
            self.assertEqual(tags["basic_acoustic"]["channels"], 2)
            self.assertNotIn("rir", tags["sound_field_scene"])
            self.assertIsNotNone(tags["sound_field_scene"]["rt60"])
            self.assertIsNotNone(tags["sound_field_scene"]["c50"])
            self.assertIsNone(tags["basic_acoustic"]["c50"])

            artifacts = list((artifact_dir / "rir").glob("*.rir.json.gz"))
            self.assertEqual(len(artifacts), 1)
            with gzip.open(str(artifacts[0]), "rt", encoding="utf-8") as source:
                artifact = json.load(source)
            self.assertEqual(artifact["sample_rate_hz"], 16000)
            self.assertEqual(len(artifact["samples"]), len(rir_samples))

    def test_c50_comparison_reports_brouhaha_and_recrir_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            result = compare_c50_record(
                make_record(str(path)),
                manifest_dir=tmpdir,
                context={},
                brouhaha_config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "best.ckpt"),
                    repo_dir=str(Path(tmpdir) / "repo"),
                    subprocess_python="",
                ),
                recrir_config=RecRirConfig(max_rir_seconds=1.0),
                brouhaha_client=FakeBrouhahaClient(
                    {"snr": [10.0], "c50": [3.0]}
                ),
                recrir_client=FakeRecRirClient(
                    {
                        "sample_rate_hz": 1000,
                        "samples": [1.0] * 50 + [0.5] * 50,
                    }
                ),
            )

            self.assertEqual(result["brouhaha"]["status"], "ok")
            self.assertEqual(result["brouhaha"]["c50_db"], 3.0)
            self.assertEqual(result["recrir"]["status"], "ok")
            self.assertAlmostEqual(result["recrir"]["c50_db"], 6.0206, places=4)
            self.assertTrue(result["comparison"]["paired"])
            self.assertAlmostEqual(
                result["comparison"]["c50_delta_recrir_minus_brouhaha_db"],
                3.0206,
                places=4,
            )


def make_record(audio_path):
    return {
        "corpus": {
            "dataset_name": "unit_test",
            "source_urls": {
                "article": [],
                "github": [],
                "huggingface": [],
                "dataset_card": [],
            },
            "native_metadata": {},
        },
        "sample": {
            "sample_id": "utt1",
            "audio": {"path": audio_path},
            "text": {"transcript": "HELLO WORLD"},
            "native_metadata": {"utt2spk": "spk1"},
        },
    }


class FakeFireRedClient:
    def __init__(self, speech_segments):
        self.speech_segments = speech_segments

    def detect_speech_segments(self, audio_path, context=None):
        return self.speech_segments


class FakeFireRedAedClient:
    def __init__(self, output):
        self.output = output

    def detect_audio_events(self, audio_path, context=None):
        return self.output


class FakeBrouhahaClient:
    def __init__(self, output):
        self.output = output

    def estimate(self, audio_path, context=None):
        return self.output


class FakeDnsmosClient:
    def __init__(self, output):
        self.output = output

    def estimate(self, audio_path, context=None):
        return self.output


class FakeRecRirClient:
    def __init__(self, output):
        self.output = output

    def estimate_rir(self, audio_path, context=None):
        return self.output


def write_test_wav(
    path: Path,
    sample_rate: int,
    channels: int,
    duration_sec: float,
):
    frame_count = int(sample_rate * duration_sec)
    frames = []
    for index in range(frame_count):
        sample = int(10000 * math.sin(2 * math.pi * 440 * index / sample_rate))
        frames.extend([sample] * channels)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack("<" + "h" * len(frames), *frames))


if __name__ == "__main__":
    unittest.main()
