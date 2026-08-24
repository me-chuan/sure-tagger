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
from tagger.pipelines.tagging import (
    FULL_STAGES,
    STAGE_PANNS,
    _stages_for_tag_paths,
    audit_audio_quality,
    audit_basic_acoustic,
    audit_room_acoustic,
    audit_speaker,
    audit_sound_field_scene,
    build_arg_parser,
    empty_tags,
    resolve_audio_path,
    run_manifest as run_tagging_manifest,
    tag_record as tag_sample_record,
)
from tagger.tools.acoustic_io import probe_audio_info
from tagger.tools.audio_quality.brouhaha_signal_estimator import (
    BrouhahaConfig,
    run as run_brouhaha_signal_estimator,
)
from tagger.tools.basic_acoustic.brouhaha_vad_silence_detector import (
    run as run_brouhaha_vad_silence_detector,
)
from tagger.tools.audio_quality.dnsmos_quality_estimator import (
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
from tagger.tools.room_acoustic.c50_estimator import (
    run as run_c50_estimator,
)
from tagger.tools.sound_field_scene.dass_categories import (
    build_category_composition,
    classify_dass_label,
)
from tagger.tools.sound_field_scene.dass_noise_type_detector import (
    DassNoiseTypeConfig,
    DassNoiseTypeError,
    run as run_dass_noise_type_detector,
    select_noise_type_events,
    validate_dass_output,
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
from tagger.tools.room_acoustic.rir_estimator import (
    RecRirConfig,
    RecRirError,
    run as run_recrir_rir_estimator,
)
from tagger.tools.room_acoustic.rt60_estimator import (
    run as run_rt60_estimator,
)
from tagger.tools.speaker.metrics import (
    SpeakerMetricsConfig,
    build_metadata_from_timeline,
    public_results_from_metadata,
)
from tagger.tools.speaker.moss_diarizer import (
    MossDiarizeConfig,
    MossDiarizeSubprocessClient,
    parse_moss_text,
)


class AcousticToolsTest(unittest.TestCase):
    def setUp(self):
        self.speaker_v2_patcher = mock.patch(
            "tagger.pipelines.tagging.run_speaker_v2_record",
            return_value={
                "speaker": {
                    "speaker_count": 1,
                    "multi_speaker": False,
                    "speaker_change_count": 0,
                    "speaker_change": False,
                    "overlap_ratio": 0.0,
                    "speaker_overlap": False,
                },
                "run_profile": "quality-shadow",
                "policy_version": "policy-v1",
                "policy_hash": "hash",
                "fusion_artifact": "fusion.json.gz",
                "artifacts": {},
            },
        )
        self.speaker_v2_patcher.start()
        self.addCleanup(self.speaker_v2_patcher.stop)

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

    def test_tagging_record_returns_acoustic_and_sound_field_tags_only(self):
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

            tags = tag_sample_record(
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
                dass_config=DassNoiseTypeConfig(
                    threshold=0.5,
                    subprocess_python="",
                ),
                dass_client=FakeDassNoiseTypeClient(
                    make_dass_output(0.8, "Traffic noise")
                ),
            )

            self.assertEqual(
                set(tags.keys()),
                set(
                    [
                        "basic_acoustic",
                        "audio_quality",
                        "room_acoustic",
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
                    ]
                ),
            )
            self.assertEqual(tags["basic_acoustic"]["duration_sec"], 1.0)
            self.assertEqual(tags["basic_acoustic"]["sample_rate_hz"], 16000)
            self.assertEqual(tags["basic_acoustic"]["channels"], 1)
            self.assertIsNone(tags["basic_acoustic"]["silence_ratio"])
            self.assertIsNone(tags["basic_acoustic"]["silence_segments"])
            self.assertIsNone(tags["audio_quality"]["snr_db"])
            self.assertEqual(tags["audio_quality"]["dnsmos_sig"], 4.1)
            self.assertEqual(tags["audio_quality"]["dnsmos_bak"], 3.2)
            self.assertEqual(tags["audio_quality"]["dnsmos_ovrl"], 3.5)
            self.assertEqual(tags["audio_quality"]["dnsmos_p808"], 3.8)
            self.assertEqual(
                set(tags["room_acoustic"].keys()),
                set(
                    [
                        "far_field",
                        "rt60_sec",
                        "c50_db",
                    ]
                ),
            )
            self.assertIsNone(tags["room_acoustic"]["far_field"])
            self.assertIsNone(tags["room_acoustic"]["rt60_sec"])
            self.assertIsNone(tags["room_acoustic"]["c50_db"])
            self.assertEqual(
                set(tags["sound_field_scene"].keys()),
                set(
                    [
                        "speech_music_events",
                        "music_present",
                        "sound",
                        "external_noise_type",
                        "noise_composition",
                    ]
                ),
            )
            self.assertEqual(
                tags["sound_field_scene"]["speech_music_events"],
                ["speech", "music"],
            )
            self.assertTrue(tags["sound_field_scene"]["music_present"])
            # PANNs is not part of the default pipeline anymore; the sound
            # field stays null unless the panns stage is selected explicitly.
            self.assertIsNone(tags["sound_field_scene"]["sound"])
            self.assertEqual(
                tags["sound_field_scene"]["external_noise_type"],
                ["mechanical"],
            )
            self.assertEqual(
                tags["sound_field_scene"]["noise_composition"],
                {
                    "music": [],
                    "animal": [],
                    "mechanical": ["Traffic noise"],
                    "nature": [],
                    "formless": [],
                    "channel_environment": [],
                },
            )

    def test_tagging_record_populates_deterministic_text_tags_without_audio(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record = make_record("missing.wav")
            record["sample"]["text"]["transcript"] = "Um hello hello."

            tags = tag_sample_record(record, tmpdir)

            self.assertIsNone(tags["language_content"]["topic"])
            # language_content.language now comes from FireRed LID, an
            # audio-dependent stage; without audio it stays null.
            self.assertIsNone(tags["language_content"]["language"])
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

    def test_tagging_pipeline_uses_speaker_v2_public_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "meeting.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=5.0)
            record = make_record(str(path))
            record["sample"]["native_metadata"] = {
                "speaker_segments": [
                    {"speaker": "native-only", "start": 0.0, "end": 5.0}
                ]
            }
            speaker_config = object()
            artifact_dir = Path(tmpdir) / "custom-artifacts"
            public_speaker = {
                "speaker_count": 2,
                "multi_speaker": True,
                "speaker_change_count": 3,
                "speaker_change": True,
                "overlap_ratio": 0.25,
                "speaker_overlap": True,
            }
            result = {
                "speaker": public_speaker,
                "run_profile": "quality-shadow",
                "policy_version": "policy-v1",
                "policy_hash": "hash",
                "fusion_artifact": "fusion.json.gz",
                "artifacts": {"sample_dir": "speaker_v2/sample"},
            }

            with mock.patch(
                "tagger.pipelines.tagging.run_speaker_v2_record",
                return_value=result,
            ) as run_speaker:
                tags = tag_sample_record(
                    record,
                    tmpdir,
                    speaker_config=speaker_config,
                    artifact_dir=artifact_dir,
                    selected_tag_paths=["speaker"],
                )

            self.assertEqual(tags["speaker"], public_speaker)
            args, kwargs = run_speaker.call_args
            self.assertIs(args[0], record)
            self.assertEqual(Path(args[1]), Path(tmpdir))
            self.assertEqual(Path(args[2]), Path(tmpdir))
            self.assertIs(args[3], speaker_config)
            self.assertIsInstance(kwargs["context"], dict)
            self.assertEqual(kwargs["artifact_root"], artifact_dir)
            self.assertTrue(kwargs["artifact_sample_id"].endswith("sample-1"))

    def test_tagging_record_populates_openai_responses_topic_when_enabled(self):
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

            tags = tag_sample_record(
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

    def test_topic_prompt_ignores_sample_utterance_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript = (
                "We compare whether the NITE XML interface is compatible with "
                "the current meeting annotation workflow."
            )
            base_record = make_record("missing.wav")
            base_record["sample"]["text"]["transcript"] = transcript
            base_record["sample"]["native_metadata"] = {}
            annotated_record = json.loads(json.dumps(base_record))
            annotated_record["sample"]["native_metadata"] = {
                "utterances": [
                    {
                        "speaker": "E",
                        "start": 0.0,
                        "end": 4.0,
                        "text": transcript,
                    },
                    {
                        "speaker": "A",
                        "start": 2.0,
                        "end": 2.3,
                        "text": "Yeah.",
                    },
                ]
            }
            output = {
                "major_topic": "technology_engineering",
                "minor_topic": "software_engineering",
                "confidence": 0.82,
                "topic_keywords": ["NITE XML", "interface"],
                "proper_nouns": ["NITE XML"],
                "reason_short": "The transcript discusses interface compatibility.",
                "secondary_topics": [],
            }

            clients = []
            for record in (base_record, annotated_record):
                client = FakeTopicClient(output)
                tag_sample_record(
                    record,
                    tmpdir,
                    topic_config=TopicConfig(enabled=True, cache_enabled=False),
                    topic_client=client,
                    selected_tag_paths=["language_content.topic"],
                )
                clients.append(client)

            plain_prompt = json.loads(clients[0].prompts[0])
            annotated_prompt = json.loads(clients[1].prompts[0])
            self.assertEqual(plain_prompt, annotated_prompt)
            self.assertEqual(plain_prompt["context"]["target_granularity"], "sample")
            self.assertNotIn(
                "Do not borrow a substantive topic",
                "\n".join(plain_prompt["rules"]),
            )

    def test_topic_short_utterance_guard_skips_openai_responses_call(self):
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

            tags = tag_sample_record(
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

    def test_tagging_pipeline_skips_speech_dependent_stages_without_transcript(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "noise.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=2.0)
            record = make_record(str(path))
            record["sample"]["text"]["transcript"] = ""
            topic_client = FakeTopicClient(
                {
                    "major_topic": "daily_life_social",
                    "minor_topic": "small_talk",
                    "confidence": 0.8,
                    "topic_keywords": [],
                    "proper_nouns": [],
                    "reason_short": "Should not be called.",
                    "secondary_topics": [],
                }
            )
            dnsmos_client = FakeDnsmosClient(
                {
                    "sig": 3.0,
                    "bak": 3.0,
                    "ovr": 3.0,
                    "p808_mos": 3.0,
                }
            )
            recrir_client = FakeRecRirClient(
                {
                    "metadata_version": "rec_rir_v0.1",
                    "sample_rate_hz": 16000,
                    "rir": [1.0, 0.0],
                }
            )

            tags = tag_sample_record(
                record,
                tmpdir,
                dnsmos_client=dnsmos_client,
                recrir_client=recrir_client,
                topic_config=TopicConfig(enabled=True, cache_enabled=False),
                topic_client=topic_client,
                selected_tag_paths=[
                    "language_content",
                    "basic_acoustic.silence_ratio",
                    "audio_quality.dnsmos_ovrl",
                    "speaker",
                    "room_acoustic.rt60_sec",
                ],
                **missing_external_model_configs(tmpdir)
            )

            self.assertEqual(topic_client.call_count, 0)
            self.assertEqual(dnsmos_client.call_count, 0)
            self.assertEqual(recrir_client.call_count, 0)
            self.assertTrue(all(value is None for value in tags["language_content"].values()))
            self.assertIsNone(tags["basic_acoustic"]["silence_segments"])
            self.assertIsNone(tags["basic_acoustic"]["silence_ratio"])
            self.assertIsNone(tags["audio_quality"]["dnsmos_ovrl"])
            self.assertIsNone(tags["room_acoustic"]["rt60_sec"])
            self.assertIsNone(tags["room_acoustic"]["c50_db"])
            self.assertFalse(tags["speaker"]["multi_speaker"])
            self.assertFalse(tags["speaker"]["speaker_change"])
            self.assertFalse(tags["speaker"]["speaker_overlap"])

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
                        "sound_field_scene.speech_music_events",
                        "sound_field_scene.music_present",
                    ]
                ),
            )
            self.assertEqual(
                by_path["sound_field_scene.speech_music_events"].value,
                ["speech", "singing"],
            )
            self.assertFalse(by_path["sound_field_scene.music_present"].value)
            self.assertEqual(
                by_path["sound_field_scene.music_present"].evidence[
                    "event_ratios"
                ]["speech"],
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

        self.assertEqual(by_path["sound_field_scene.speech_music_events"], [])
        self.assertFalse(by_path["sound_field_scene.music_present"])

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

    def test_dass_noise_type_detector_uses_inclusive_threshold(self):
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(threshold=0.5, subprocess_python=""),
            client=FakeDassNoiseTypeClient(make_dass_output(0.5, "Traffic noise")),
        )
        by_path = {result.tag_path: result for result in results}
        result = by_path["sound_field_scene.external_noise_type"]

        self.assertEqual(result.tag_path, "sound_field_scene.external_noise_type")
        self.assertEqual(result.value, ["mechanical"])
        self.assertEqual(result.evidence["max_noise_score"], 0.5)
        self.assertEqual(result.evidence["winning_event"]["display_name"], "Traffic noise")

    def test_dass_noise_type_detector_default_threshold_is_calibrated(self):
        # Regressed on 2026-08-24: the default was lowered from the AudioSet
        # convention 0.50 to 0.25 because DASS-medium noise scores are soft.
        self.assertEqual(DassNoiseTypeConfig().threshold, 0.25)
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(subprocess_python=""),
            client=FakeDassNoiseTypeClient(make_dass_output(0.3, "Traffic noise")),
        )
        by_path = {result.tag_path: result for result in results}

        self.assertEqual(
            by_path["sound_field_scene.external_noise_type"].value, ["mechanical"]
        )

    def test_dass_noise_type_detector_returns_empty_list_below_threshold(self):
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(threshold=0.5, subprocess_python=""),
            client=FakeDassNoiseTypeClient(make_dass_output(0.499999, "Traffic noise")),
        )
        by_path = {result.tag_path: result for result in results}

        # External categories derive from the full vector at the (higher)
        # threshold: 0.499999 stays below 0.5, so no category is present.
        self.assertEqual(by_path["sound_field_scene.external_noise_type"].value, [])
        # Composition has its own (lower) threshold, so the same event still
        # enters the composition bucket.
        self.assertEqual(
            by_path["sound_field_scene.noise_composition"].value["mechanical"],
            ["Traffic noise"],
        )

    def test_dass_noise_type_detector_returns_ranked_classes_above_threshold(self):
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(threshold=0.5, subprocess_python=""),
            client=FakeDassNoiseTypeClient(
                make_dass_output(
                    0.7,
                    "Traffic noise",
                    extra_events=[(0.6, "Vehicle"), (0.2, "Noise")],
                )
            ),
        )
        by_path = {result.tag_path: result for result in results}

        # Both events share the mechanical category; "Noise" (0.2) stays
        # below the threshold so channel_environment is absent.
        self.assertEqual(
            by_path["sound_field_scene.external_noise_type"].value,
            ["mechanical"],
        )

    def test_dass_detector_orders_external_categories_by_best_score(self):
        # Categories are derived from the full 527-class vector (the
        # exclusion policy does not apply) and ordered by each category's
        # best label score.
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(threshold=0.4, subprocess_python=""),
            client=FakeDassNoiseTypeClient(
                make_dass_output(
                    0.8,
                    "Traffic noise",
                    extra_vector_events=[
                        (0.9, "Rain"),
                        (0.6, "Dog"),
                        (0.4, "Music"),
                    ],
                )
            ),
        )
        by_path = {result.tag_path: result for result in results}

        self.assertEqual(
            by_path["sound_field_scene.external_noise_type"].value,
            ["nature", "mechanical", "animal", "music"],
        )

    def test_dass_detector_ignores_excluded_labels_in_external_categories(self):
        # Silence (formless) is excluded by policy and must not drive the
        # external category list, while Traffic noise (mechanical) does.
        # Regressed on 2026-08-24: deriving categories from the raw full
        # vector flagged clean-speech samples as formless via Silence.
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(threshold=0.25, subprocess_python=""),
            client=FakeDassNoiseTypeClient(
                make_dass_output(
                    0.6,
                    "Traffic noise",
                    extra_vector_events=[(0.9, "Silence")],
                )
            ),
        )
        by_path = {result.tag_path: result for result in results}

        self.assertEqual(
            by_path["sound_field_scene.external_noise_type"].value,
            ["mechanical"],
        )
        # Composition reads the full vector and is unaffected by the policy.
        self.assertEqual(
            by_path["sound_field_scene.noise_composition"].value["formless"],
            ["Silence"],
        )

    def test_dass_noise_type_selection_excludes_primary_speech_and_scene(self):
        summary = select_noise_type_events(
            [
                {"index": 0, "display_name": "Speech"},
                {"index": 1, "display_name": "Inside, small room"},
                {"index": 2, "display_name": "Music"},
            ],
            [0.99, 0.95, 0.51],
        )

        self.assertEqual(summary["max_noise_score"], 0.51)
        self.assertEqual(summary["winning_event"]["display_name"], "Music")

    def test_dass_noise_type_output_rejects_excluded_winner(self):
        with self.assertRaises(DassNoiseTypeError):
            validate_dass_output(make_dass_output(0.9, "Speech"))

    def test_dass_noise_type_selection_keeps_all_classes_without_exclusion(self):
        summary = select_noise_type_events(
            [
                {"index": 0, "display_name": "Speech"},
                {"index": 1, "display_name": "Silence"},
                {"index": 2, "display_name": "Music"},
            ],
            [0.99, 0.95, 0.51],
            exclude_classes=False,
        )

        self.assertEqual(summary["max_noise_score"], 0.99)
        self.assertEqual(summary["winning_event"]["display_name"], "Speech")
        self.assertEqual(
            [item["display_name"] for item in summary["top_noise_events"]],
            ["Speech", "Silence", "Music"],
        )

    def test_dass_noise_type_output_accepts_silence_winner_without_exclusion(self):
        summary = validate_dass_output(
            make_dass_output(0.9, "Silence"), exclude_classes=False
        )

        self.assertEqual(summary["winning_event"]["display_name"], "Silence")

    def test_dass_noise_type_output_accepts_speech_winner_without_exclusion(self):
        summary = validate_dass_output(
            make_dass_output(0.9, "Speech"), exclude_classes=False
        )

        self.assertEqual(summary["winning_event"]["display_name"], "Speech")

    def test_dass_noise_type_output_accepts_scene_winner_without_exclusion(self):
        summary = validate_dass_output(
            make_dass_output(0.9, "Inside, small room"), exclude_classes=False
        )

        self.assertEqual(summary["winning_event"]["display_name"], "Inside, small room")

    def test_dass_noise_type_detector_publishes_all_classes_without_exclusion(self):
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(
                threshold=0.5, exclude_classes=False, subprocess_python=""
            ),
            client=FakeDassNoiseTypeClient(make_dass_output(0.8, "Speech")),
        )
        by_path = {result.tag_path: result for result in results}
        result = by_path["sound_field_scene.external_noise_type"]

        self.assertEqual(result.tag_path, "sound_field_scene.external_noise_type")
        # Speech classifies into the human category, which is evidence-only:
        # it never enters the public external_noise_type value.
        self.assertEqual(result.value, [])
        self.assertEqual(result.evidence["winning_event"]["display_name"], "Speech")
        self.assertFalse(result.evidence["config"]["exclude_classes"])
        # Human labels never enter the public composition either, even with
        # exclusion disabled.
        self.assertEqual(
            by_path["sound_field_scene.noise_composition"].value["formless"],
            [],
        )

    def test_default_full_pipeline_excludes_panns_stage(self):
        self.assertNotIn(STAGE_PANNS, FULL_STAGES)
        self.assertNotIn(STAGE_PANNS, _stages_for_tag_paths(None))
        self.assertIn(STAGE_PANNS, _stages_for_tag_paths(["panns"]))
        self.assertIn(STAGE_PANNS, _stages_for_tag_paths(["sound_field_scene.sound"]))

    def test_tagging_pipeline_publishes_dass_all_classes_without_exclusion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)
            configs = missing_external_model_configs(tmpdir)
            configs["dass_config"] = DassNoiseTypeConfig(
                threshold=0.5, exclude_classes=False, subprocess_python=""
            )

            tags = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                dass_client=FakeDassNoiseTypeClient(
                    make_dass_output(0.9, "Silence")
                ),
                **configs
            )

            self.assertEqual(
                tags["sound_field_scene"]["external_noise_type"], ["formless"]
            )
            self.assertEqual(
                tags["sound_field_scene"]["noise_composition"],
                {
                    "music": [],
                    "animal": [],
                    "mechanical": [],
                    "nature": [],
                    "formless": ["Silence"],
                    "channel_environment": [],
                },
            )

    def test_tagging_pipeline_runs_panns_when_explicitly_selected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            tags = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                selected_tag_paths=["panns"],
                panns_config=PannsBackgroundConfig(
                    threshold=0.3, subprocess_python=""
                ),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.6, "/m/0btp2", "Traffic noise")
                ),
            )

            self.assertEqual(tags["sound_field_scene"]["sound"], ["Traffic noise"])
            self.assertIsNone(
                tags["sound_field_scene"]["external_noise_type"]
            )

    def test_tagging_pipeline_nulls_dass_noise_type_on_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)

            tags = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                **missing_external_model_configs(tmpdir),
            )

            self.assertIsNone(tags["sound_field_scene"]["external_noise_type"])
            self.assertIsNone(tags["sound_field_scene"]["noise_composition"])

    def test_classify_dass_label_assigns_expected_categories(self):
        self.assertEqual(classify_dass_label("Speech"), "human")
        self.assertEqual(
            classify_dass_label("Traffic noise, roadway noise"), "mechanical"
        )
        self.assertEqual(classify_dass_label("Music"), "music")
        self.assertEqual(classify_dass_label("Rain"), "nature")
        self.assertEqual(classify_dass_label("Silence"), "formless")
        self.assertEqual(classify_dass_label("Reverberation"), "channel_environment")
        self.assertEqual(classify_dass_label("class_123"), "other")

    def test_classify_dass_label_covers_deployed_checkpoint(self):
        import json

        checkpoint_config = (
            Path(__file__).resolve().parents[1]
            / "models"
            / "DASS"
            / "saurabhati__DASS_medium_AudioSet_48.9"
            / "config.json"
        )
        with open(str(checkpoint_config), encoding="utf-8") as source:
            id2label = json.load(source)["id2label"]
        for index in range(527):
            category = classify_dass_label(id2label[str(index)])
            self.assertIn(
                category,
                ("music", "animal", "mechanical", "nature", "formless",
                 "channel_environment", "human", "other"),
            )
        categories = {
            classify_dass_label(id2label[str(index)]) for index in range(527)
        }
        self.assertNotIn("other", categories)

    def test_dass_category_composition_ranks_filters_and_truncates(self):
        labels = [
            {"index": index, "display_name": "class_%03d" % index}
            for index in range(4)
        ]
        labels[1] = {"index": 1, "display_name": "Car"}
        labels[2] = {"index": 2, "display_name": "Truck"}
        labels[3] = {"index": 3, "display_name": "Rain"}
        scores = [0.0, 0.8, 0.6, 0.4]
        composition, category_events = build_category_composition(
            labels, scores, threshold=0.5, top_k=3, music_present=None
        )

        self.assertEqual(composition["mechanical"], ["Car", "Truck"])
        self.assertEqual(composition["nature"], [])
        self.assertEqual(
            category_events["mechanical"],
            [
                {"index": 1, "display_name": "Car", "score": 0.8},
                {"index": 2, "display_name": "Truck", "score": 0.6},
            ],
        )

    def test_dass_category_composition_truncates_per_category(self):
        labels = [
            {"index": index, "display_name": "class_%03d" % index}
            for index in range(6)
        ]
        names = ["Car", "Bus", "Train", "Bicycle", "Radio"]
        for offset, name in enumerate(names, start=1):
            labels[offset] = {"index": offset, "display_name": name}
        scores = [0.0, 0.9, 0.85, 0.8, 0.75, 0.7]
        composition, category_events = build_category_composition(
            labels, scores, threshold=0.5, top_k=3, music_present=None
        )

        self.assertEqual(composition["mechanical"], ["Car", "Bus", "Train"])
        self.assertEqual(
            [item["display_name"] for item in category_events["mechanical"]],
            ["Car", "Bus", "Train"],
        )

    def test_dass_category_composition_applies_music_gate(self):
        labels = [
            {"index": index, "display_name": "class_%03d" % index}
            for index in range(2)
        ]
        labels[1] = {"index": 1, "display_name": "Music"}
        scores = [0.0, 0.9]

        kept, _events = build_category_composition(
            labels, scores, threshold=0.5, top_k=3, music_present=True
        )
        gated, _events = build_category_composition(
            labels, scores, threshold=0.5, top_k=3, music_present=False
        )
        unguarded, events = build_category_composition(
            labels, scores, threshold=0.5, top_k=3, music_present=None
        )

        self.assertEqual(kept["music"], ["Music"])
        self.assertEqual(gated["music"], [])
        self.assertEqual(unguarded["music"], ["Music"])
        self.assertEqual(events["music"][0]["score"], 0.9)

    def test_dass_category_composition_keeps_human_in_evidence_only(self):
        labels = [
            {"index": index, "display_name": "class_%03d" % index}
            for index in range(2)
        ]
        labels[1] = {"index": 1, "display_name": "Laughter"}
        scores = [0.0, 0.8]
        composition, category_events = build_category_composition(
            labels, scores, threshold=0.5, top_k=3, music_present=None
        )

        for values in composition.values():
            self.assertEqual(values, [])
        self.assertEqual(
            category_events["human"],
            [{"index": 1, "display_name": "Laughter", "score": 0.8}],
        )

    def test_dass_detector_publishes_composition_with_music_gate(self):
        results = run_dass_noise_type_detector(
            "audio.wav",
            config=DassNoiseTypeConfig(threshold=0.5, subprocess_python=""),
            client=FakeDassNoiseTypeClient(
                make_dass_output(
                    0.8,
                    "Traffic noise",
                    extra_vector_events=[(0.6, "Music"), (0.7, "Laughter")],
                )
            ),
            music_present=False,
        )
        by_path = {result.tag_path: result for result in results}
        composition_result = by_path["sound_field_scene.noise_composition"]

        self.assertEqual(
            composition_result.value,
            {
                "music": [],
                "animal": [],
                "mechanical": ["Traffic noise"],
                "nature": [],
                "formless": [],
                "channel_environment": [],
            },
        )
        self.assertEqual(
            composition_result.evidence["music_gate"],
            {"aed_music_present": False, "gated": True},
        )
        self.assertEqual(
            composition_result.evidence["category_events"]["human"][0][
                "display_name"
            ],
            "Laughter",
        )

    def test_tagging_pipeline_gates_dass_music_by_firered_aed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)
            configs = missing_external_model_configs(tmpdir)
            configs["firered_aed_config"] = FireRedAedConfig(
                model_dir=str(Path(tmpdir) / "missing_aed"),
                subprocess_python="",
            )
            configs["firered_aed_client"] = FakeFireRedAedClient(
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
            )
            configs["dass_client"] = FakeDassNoiseTypeClient(
                make_dass_output(
                    0.8,
                    "Traffic noise",
                    extra_vector_events=[(0.6, "Music")],
                )
            )

            tags = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                **configs
            )

            self.assertFalse(tags["sound_field_scene"]["music_present"])
            self.assertEqual(
                tags["sound_field_scene"]["noise_composition"]["music"], []
            )
            self.assertEqual(
                tags["sound_field_scene"]["noise_composition"]["mechanical"],
                ["Traffic noise"],
            )

    def test_tagging_pipeline_keeps_dass_music_without_aed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=16000, channels=1, duration_sec=1.0)
            configs = missing_external_model_configs(tmpdir)
            configs["dass_config"] = DassNoiseTypeConfig(
                threshold=0.5, subprocess_python=""
            )
            configs["dass_client"] = FakeDassNoiseTypeClient(
                make_dass_output(
                    0.8,
                    "Traffic noise",
                    extra_vector_events=[(0.6, "Music")],
                )
            )

            tags = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                selected_tag_paths=["sound_field_scene.noise_composition"],
                **configs
            )

            self.assertIsNone(tags["sound_field_scene"]["music_present"])
            self.assertEqual(
                tags["sound_field_scene"]["noise_composition"]["music"], ["Music"]
            )
            # One DASS inference publishes both tag paths.
            self.assertEqual(
                tags["sound_field_scene"]["external_noise_type"],
                ["mechanical", "music"],
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
            self.assertEqual(values["audio_quality.snr_db"], 12.0)
            self.assertEqual(values["internal.brouhaha_c50_db"], 3.0)

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
            self.assertIsNone(by_path["audio_quality.snr_db"].value)
            self.assertEqual(by_path["audio_quality.snr_db"].status, "failed")
            self.assertEqual(by_path["internal.brouhaha_c50_db"].value, 5.0)
            self.assertEqual(by_path["internal.brouhaha_c50_db"].status, "estimated")

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
            self.assertIsNone(values["audio_quality.snr_db"])
            self.assertIsNone(values["internal.brouhaha_c50_db"])

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
            self.assertEqual(by_path["audio_quality.dnsmos_sig"].value, 4.125679)
            self.assertEqual(by_path["audio_quality.dnsmos_bak"].value, 3.25)
            self.assertEqual(by_path["audio_quality.dnsmos_ovrl"].value, 3.75)
            self.assertEqual(by_path["audio_quality.dnsmos_p808"].value, 4.0)
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
            self.assertIsNone(by_path["audio_quality.dnsmos_sig"].value)
            self.assertIsNone(by_path["audio_quality.dnsmos_bak"].value)
            self.assertEqual(by_path["audio_quality.dnsmos_ovrl"].value, 3.0)
            self.assertIsNone(by_path["audio_quality.dnsmos_p808"].value)
            self.assertEqual(by_path["audio_quality.dnsmos_p808"].status, "failed")

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

            self.assertEqual(result.tag_path, "room_acoustic.rir")
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

        self.assertEqual(result.tag_path, "room_acoustic.rt60_sec")
        self.assertGreater(result.value, 1.0)
        self.assertLess(result.value, 1.7)

    def test_c50_estimator_derives_value_from_rir(self):
        result = run_c50_estimator(
            {"sample_rate_hz": 1000, "samples": [1.0] * 50 + [0.5] * 50}
        )

        self.assertEqual(result.tag_path, "room_acoustic.c50_db")
        self.assertAlmostEqual(result.value, 6.0206, places=4)

    def test_room_acoustic_auditor_rejects_invalid_rt60_and_c50(self):
        room_acoustic = {
            "far_field": None,
            "rt60_sec": -1.0,
            "c50_db": float("nan"),
        }

        warnings = audit_room_acoustic(room_acoustic)

        self.assertIsNone(room_acoustic["rt60_sec"])
        self.assertIsNone(room_acoustic["c50_db"])
        self.assertEqual(
            warnings,
            [
                {"type": "invalid_room_acoustic_value", "field": "rt60_sec"},
                {"type": "invalid_room_acoustic_value", "field": "c50_db"},
            ],
        )

    def test_sound_field_auditor_rejects_invalid_event_label_lists(self):
        sound_field_scene = {
            "speech_music_events": ["music", "speech"],
            "music_present": True,
            "sound": True,
            "external_noise_type": ["mechanical", "human"],
            "noise_composition": {
                "music": [],
                "animal": [],
                "mechanical": ["Music"],
                "nature": [],
                "formless": [],
                "channel_environment": [],
            },
        }

        warnings = audit_sound_field_scene(sound_field_scene)

        self.assertIsNone(sound_field_scene["speech_music_events"])
        self.assertIsNone(sound_field_scene["sound"])
        self.assertIsNone(sound_field_scene["external_noise_type"])
        self.assertIsNone(sound_field_scene["noise_composition"])
        self.assertEqual(
            [warning["field"] for warning in warnings],
            [
                "speech_music_events",
                "sound",
                "external_noise_type",
                "noise_composition",
            ],
        )

    def test_sound_field_auditor_accepts_valid_noise_composition(self):
        sound_field_scene = {
            "speech_music_events": ["speech"],
            "music_present": False,
            "sound": None,
            "external_noise_type": [],
            "noise_composition": {
                "music": [],
                "animal": ["Dog"],
                "mechanical": ["Traffic noise, roadway noise"],
                "nature": ["Rain"],
                "formless": ["Silence"],
                "channel_environment": ["Reverberation"],
            },
        }

        warnings = audit_sound_field_scene(sound_field_scene)

        self.assertEqual(warnings, [])
        self.assertEqual(
            sound_field_scene["noise_composition"]["mechanical"],
            ["Traffic noise, roadway noise"],
        )

    def test_audio_quality_auditor_rejects_invalid_dnsmos_scores(self):
        audio_quality = {
            "dnsmos_sig": 0.9,
            "dnsmos_bak": 5.1,
            "dnsmos_ovrl": float("nan"),
            "dnsmos_p808": 4.0,
        }

        warnings = audit_audio_quality(audio_quality)

        self.assertIsNone(audio_quality["dnsmos_sig"])
        self.assertIsNone(audio_quality["dnsmos_bak"])
        self.assertIsNone(audio_quality["dnsmos_ovrl"])
        self.assertEqual(audio_quality["dnsmos_p808"], 4.0)
        self.assertEqual(
            [warning["field"] for warning in warnings],
            ["dnsmos_sig", "dnsmos_bak", "dnsmos_ovrl"],
        )

    def test_tagging_pipeline_uses_injected_recrir_client_for_non_model_input_audio(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tone.wav"
            write_test_wav(path, sample_rate=8000, channels=2, duration_sec=1.0)
            rir_samples = [
                math.exp(-float(index) / (16000 * 0.2))
                for index in range(16000)
            ]
            artifact_dir = Path(tmpdir) / "artifacts"

            tags = tag_sample_record(
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
                selected_tag_paths=[
                    "panns",
                    "recrir",
                    "firered_aed",
                ],
            )

            self.assertEqual(tags["basic_acoustic"]["sample_rate_hz"], 8000)
            self.assertEqual(tags["basic_acoustic"]["channels"], 2)
            self.assertNotIn("rir", tags["room_acoustic"])
            self.assertIsNotNone(tags["room_acoustic"]["rt60_sec"])
            self.assertIsNotNone(tags["room_acoustic"]["c50_db"])
            self.assertNotIn("snr_db", tags["basic_acoustic"])
            self.assertEqual(
                tags["sound_field_scene"]["speech_music_events"], ["speech"]
            )
            self.assertFalse(tags["sound_field_scene"]["music_present"])
            self.assertEqual(tags["sound_field_scene"]["sound"], ["Noise"])

            artifacts = list((artifact_dir / "rir").glob("*.rir.json.gz"))
            self.assertEqual(len(artifacts), 1)
            with gzip.open(str(artifacts[0]), "rt", encoding="utf-8") as source:
                artifact = json.load(source)
            self.assertEqual(artifact["sample_rate_hz"], 16000)
            self.assertEqual(len(artifact["samples"]), len(rir_samples))

    def test_tagging_pipeline_isolates_music_and_sound_failures(self):
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

            panns_failure = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                selected_tag_paths=["panns", "firered_aed"],
                firered_aed_client=FakeFireRedAedClient(fire_output),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.9, "/m/09x0r", "Speech")
                ),
                **common
            )
            fire_failure = tag_sample_record(
                make_record(str(path)),
                tmpdir,
                selected_tag_paths=["panns", "firered_aed"],
                firered_aed_client=FakeFireRedAedClient({}),
                panns_client=FakePannsBackgroundClient(
                    make_panns_output(0.8, "/m/096m7z", "Noise")
                ),
                **common
            )

            self.assertTrue(panns_failure["sound_field_scene"]["music_present"])
            self.assertEqual(
                panns_failure["sound_field_scene"]["speech_music_events"],
                ["music"],
            )
            self.assertIsNone(panns_failure["sound_field_scene"]["sound"])
            self.assertIsNone(fire_failure["sound_field_scene"]["music_present"])
            self.assertIsNone(fire_failure["sound_field_scene"]["speech_music_events"])
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
        self.assertEqual(public_values["speaker.speaker_count"], 2)
        self.assertTrue(public_values["speaker.multi_speaker"])
        self.assertEqual(public_values["speaker.speaker_change_count"], 1)
        self.assertTrue(public_values["speaker.speaker_change"])
        self.assertEqual(public_values["speaker.overlap_ratio"], 0.75)
        self.assertTrue(public_values["speaker.speaker_overlap"])
        self.assertEqual(
            set(public_values),
            {
                "speaker.speaker_count",
                "speaker.multi_speaker",
                "speaker.speaker_change_count",
                "speaker.speaker_change",
                "speaker.overlap_ratio",
                "speaker.speaker_overlap",
            },
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
        self.assertEqual(public_values["speaker.overlap_ratio"], 0.166667)
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
            timeout_sec=900,
        )

    def test_speaker_v2_cli_profile_options(self):
        args = build_arg_parser().parse_args([])
        self.assertEqual(args.speaker_profile, "quality-shadow")
        self.assertFalse(args.speaker_v2_skip_model_verification)

        args = build_arg_parser().parse_args(
            [
                "--speaker-profile",
                "lean-shadow",
                "--speaker-v2-skip-model-verification",
                "--topic-enable",
                "--topic-model",
                "gpt-5.5",
                "--topic-api-key-path",
                "api.txt",
                "--sample-id",
                "utt1",
                "--input-tags",
                "old.jsonl",
                "--only-tags",
                "speaker,language_content.topic",
                "--missing-only",
            ]
        )
        self.assertEqual(args.speaker_profile, "lean-shadow")
        self.assertTrue(args.speaker_v2_skip_model_verification)
        self.assertTrue(args.topic_enable)
        self.assertEqual(args.topic_model, "gpt-5.5")
        self.assertEqual(args.topic_api_key_path, "api.txt")
        self.assertEqual(args.sample_id, ["utt1"])
        self.assertEqual(args.input_tags, "old.jsonl")
        self.assertEqual(args.only_tags, "speaker,language_content.topic")
        self.assertTrue(args.missing_only)

    def test_tagging_manifest_reuses_context_and_isolates_speaker_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audio.wav"
            write_test_wav(path, sample_rate=8000, channels=1, duration_sec=2.0)
            manifest_path = Path(tmpdir) / "manifest.jsonl"
            output_path = Path(tmpdir) / "tags.jsonl"
            records = [make_record(str(path)), make_record(str(path))]
            with manifest_path.open("w", encoding="utf-8") as sink:
                for record in records:
                    sink.write(json.dumps(record, ensure_ascii=False) + "\n")

            public_speaker = {
                "speaker_count": 1,
                "multi_speaker": False,
                "speaker_change_count": 0,
                "speaker_change": False,
                "overlap_ratio": 0.0,
                "speaker_overlap": False,
            }
            result = {
                "speaker": public_speaker,
                "run_profile": "quality-shadow",
                "policy_version": "policy-v1",
                "policy_hash": "hash",
                "fusion_artifact": "fusion.json.gz",
                "artifacts": {},
            }
            with mock.patch(
                "tagger.pipelines.tagging.run_speaker_v2_record",
                return_value=result,
            ) as run_speaker:
                summary = run_tagging_manifest(
                    manifest_path,
                    output_path,
                    speaker_config=object(),
                    selected_tag_paths=["speaker"],
                )

            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(run_speaker.call_count, 2)
            first = run_speaker.call_args_list[0].kwargs
            second = run_speaker.call_args_list[1].kwargs
            self.assertIs(first["context"], second["context"])
            self.assertNotEqual(
                first["artifact_sample_id"],
                second["artifact_sample_id"],
            )
            self.assertEqual(
                first["artifact_root"],
                Path(tmpdir) / "artifacts",
            )
            with output_path.open("r", encoding="utf-8") as source_file:
                rows = [json.loads(line) for line in source_file if line.strip()]
            self.assertEqual([row["speaker"] for row in rows], [public_speaker] * 2)

    def test_tagging_manifest_supplements_selected_sample_tags_from_existing_output(self):
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

            summary = run_tagging_manifest(
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

    def test_tagging_pipeline_nulls_speaker_fields_when_v2_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audio.wav"
            write_test_wav(path, sample_rate=8000, channels=1, duration_sec=2.0)
            manifest_path = Path(tmpdir) / "manifest.jsonl"
            output_path = Path(tmpdir) / "tags.jsonl"
            with manifest_path.open("w", encoding="utf-8") as sink:
                sink.write(json.dumps(make_record(str(path)), ensure_ascii=False) + "\n")

            with mock.patch(
                "tagger.pipelines.tagging.run_speaker_v2_record",
                side_effect=RuntimeError("speaker failed"),
            ):
                summary = run_tagging_manifest(
                    manifest_path,
                    output_path,
                    speaker_config=object(),
                    selected_tag_paths=["speaker"],
                )

            self.assertEqual(summary["internal_warning_count"], 1)
            with output_path.open("r", encoding="utf-8") as source_file:
                tags = json.loads(source_file.readline())
            self.assertTrue(all(value is None for value in tags["speaker"].values()))

    def test_speaker_auditor_rejects_invalid_public_values(self):
        speaker = {
            "multi_speaker": "yes",
            "speaker_change": "yes",
            "speaker_overlap": 1,
            "speaker_count": -1,
            "speaker_change_count": 1.5,
            "overlap_ratio": 1.1,
        }

        warnings = audit_speaker(speaker)

        self.assertEqual(
            warnings,
            [
                {"type": "invalid_speaker_value", "field": "multi_speaker"},
                {"type": "invalid_speaker_value", "field": "speaker_change"},
                {"type": "invalid_speaker_value", "field": "speaker_overlap"},
                {"type": "invalid_speaker_value", "field": "speaker_count"},
                {"type": "invalid_speaker_value", "field": "speaker_change_count"},
                {"type": "invalid_speaker_value", "field": "overlap_ratio"},
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


class FakeDassNoiseTypeClient:
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
        self.call_count = 0

    def estimate(self, audio_path, context=None):
        self.call_count += 1
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
        self.call_count = 0

    def estimate_rir(self, audio_path, context=None):
        self.call_count += 1
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


def make_dass_output(score, display_name, extra_events=None, extra_vector_events=None):
    """Build a full fake DASS estimate.

    ``extra_events`` are ``(score, display_name)`` pairs appended to the
    public top-noise list (scores must not exceed the winning score).
    ``extra_vector_events`` are injected only into the full 527-class vector,
    which is where the composition layer reads from.
    """
    labels = [
        {"index": index, "display_name": "class_%03d" % index}
        for index in range(527)
    ]
    scores = [0.0] * 527
    events = [(score, display_name)] + list(extra_events or [])
    top_noise_events = []
    for event_index, (event_score, event_name) in enumerate(events, start=1):
        labels[event_index] = {"index": event_index, "display_name": event_name}
        scores[event_index] = event_score
        top_noise_events.append(
            {"index": event_index, "display_name": event_name, "score": event_score}
        )
    for event_index, (event_score, event_name) in enumerate(
        extra_vector_events or [], start=100
    ):
        labels[event_index] = {"index": event_index, "display_name": event_name}
        scores[event_index] = event_score
    return {
        "chunk_count": 1,
        "max_noise_score": score,
        "winning_event": dict(top_noise_events[0]),
        "top_noise_events": top_noise_events,
        "labels": labels,
        "scores": scores,
    }


def missing_external_model_configs(tmpdir):
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
        "dass_config": DassNoiseTypeConfig(
            model_dir=str(root / "missing_dass"),
            subprocess_python="",
        ),
    }


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
