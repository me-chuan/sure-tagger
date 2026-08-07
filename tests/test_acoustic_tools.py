import gzip
import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
import wave

from scripts.run_c50_method_comparison import compare_record as compare_c50_record
from tagger.input_schema import InputSchemaError, validate_input_record
from tagger.pipelines.signal import (
    audit_basic_acoustic,
    audit_speaker,
    audit_sound_field_scene,
    build_arg_parser,
    empty_tags,
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
from tagger.tools.language_content.topic import TopicConfig, validate_payload
from tagger.tools.sound_field_scene.c50_estimator import (
    run as run_c50_estimator,
)
from tagger.tools.sound_field_scene.firered_aed_detector import (
    FireRedAedConfig,
    FireRedAedError,
    run as run_firered_aed_detector,
    validate_aed_output,
)
from tagger.tools.sound_field_scene.panns_background_detector import (
    PannsBackgroundConfig,
    PannsBackgroundError,
    run as run_panns_background_detector,
    select_background_events,
    validate_panns_output,
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
from tagger.tools.speaker.moss_diarizer import (
    MossDiarizeConfig,
    MossDiarizeSubprocessClient,
    parse_moss_text,
    run_channel_purity_check,
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
                panns_config=PannsBackgroundConfig(
                    threshold=0.3,
                    subprocess_python="",
                ),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.6, "/m/0btp2", "Traffic noise")
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
                set(
                    [
                        "far_field",
                        "rt60",
                        "c50",
                        "audio_events",
                        "music",
                        "sound",
                    ]
                ),
            )
            self.assertIsNone(tags["sound_field_scene"]["rt60"])
            self.assertIsNone(tags["sound_field_scene"]["c50"])
            self.assertEqual(
                tags["sound_field_scene"]["audio_events"],
                ["speech", "music"],
            )
            self.assertTrue(tags["sound_field_scene"]["music"])
            self.assertEqual(tags["sound_field_scene"]["sound"], ["Traffic noise"])

    def test_signal_tag_record_populates_deterministic_language_content_without_audio(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record = make_record("missing.wav")
            record["sample"]["text"]["transcript"] = "Um hello hello."

            tags = tag_signal_record(record, tmpdir)

            self.assertIsNone(tags["language_content"]["topic"])
            self.assertEqual(tags["language_content"]["language"], "en")
            self.assertEqual(tags["language_content"]["word_count"], 3)
            self.assertEqual(
                tags["language_content"]["punctuation"],
                {
                    "punctuation_count": 1,
                    "has_terminal_punctuation": True,
                },
            )
            self.assertEqual(
                tags["language_content"]["repetition"],
                {
                    "has_repetition": True,
                    "repetition_count": 1,
                },
            )
            self.assertEqual(tags["language_content"]["filler"], 1)

    def test_signal_pipeline_prefers_native_metadata_segments_for_vad_and_speaker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "meeting.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=5.0)
            record = make_record(str(path))
            record["sample"]["native_metadata"] = {
                "utterances": [
                    {
                        "utt_id": "u1",
                        "speaker": "A",
                        "start": 1.0,
                        "end": 3.0,
                        "text": "first speaker",
                    },
                    {
                        "utt_id": "u2",
                        "speaker": "B",
                        "start": 2.5,
                        "end": 4.0,
                        "text": "second speaker",
                    },
                ]
            }

            tags = tag_signal_record(
                record,
                tmpdir,
                speaker_config=default_speaker_layer_config(enable_moss=False),
                **missing_signal_model_configs(tmpdir)
            )

            self.assertEqual(
                tags["basic_acoustic"]["silence_segments"],
                [
                    {"start_sec": 0.0, "end_sec": 1.0},
                    {"start_sec": 4.0, "end_sec": 5.0},
                ],
            )
            self.assertEqual(tags["basic_acoustic"]["silence_ratio"], 0.4)
            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertTrue(tags["speaker"]["speaker_change"])
            self.assertTrue(tags["speaker"]["speaker_overlap"])

    def test_signal_tag_record_populates_openai_responses_topic_when_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record = make_record("missing.wav")
            record["sample"]["text"]["transcript"] = (
                "We discuss ASR dataset tagging and automatic annotation quality."
            )
            client = FakeTopicClient(
                {
                    "major_topic": "technology_engineering",
                    "minor_topic": "artificial_intelligence",
                    "confidence": 0.82,
                    "topic_keywords": ["ASR", "dataset", "tagging"],
                    "proper_nouns": [],
                    "reason_short": "The transcript discusses ASR annotation.",
                    "secondary_topics": [],
                }
            )

            tags = tag_signal_record(
                record,
                tmpdir,
                topic_config=TopicConfig(enabled=True, cache_enabled=False),
                topic_client=client,
            )

            self.assertEqual(
                tags["language_content"]["topic"],
                "technology_engineering/artificial_intelligence",
            )
            self.assertEqual(client.call_count, 1)

    def test_signal_topic_short_utterance_guard_skips_openai_responses_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record = make_record("missing.wav")
            record["sample"]["text"]["transcript"] = "Yeah."
            client = FakeTopicClient(
                {
                    "major_topic": "technology_engineering",
                    "minor_topic": "artificial_intelligence",
                    "confidence": 0.82,
                    "topic_keywords": [],
                    "proper_nouns": [],
                    "reason_short": "Should not be called.",
                    "secondary_topics": [],
                }
            )

            tags = tag_signal_record(
                record,
                tmpdir,
                topic_config=TopicConfig(enabled=True, cache_enabled=False),
                topic_client=client,
            )

            self.assertEqual(
                tags["language_content"]["topic"],
                "other/insufficient_context",
            )
            self.assertEqual(client.call_count, 0)

    def test_topic_validation_repairs_known_minor_under_wrong_major(self):
        payload = {
            "major_topic": "meeting_workflow",
            "minor_topic": "project_management",
            "confidence": 0.92,
            "topic_keywords": ["prototype", "week six"],
            "proper_nouns": [],
            "reason_short": "The transcript discusses project planning.",
            "secondary_topics": [],
        }

        clean = validate_payload(payload)

        self.assertEqual(clean["major_topic"], "business_management")
        self.assertEqual(clean["minor_topic"], "project_management")

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

    def test_fire_red_aed_maps_event_names_and_music_to_public_tags(self):
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
            self.assertEqual(
                set(by_path),
                set(
                    [
                        "sound_field_scene.audio_events",
                        "sound_field_scene.music",
                    ]
                ),
            )
            self.assertEqual(
                by_path["sound_field_scene.audio_events"].value,
                ["speech", "singing"],
            )
            self.assertFalse(by_path["sound_field_scene.music"].value)
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

    def test_fire_red_aed_returns_empty_event_list_when_nothing_is_detected(self):
        output = {
            "event2timestamps": {"speech": [], "singing": [], "music": []},
            "event2ratio": {"speech": 0.0, "singing": 0.0, "music": 0.0},
        }
        results = run_firered_aed_detector(
            "audio.wav",
            duration_sec=1.0,
            config=FireRedAedConfig(subprocess_python=""),
            client=FakeFireRedAedClient(output),
        )
        by_path = {result.tag_path: result.value for result in results}

        self.assertEqual(by_path["sound_field_scene.audio_events"], [])
        self.assertFalse(by_path["sound_field_scene.music"])

    def test_panns_background_detector_uses_inclusive_threshold(self):
        result = run_panns_background_detector(
            "audio.wav",
            config=PannsBackgroundConfig(threshold=0.3, subprocess_python=""),
            client=FakePannsBackgroundClient(
                make_panns_output(0.3, "/m/04rlf", "Music")
            ),
        )

        self.assertEqual(result.tag_path, "sound_field_scene.sound")
        self.assertEqual(result.value, ["Music"])
        self.assertEqual(result.evidence["max_background_score"], 0.3)
        self.assertEqual(result.evidence["winning_event"]["mid"], "/m/04rlf")

    def test_panns_background_detector_returns_empty_list_below_threshold(self):
        result = run_panns_background_detector(
            "audio.wav",
            config=PannsBackgroundConfig(threshold=0.3, subprocess_python=""),
            client=FakePannsBackgroundClient(
                make_panns_output(0.299999, "/m/0btp2", "Traffic noise")
            ),
        )

        self.assertEqual(result.value, [])

    def test_panns_background_detector_returns_ranked_classes_above_threshold(self):
        events = [
            {
                "index": 1,
                "mid": "/m/0btp2",
                "display_name": "Traffic noise",
                "score": 0.7,
            },
            {
                "index": 2,
                "mid": "/m/07yv9",
                "display_name": "Vehicle",
                "score": 0.4,
            },
            {
                "index": 3,
                "mid": "/m/096m7z",
                "display_name": "Noise",
                "score": 0.2,
            },
        ]
        result = run_panns_background_detector(
            "audio.wav",
            config=PannsBackgroundConfig(threshold=0.3, subprocess_python=""),
            client=FakePannsBackgroundClient(
                {
                    "chunk_count": 1,
                    "max_background_score": 0.7,
                    "winning_event": dict(events[0]),
                    "top_background_events": events,
                }
            ),
        )

        self.assertEqual(result.value, ["Traffic noise", "Vehicle"])

    def test_panns_background_selection_excludes_primary_speech_and_scene(self):
        summary = select_background_events(
            [
                {"index": 0, "mid": "/m/09x0r", "display_name": "Speech"},
                {
                    "index": 1,
                    "mid": "/t/dd00125",
                    "display_name": "Inside, small room",
                },
                {"index": 2, "mid": "/m/04rlf", "display_name": "Music"},
            ],
            [0.99, 0.95, 0.31],
        )

        self.assertEqual(summary["max_background_score"], 0.31)
        self.assertEqual(summary["winning_event"]["mid"], "/m/04rlf")

    def test_panns_background_output_rejects_excluded_winner(self):
        with self.assertRaises(PannsBackgroundError):
            validate_panns_output(
                make_panns_output(0.9, "/m/09x0r", "Speech")
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
            "audio_events": None,
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

    def test_sound_field_auditor_rejects_invalid_event_label_lists(self):
        sound_field_scene = {
            "far_field": None,
            "rt60": None,
            "c50": None,
            "audio_events": ["music", "speech"],
            "music": True,
            "sound": True,
        }

        warnings = audit_sound_field_scene(sound_field_scene)

        self.assertIsNone(sound_field_scene["audio_events"])
        self.assertIsNone(sound_field_scene["sound"])
        self.assertEqual(
            [warning["field"] for warning in warnings],
            ["audio_events", "sound"],
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
                panns_config=PannsBackgroundConfig(
                    threshold=0.3,
                    subprocess_python="",
                ),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.4, "/m/096m7z", "Noise")
                ),
            )

            self.assertEqual(tags["basic_acoustic"]["sample_rate_hz"], 8000)
            self.assertEqual(tags["basic_acoustic"]["channels"], 2)
            self.assertNotIn("rir", tags["sound_field_scene"])
            self.assertIsNotNone(tags["sound_field_scene"]["rt60"])
            self.assertIsNotNone(tags["sound_field_scene"]["c50"])
            self.assertIsNone(tags["basic_acoustic"]["c50"])
            self.assertEqual(tags["sound_field_scene"]["audio_events"], ["speech"])
            self.assertFalse(tags["sound_field_scene"]["music"])
            self.assertEqual(tags["sound_field_scene"]["sound"], ["Noise"])

            artifacts = list((artifact_dir / "rir").glob("*.rir.json.gz"))
            self.assertEqual(len(artifacts), 1)
            with gzip.open(str(artifacts[0]), "rt", encoding="utf-8") as source:
                artifact = json.load(source)
            self.assertEqual(artifact["sample_rate_hz"], 16000)
            self.assertEqual(len(artifact["samples"]), len(rir_samples))

    def test_signal_pipeline_isolates_music_and_sound_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)
            common = {
                "firered_vad_config": FireRedVadConfig(
                    model_dir=str(Path(tmpdir) / "missing_vad"),
                    subprocess_python="",
                ),
                "brouhaha_config": BrouhahaConfig(
                    model_path=str(Path(tmpdir) / "missing_brouhaha.ckpt"),
                    repo_dir=str(Path(tmpdir) / "missing_brouhaha"),
                    subprocess_python="",
                ),
                "recrir_config": RecRirConfig(
                    repo_dir=str(Path(tmpdir) / "missing_recrir"),
                    config_path=str(Path(tmpdir) / "missing.toml"),
                    checkpoint_path=str(Path(tmpdir) / "missing.tar"),
                    subprocess_python="",
                ),
                "dnsmos_config": DnsmosConfig(subprocess_python=""),
                "firered_aed_config": FireRedAedConfig(subprocess_python=""),
                "panns_config": PannsBackgroundConfig(subprocess_python=""),
            }
            fire_output = {
                "event2timestamps": {
                    "speech": [],
                    "singing": [],
                    "music": [[0.1, 0.9]],
                },
                "event2ratio": {"speech": 0.0, "singing": 0.0, "music": 0.8},
            }

            panns_failure = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                firered_aed_client=FakeFireRedAedClient(fire_output),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.9, "/m/09x0r", "Speech")
                ),
                **common
            )
            fire_failure = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                firered_aed_client=FakeFireRedAedClient({}),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.8, "/m/096m7z", "Noise")
                ),
                **common
            )

            self.assertTrue(panns_failure["sound_field_scene"]["music"])
            self.assertEqual(
                panns_failure["sound_field_scene"]["audio_events"],
                ["music"],
            )
            self.assertIsNone(panns_failure["sound_field_scene"]["sound"])
            self.assertIsNone(fire_failure["sound_field_scene"]["music"])
            self.assertIsNone(fire_failure["sound_field_scene"]["audio_events"])
            self.assertEqual(fire_failure["sound_field_scene"]["sound"], ["Noise"])

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

    def test_moss_subprocess_client_calls_local_worker(self):
        config = MossDiarizeConfig(
            model="local-moss",
            subprocess_python="/tmp/moss-python",
            device="cpu",
            torch_dtype="float32",
            max_new_tokens=2048,
        )
        client = MossDiarizeSubprocessClient(config)

        with mock.patch(
            "tagger.tools.speaker.moss_diarizer.run_subprocess_tool",
            return_value={"output": {"text": "[0.00][S01] hi [1.00]"}},
        ) as run_tool:
            output = client.diarize("audio.wav", context={"cache": True})

        self.assertEqual(output["text"], "[0.00][S01] hi [1.00]")
        run_tool.assert_called_once_with(
            "/tmp/moss-python",
            "moss_diarize_estimate",
            {
                "audio_path": "audio.wav",
                "config": {
                    "endpoint": "",
                    "model": "local-moss",
                    "timeout_sec": 900,
                    "max_new_tokens": 2048,
                    "api_key": "",
                    "subprocess_python": "",
                    "device": "cpu",
                    "torch_dtype": "float32",
                    "trust_remote_code": True,
                    "prompt": "",
                },
            },
            context={"cache": True},
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

    def test_moss_channel_purity_check_splits_and_checks_each_channel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            client = FakeMossClient([
                {
                    "segments": [
                        {"start_sec": 0.0, "end_sec": 2.0, "speaker_id": "S01"}
                    ]
                },
                {
                    "segments": [
                        {"start_sec": 0.0, "end_sec": 2.0, "speaker_id": "S07"}
                    ]
                },
            ])

            result = run_channel_purity_check(path, duration_sec=2.0, client=client)

            self.assertTrue(result.value["all_channels_single_speaker"])
            self.assertEqual(
                [item["speaker_count"] for item in result.value["channels"]],
                [1, 1],
            )
            self.assertEqual(client.input_channel_counts, [1, 1])
            self.assertEqual(
                [item.get("source_channel_id") for item in client.contexts],
                ["ch0", "ch1"],
            )

    def test_signal_pipeline_uses_injected_moss_client_for_speaker_tags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mono.wav"
            write_test_wav(path, sample_rate=8000, channels=1, duration_sec=2.0)
            artifact_dir = Path(tmpdir) / "artifacts"
            common = missing_signal_model_configs(tmpdir)

            tags = tag_signal_record(
                make_record(str(path)),
                tmpdir,
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
                **common
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

    def test_signal_pipeline_derives_speaker_target_unit_from_ami_utterance_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "EN2001a_utt_00000.wav"
            write_test_wav(path, sample_rate=8000, channels=1, duration_sec=0.8)
            artifact_dir = Path(tmpdir) / "artifacts"
            record = make_record(str(path))
            record["sample"]["sample_id"] = "EN2001a_utt_00000"
            record["sample"]["native_metadata"] = {
                "utt_id": "EN2001a_utt_00000",
                "audio_id": "EN2001a",
                "speaker": "E",
                "start": 3.168,
                "end": 3.968,
                "text": "'Kay.",
                "words": [
                    {"w": "'Kay", "start": 3.34, "end": 3.88},
                    {"w": ".", "start": 3.88, "end": 3.88},
                ],
            }
            common = missing_signal_model_configs(tmpdir)

            tags = tag_signal_record(
                record,
                tmpdir,
                speaker_config=default_speaker_layer_config(enable_moss=True),
                moss_client=FakeMossClient(
                    {
                        "segments": [
                            {
                                "start_sec": 0.0,
                                "end_sec": 0.8,
                                "speaker_id": "S01",
                            }
                        ]
                    }
                ),
                artifact_dir=artifact_dir,
                **common
            )

            self.assertFalse(tags["speaker"]["multi_speaker"])
            self.assertFalse(tags["speaker"]["speaker_change"])
            self.assertFalse(tags["speaker"]["speaker_overlap"])

            artifacts = list((artifact_dir / "speaker").glob("*.moss_diarize.json.gz"))
            self.assertEqual(len(artifacts), 1)
            with gzip.open(str(artifacts[0]), "rt", encoding="utf-8") as source:
                artifact = json.load(source)
            self.assertEqual(artifact["sample_id"], "EN2001a_utt_00000")
            self.assertEqual(artifact["recording_id"], "EN2001a")
            self.assertEqual(len(artifact["utterances"]), 1)
            utterance = artifact["utterances"][0]
            self.assertEqual(utterance["unit_id"], "EN2001a_utt_00000")
            self.assertEqual(utterance["start_sec"], 0.0)
            self.assertEqual(utterance["end_sec"], 0.8)
            self.assertEqual(utterance["primary_speaker_id"], "spk_001")

    def test_signal_pipeline_uses_merged_headset_moss_for_separated_headset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            artifact_dir = Path(tmpdir) / "artifacts"
            record = make_record(str(path))
            record["sample"]["native_metadata"]["microphone_type"] = "Headset"
            common = missing_signal_model_configs(tmpdir)

            moss_client = FakeMossClient(
                {
                    "segments": [
                        {"start_sec": 0.0, "end_sec": 1.2, "speaker_id": "S01"},
                        {"start_sec": 0.8, "end_sec": 2.0, "speaker_id": "S02"},
                    ]
                }
            )
            tags = tag_signal_record(
                record,
                tmpdir,
                speaker_config=default_speaker_layer_config(enable_moss=True),
                moss_client=moss_client,
                artifact_dir=artifact_dir,
                **common
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
            self.assertEqual(moss_client.input_channel_counts, [1, 1, 1])
            self.assertIn("merged_mono", moss_client.audio_names[-1])

    def test_signal_pipeline_uses_channel_activity_after_moss_purity_check(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            artifact_dir = Path(tmpdir) / "artifacts"
            record = make_record(str(path))
            record["sample"]["native_metadata"]["microphone_type"] = "Headset"
            moss_client = FakeMossClient([
                {
                    "segments": [
                        {"start_sec": 0.0, "end_sec": 2.0, "speaker_id": "S01"}
                    ]
                },
                {
                    "segments": [
                        {"start_sec": 0.0, "end_sec": 2.0, "speaker_id": "S01"}
                    ]
                },
            ])
            channel_client = FakeChannelActivityClient(
                {
                    "metadata_version": "channel_activity_v0.1",
                    "duration_sec": 2.0,
                    "channels": [
                        {
                            "channel_id": "ch0",
                            "speaker_id": "spk_A",
                            "speech_segments": [{"start_sec": 0.0, "end_sec": 1.2}],
                        },
                        {
                            "channel_id": "ch1",
                            "speaker_id": "spk_B",
                            "speech_segments": [{"start_sec": 0.8, "end_sec": 2.0}],
                        },
                    ],
                }
            )

            tags = tag_signal_record(
                record,
                tmpdir,
                speaker_config=default_speaker_layer_config(enable_moss=True),
                moss_client=moss_client,
                channel_activity_client=channel_client,
                artifact_dir=artifact_dir,
            )

            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertEqual(moss_client.input_channel_counts, [1, 1])
            self.assertEqual(channel_client.call_count, 1)
            artifacts = list((artifact_dir / "speaker").glob("*.channel_activity.json.gz"))
            self.assertEqual(len(artifacts), 1)

    def test_force_channel_activity_skips_moss_purity_check(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            config = default_speaker_layer_config(enable_moss=True)
            config.force_channel_activity = True
            moss_client = FakeMossClient({"segments": []})
            channel_client = FakeChannelActivityClient(
                {
                    "metadata_version": "channel_activity_v0.1",
                    "duration_sec": 2.0,
                    "channels": [
                        {
                            "channel_id": "ch0",
                            "speaker_id": "spk_A",
                            "speech_segments": [{"start_sec": 0.0, "end_sec": 1.2}],
                        },
                        {
                            "channel_id": "ch1",
                            "speaker_id": "spk_B",
                            "speech_segments": [{"start_sec": 0.8, "end_sec": 2.0}],
                        },
                    ],
                }
            )

            tags = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                speaker_config=config,
                moss_client=moss_client,
                channel_activity_client=channel_client,
            )

            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertEqual(moss_client.input_channel_counts, [])
            self.assertEqual(channel_client.call_count, 1)

    def test_channel_activity_requires_purity_confirmation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            channel_client = FakeChannelActivityClient(
                {
                    "metadata_version": "channel_activity_v0.1",
                    "duration_sec": 2.0,
                    "channels": [
                        {
                            "channel_id": "ch0",
                            "speaker_id": "spk_A",
                            "speech_segments": [{"start_sec": 0.0, "end_sec": 2.0}],
                        },
                        {
                            "channel_id": "ch1",
                            "speaker_id": "spk_B",
                            "speech_segments": [{"start_sec": 0.0, "end_sec": 2.0}],
                        },
                    ],
                }
            )

            tags = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                speaker_config=default_speaker_layer_config(enable_moss=False),
                channel_activity_client=channel_client,
            )

            self.assertIsNone(tags["speaker"]["multi_speaker"])
            self.assertIsNone(tags["speaker"]["speaker_change"])
            self.assertIsNone(tags["speaker"]["speaker_overlap"])
            self.assertEqual(channel_client.call_count, 0)

    def test_speaker_force_channel_activity_cli_aliases(self):
        for option in (
            "--speaker-force-channel-activity",
            "--speaker-single-speaker-per-channel",
            "--speaker-prefer-channel-activity",
        ):
            args = build_arg_parser().parse_args([option])
            self.assertTrue(args.speaker_force_channel_activity)

        self.assertEqual(
            default_speaker_layer_config().channel_activity_config.energy_threshold,
            200.0,
        )

        args = build_arg_parser().parse_args(
            [
                "--topic-enable",
                "--topic-model",
                "gpt-5.5",
                "--topic-api-key-path",
                "api.txt",
            ]
        )
        self.assertTrue(args.topic_enable)
        self.assertEqual(args.topic_model, "gpt-5.5")
        self.assertEqual(args.topic_api_key_path, "api.txt")

        args = build_arg_parser().parse_args(
            [
                "--sample-id",
                "utt1",
                "--input-tags",
                "old.jsonl",
                "--only-tags",
                "speaker,language_content.topic",
                "--missing-only",
            ]
        )
        self.assertEqual(args.sample_id, ["utt1"])
        self.assertEqual(args.input_tags, "old.jsonl")
        self.assertEqual(args.only_tags, "speaker,language_content.topic")
        self.assertTrue(args.missing_only)

    def test_signal_manifest_passes_injected_channel_activity_client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "stereo.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            manifest_path = Path(tmpdir) / "manifest.jsonl"
            output_path = Path(tmpdir) / "tags.jsonl"
            with manifest_path.open("w", encoding="utf-8") as sink:
                sink.write(json.dumps(make_record(str(path)), ensure_ascii=False) + "\n")
            common = missing_signal_model_configs(tmpdir)

            run_signal_manifest(
                manifest_path,
                output_path,
                speaker_config=_forced_channel_activity_config(),
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
                **common
            )

            with output_path.open("r", encoding="utf-8") as source:
                tags = json.loads(source.readline())
            self.assertTrue(tags["speaker"]["multi_speaker"])
            self.assertTrue(tags["speaker"]["speaker_change"])
            self.assertTrue(tags["speaker"]["speaker_overlap"])
            self.assertNotIn("channel_activity", tags["speaker"])

    def test_signal_manifest_supplements_selected_sample_tags_from_existing_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.jsonl"
            input_tags_path = Path(tmpdir) / "existing_tags.jsonl"
            output_path = Path(tmpdir) / "updated_tags.jsonl"
            first = make_record("missing_first.wav")
            first["sample"]["sample_id"] = "first"
            first["sample"]["text"]["transcript"] = "Um hello."
            second = make_record("missing_second.wav")
            second["sample"]["sample_id"] = "second"
            second["sample"]["text"]["transcript"] = "Keep this row."
            with manifest_path.open("w", encoding="utf-8") as sink:
                sink.write(json.dumps(first, ensure_ascii=False) + "\n")
                sink.write(json.dumps(second, ensure_ascii=False) + "\n")

            first_tags = empty_tags()
            second_tags = empty_tags()
            second_tags["language_content"]["filler"] = 99
            with input_tags_path.open("w", encoding="utf-8") as sink:
                sink.write(json.dumps(first_tags, ensure_ascii=False) + "\n")
                sink.write(json.dumps(second_tags, ensure_ascii=False) + "\n")

            summary = run_signal_manifest(
                manifest_path,
                output_path,
                sample_ids=["first"],
                existing_tags_path=input_tags_path,
                selected_tag_paths=["language_content.filler"],
            )

            with output_path.open("r", encoding="utf-8") as source:
                rows = [json.loads(line) for line in source if line.strip()]
            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(summary["processed_sample_count"], 1)
            self.assertEqual(rows[0]["language_content"]["filler"], 1)
            self.assertEqual(rows[1]["language_content"]["filler"], 99)
            self.assertIsNone(rows[0]["basic_acoustic"]["duration_sec"])

    def test_signal_pipeline_does_not_treat_mix_headset_stereo_as_separated_channels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.Mix-Headset.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=2.0)
            common = missing_signal_model_configs(tmpdir)

            tags = tag_signal_record(
                make_record(str(path)),
                tmpdir,
                speaker_config=default_speaker_layer_config(enable_moss=False),
                **common
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


class FakeFireRedAedClient:
    def __init__(self, output):
        self.output = output

    def detect_audio_events(self, audio_path, context=None):
        return self.output


class FakePannsBackgroundClient:
    def __init__(self, output):
        self.output = output

    def estimate(self, audio_path, context=None):
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


class FakeTopicClient:
    def __init__(self, output):
        self.output = output
        self.call_count = 0
        self.prompts = []

    def complete_json(self, prompt):
        self.call_count += 1
        self.prompts.append(prompt)
        return self.output


class FakeRecRirClient:
    def __init__(self, output):
        self.output = output

    def estimate_rir(self, audio_path, context=None):
        return self.output


def make_panns_output(score, mid, display_name):
    event = {
        "index": 1,
        "mid": mid,
        "display_name": display_name,
        "score": score,
    }
    return {
        "chunk_count": 1,
        "max_background_score": score,
        "winning_event": dict(event),
        "top_background_events": [dict(event)],
    }


class FakeMossClient:
    def __init__(self, output):
        if isinstance(output, list):
            self.outputs = list(output)
            self.output = None
        else:
            self.outputs = None
            self.output = output
        self.audio_names = []
        self.contexts = []
        self.input_channel_counts = []

    def diarize(self, audio_path, context=None):
        self.audio_names.append(Path(audio_path).name)
        self.contexts.append(dict(context or {}))
        with wave.open(str(audio_path), "rb") as source:
            self.input_channel_counts.append(source.getnchannels())
        if self.outputs is not None:
            if not self.outputs:
                return {"segments": []}
            return self.outputs.pop(0)
        return self.output


class FakeChannelActivityClient:
    def __init__(self, output):
        self.output = output
        self.call_count = 0

    def detect_channel_activity(self, audio_path, context=None):
        self.call_count += 1
        return self.output


def missing_signal_model_configs(tmpdir):
    root = Path(tmpdir)
    return {
        "firered_vad_config": FireRedVadConfig(
            model_dir=str(root / "missing_vad"),
            subprocess_python="",
        ),
        "brouhaha_config": BrouhahaConfig(
            model_path=str(root / "missing_brouhaha.ckpt"),
            repo_dir=str(root / "missing_brouhaha_repo"),
            subprocess_python="",
        ),
        "recrir_config": RecRirConfig(
            repo_dir=str(root / "missing_recrir_repo"),
            config_path=str(root / "missing_recrir.toml"),
            checkpoint_path=str(root / "missing_recrir.tar"),
            subprocess_python="",
        ),
        "dnsmos_config": DnsmosConfig(
            primary_model_path=str(root / "missing_dnsmos.onnx"),
            p808_model_path=str(root / "missing_p808.onnx"),
            personalized_model_path=str(root / "missing_pdnsmos.onnx"),
            subprocess_python="",
        ),
        "firered_aed_config": FireRedAedConfig(
            model_dir=str(root / "missing_aed"),
            subprocess_python="",
        ),
        "panns_config": PannsBackgroundConfig(
            repo_dir=str(root / "missing_panns_repo"),
            checkpoint_path=str(root / "missing_panns.pth"),
            subprocess_python="",
        ),
    }


def _forced_channel_activity_config():
    config = default_speaker_layer_config(enable_moss=False)
    config.force_channel_activity = True
    return config


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
