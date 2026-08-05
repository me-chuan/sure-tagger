import gzip
import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
import wave

from tagger.input_schema import InputSchemaError, validate_input_record
from tagger.pipelines.signal import (
    audit_speaker,
    audit_sound_field_scene,
    resolve_audio_path,
    run_manifest as run_signal_manifest,
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
from tagger.tools.sound_field_scene.rir_estimator import (
    RecRirConfig,
    RecRirError,
    run as run_recrir_rir_estimator,
)
from tagger.tools.sound_field_scene.rt60_estimator import (
    run as run_rt60_estimator,
)
from tagger.tools.speaker.channel_activity import (
    ChannelActivityConfig,
    detect_channel_activity,
)
from tagger.tools.speaker.config import default_speaker_layer_config
from tagger.tools.speaker.metrics import (
    SpeakerMetricsConfig,
    build_metadata_from_timeline,
    public_results_from_metadata,
)
from tagger.tools.speaker.moss_diarizer import parse_moss_text


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
            self.assertEqual(
                set(tags["sound_field_scene"].keys()),
                set(["far_field", "rt60", "c50", "music", "sound"]),
            )
            self.assertIsNone(tags["sound_field_scene"]["rt60"])
            self.assertIsNone(tags["sound_field_scene"]["c50"])

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

    def test_speaker_metrics_derive_internal_summary_and_public_utterance_tags(self):
        metadata = build_metadata_from_timeline(
            [
                {"start_sec": 0.0, "end_sec": 1.2, "speaker_id": "S01"},
                {"start_sec": 0.8, "end_sec": 2.0, "speaker_id": "S02"},
            ],
            duration_sec=2.0,
            sample_id="u1",
            recording_id="meet1",
            target_units=[
                {"unit_id": "u0", "start_sec": 0.0, "end_sec": 0.75},
                {"unit_id": "u1", "start_sec": 0.7, "end_sec": 1.1},
            ],
            config=SpeakerMetricsConfig(min_speech_duration_sec=0.1),
        )

        summary = metadata["recording_summary"]
        self.assertEqual(summary["speaker_count"], 2)
        self.assertTrue(summary["multi_speaker"])
        self.assertEqual(summary["turn_count"], 2)
        self.assertEqual(summary["speaker_change_rate_per_min"], 30.0)
        self.assertEqual(summary["overlap_ratio_speech"], 0.2)
        self.assertEqual(summary["crosstalk_level"], "medium")
        self.assertEqual(summary["dominant_speaker_ratio"], 0.6)

        utterances = metadata["utterances"]
        self.assertEqual(utterances[0]["primary_speaker_id"], "spk_001")
        self.assertEqual(utterances[0]["active_speaker_count"], 1)
        self.assertFalse(utterances[0]["is_overlapped"])
        self.assertEqual(utterances[1]["active_speaker_count"], 2)
        self.assertEqual(utterances[1]["speaker_change_count"], 1)
        self.assertTrue(utterances[1]["speaker_change"])
        self.assertTrue(utterances[1]["is_overlapped"])
        self.assertEqual(utterances[1]["overlap_ratio"], 0.75)

        public_values = {
            result.tag_path: result.value
            for result in public_results_from_metadata(metadata)
        }
        self.assertTrue(public_values["speaker.multi_speaker"])
        self.assertTrue(public_values["speaker.speaker_change"])
        self.assertTrue(public_values["speaker.speaker_overlap"])
        self.assertEqual(
            set(public_values),
            {"speaker.multi_speaker", "speaker.speaker_change", "speaker.speaker_overlap"},
        )

    def test_utterance_overlap_ratio_uses_speech_union_not_utterance_duration(self):
        metadata = build_metadata_from_timeline(
            [
                {"start_sec": 0.0, "end_sec": 1.0, "speaker_id": "S01"},
                {"start_sec": 0.8, "end_sec": 1.2, "speaker_id": "S02"},
            ],
            duration_sec=10.0,
            sample_id="u_silence_padded",
            recording_id="meet1",
            target_units=[
                {"unit_id": "u_silence_padded", "start_sec": 0.0, "end_sec": 10.0},
            ],
            config=SpeakerMetricsConfig(min_speech_duration_sec=0.1),
        )

        utterance = metadata["utterances"][0]
        self.assertEqual(utterance["overlap_duration_sec"], 0.2)
        self.assertEqual(utterance["speech_union_duration_sec"], 1.2)
        self.assertEqual(utterance["overlap_ratio"], 0.166667)
        self.assertTrue(utterance["is_overlapped"])

        public_values = {
            result.tag_path: result.value
            for result in public_results_from_metadata(metadata)
        }
        self.assertTrue(public_values["speaker.speaker_overlap"])

    def test_moss_text_parser_reads_speaker_timestamp_segments(self):
        segments = parse_moss_text(
            "[0.00][S01] hello there [1.00]\n"
            "[0.80][S02] hi [2.00]"
        )

        self.assertEqual(
            segments,
            [
                {
                    "start_sec": 0.0,
                    "end_sec": 1.0,
                    "speaker_id": "S01",
                    "text": "hello there",
                },
                {
                    "start_sec": 0.8,
                    "end_sec": 2.0,
                    "speaker_id": "S02",
                    "text": "hi",
                },
            ],
        )

    def test_channel_activity_detects_multichannel_speech_and_overlap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_channel_activity_wav(
                path,
                sample_rate=8000,
                duration_sec=2.0,
                channel_segments=[
                    [(0.0, 1.2)],
                    [(0.8, 2.0)],
                ],
            )

            activity = detect_channel_activity(
                path,
                duration_sec=2.0,
                config=ChannelActivityConfig(
                    window_sec=0.05,
                    energy_threshold=500.0,
                    min_segment_duration_sec=0.1,
                    merge_gap_sec=0.05,
                ),
            )

            self.assertEqual(len(activity["channels"]), 2)
            self.assertEqual(
                activity["channels"][0]["speech_segments"],
                [{"start_sec": 0.0, "end_sec": 1.2}],
            )
            self.assertEqual(
                activity["channels"][1]["speech_segments"],
                [{"start_sec": 0.8, "end_sec": 2.0}],
            )

    def test_signal_pipeline_uses_injected_moss_client_for_speaker_tags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mono.wav"
            write_test_wav(path, sample_rate=8000, channels=1, duration_sec=2.0)
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
                recrir_config=RecRirConfig(
                    repo_dir=str(Path(tmpdir) / "missing_recrir_repo"),
                    config_path=str(Path(tmpdir) / "missing_recrir.toml"),
                    checkpoint_path=str(Path(tmpdir) / "missing_recrir.tar"),
                    subprocess_python="",
                ),
                speaker_config=default_speaker_layer_config(enable_moss=True),
                moss_client=FakeMossClient(
                    {
                        "segments": [
                            {"start_sec": 0.0, "end_sec": 1.2, "speaker_id": "S01"},
                            {"start_sec": 0.8, "end_sec": 2.0, "speaker_id": "S02"},
                        ]
                    }
                ),
                artifact_dir=artifact_dir,
            )

            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertTrue(tags["speaker"]["speaker_change"])
            self.assertTrue(tags["speaker"]["speaker_overlap"])
            self.assertNotIn("metadata", tags["speaker"])
            self.assertNotIn("artifact_path", json.dumps(tags, sort_keys=True))

            artifacts = list((artifact_dir / "speaker").glob("*.moss_diarize.json.gz"))
            self.assertEqual(len(artifacts), 1)
            with gzip.open(str(artifacts[0]), "rt", encoding="utf-8") as source:
                artifact = json.load(source)
            self.assertEqual(artifact["primary_route"], "moss_diarize")
            self.assertEqual(artifact["recording_summary"]["speaker_count"], 2)

    def test_signal_pipeline_uses_merged_headset_moss_for_separated_headset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            artifact_dir = Path(tmpdir) / "artifacts"
            record = make_record(str(path))
            record["sample"]["native_metadata"]["microphone_type"] = "Headset"

            tags = tag_signal_record(
                record,
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
                recrir_config=RecRirConfig(
                    repo_dir=str(Path(tmpdir) / "missing_recrir_repo"),
                    config_path=str(Path(tmpdir) / "missing_recrir.toml"),
                    checkpoint_path=str(Path(tmpdir) / "missing_recrir.tar"),
                    subprocess_python="",
                ),
                speaker_config=default_speaker_layer_config(enable_moss=True),
                moss_client=FakeMossClient(
                    {
                        "segments": [
                            {"start_sec": 0.0, "end_sec": 1.2, "speaker_id": "S01"},
                            {"start_sec": 0.8, "end_sec": 2.0, "speaker_id": "S02"},
                        ]
                    }
                ),
                artifact_dir=artifact_dir,
            )

            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertTrue(tags["speaker"]["speaker_change"])
            self.assertTrue(tags["speaker"]["speaker_overlap"])

            artifacts = list((artifact_dir / "speaker").glob("*.moss_diarize_merged_headset.json.gz"))
            self.assertEqual(len(artifacts), 1)
            with gzip.open(str(artifacts[0]), "rt", encoding="utf-8") as source:
                artifact = json.load(source)
            self.assertEqual(artifact["primary_route"], "moss_diarize_merged_headset")
            self.assertEqual(artifact["input_kind"], "separated_headset_channels")
            self.assertEqual(artifact["recording_summary"]["speaker_count"], 2)
            self.assertEqual(
                [segment["speaker_id"] for segment in artifact["segments"]],
                ["spk_001", "spk_002"],
            )
            self.assertNotIn("source_channel_id", artifact["segments"][0])

    def test_signal_manifest_passes_injected_channel_activity_client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "stereo.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            manifest_path = Path(tmpdir) / "manifest.jsonl"
            output_path = Path(tmpdir) / "tags.jsonl"
            with manifest_path.open("w", encoding="utf-8") as sink:
                sink.write(json.dumps(make_record(str(path)), ensure_ascii=False) + "\n")

            run_signal_manifest(
                manifest_path,
                output_path,
                firered_vad_config=FireRedVadConfig(
                    model_dir=str(Path(tmpdir) / "missing_model"),
                    subprocess_python="",
                ),
                brouhaha_config=BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "missing_brouhaha.ckpt"),
                    repo_dir=str(Path(tmpdir) / "missing_brouhaha_repo"),
                    subprocess_python="",
                ),
                recrir_config=RecRirConfig(
                    repo_dir=str(Path(tmpdir) / "missing_recrir_repo"),
                    config_path=str(Path(tmpdir) / "missing_recrir.toml"),
                    checkpoint_path=str(Path(tmpdir) / "missing_recrir.tar"),
                    subprocess_python="",
                ),
                speaker_config=default_speaker_layer_config(enable_moss=False),
                channel_activity_client=FakeChannelActivityClient(
                    {
                        "metadata_version": "channel_activity_v0.1",
                        "duration_sec": 2.0,
                        "channels": [
                            {
                                "channel_id": "ch0",
                                "speaker_id": "spk_A",
                                "speech_segments": [
                                    {"start_sec": 0.0, "end_sec": 1.2}
                                ],
                            },
                            {
                                "channel_id": "ch1",
                                "speaker_id": "spk_B",
                                "speech_segments": [
                                    {"start_sec": 0.8, "end_sec": 2.0}
                                ],
                            },
                        ],
                    }
                ),
            )

            with output_path.open("r", encoding="utf-8") as source:
                tags = json.loads(source.readline())
            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertTrue(tags["speaker"]["speaker_change"])
            self.assertTrue(tags["speaker"]["speaker_overlap"])
            self.assertNotIn("channel_activity", tags["speaker"])

    def test_signal_pipeline_does_not_treat_mix_headset_stereo_as_separated_channels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.Mix-Headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)

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
                recrir_config=RecRirConfig(
                    repo_dir=str(Path(tmpdir) / "missing_recrir_repo"),
                    config_path=str(Path(tmpdir) / "missing_recrir.toml"),
                    checkpoint_path=str(Path(tmpdir) / "missing_recrir.tar"),
                    subprocess_python="",
                ),
                speaker_config=default_speaker_layer_config(enable_moss=False),
            )

            self.assertEqual(tags["basic_acoustic"]["channels"], 2)
            self.assertIsNone(tags["speaker"]["multi_speaker"])
            self.assertIsNone(tags["speaker"]["speaker_change"])
            self.assertIsNone(tags["speaker"]["speaker_overlap"])

    def test_speaker_auditor_rejects_invalid_public_values(self):
        speaker = {
            "multi_speaker": "yes",
            "speaker_change": "yes",
            "speaker_overlap": 1,
        }

        warnings = audit_speaker(speaker)

        self.assertEqual(
            warnings,
            [
                {"type": "invalid_speaker_value", "field": "multi_speaker"},
                {"type": "invalid_speaker_value", "field": "speaker_change"},
                {"type": "invalid_speaker_value", "field": "speaker_overlap"},
            ],
        )
        self.assertTrue(all(value is None for value in speaker.values()))


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


class FakeBrouhahaClient:
    def __init__(self, output):
        self.output = output

    def estimate(self, audio_path, context=None):
        return self.output


class FakeRecRirClient:
    def __init__(self, output):
        self.output = output

    def estimate_rir(self, audio_path, context=None):
        return self.output


class FakeMossClient:
    def __init__(self, output):
        if isinstance(output, list):
            self.outputs = list(output)
            self.output = None
        else:
            self.outputs = None
            self.output = output

    def diarize(self, audio_path, context=None):
        if self.outputs is not None:
            if not self.outputs:
                return {"segments": []}
            return self.outputs.pop(0)
        return self.output


class FakeChannelActivityClient:
    def __init__(self, output):
        self.output = output

    def detect_channel_activity(self, audio_path, context=None):
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


def write_channel_activity_wav(path, sample_rate, duration_sec, channel_segments):
    frame_count = int(sample_rate * duration_sec)
    channels = len(channel_segments)
    frames = []
    for index in range(frame_count):
        time_sec = (float(index) + 0.5) / float(sample_rate)
        carrier = math.sin(2 * math.pi * 440 * index / sample_rate)
        for segments in channel_segments:
            active = any(start <= time_sec < end for start, end in segments)
            sample = int(10000 * carrier) if active else 0
            frames.append(sample)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack("<" + "h" * len(frames), *frames))


if __name__ == "__main__":
    unittest.main()
