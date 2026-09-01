"""Integration checks for the speaker-v2 dual-ASR execution boundary."""

import gzip
import json
from pathlib import Path
import struct
import tempfile
import threading
import unittest
from unittest import mock
import wave

from tagger.pipelines.speaker_evidence import SpeakerEvidenceConfig, run_record
from tagger.tools.speaker_v2.contracts import build_evidence
from tagger.tools.speaker_v2.timeline import summarize_timeline


def _write_wav(path, duration_sec=1.0):
    sample_rate = 16000
    frame_count = int(round(sample_rate * duration_sec))
    with wave.open(str(path), "wb") as sink:
        sink.setnchannels(1)
        sink.setsampwidth(2)
        sink.setframerate(sample_rate)
        sink.writeframes(struct.pack("<%sh" % frame_count, *([0] * frame_count)))


def _record(audio_path):
    return {
        "corpus": {
            "dataset_name": "speaker-v2-test",
            "source_urls": {
                "article": [],
                "github": [],
                "huggingface": [],
                "dataset_card": [],
            },
            "native_metadata": {},
        },
        "sample": {
            "sample_id": "dual-asr-parallel",
            "audio": {"path": str(audio_path)},
            "text": {"transcript": "native text is not an inference input"},
            "native_metadata": {},
        },
    }


def _fake_asr_evidence(source, scope):
    if source == "moss":
        return build_evidence(
            scope["sample_id"],
            scope["duration_sec"],
            "joint_speaker_timeline_and_text",
            "moss_transcribe_diarize",
            "test-moss",
            "joint_asr_diarizer",
            ["speaker_timeline", "joint_speaker_text"],
            ["G_test_moss"],
            {
                "timeline_summary": summarize_timeline(
                    [
                        {
                            "start_sec": 0.0,
                            "end_sec": scope["duration_sec"],
                            "speaker_id": "S01",
                            "text": "moss candidate",
                        }
                    ],
                    scope["duration_sec"],
                ),
                "asr_transcript": "moss candidate",
            },
            quality={"usable": True},
            applicability={"audio_sha256": scope["audio_sha256"]},
        )
    return build_evidence(
        scope["sample_id"],
        scope["duration_sec"],
        "asr_transcript",
        "fireredasr2_aed",
        "test-firered",
        "asr",
        ["asr_transcript", "lexical_timeline"],
        ["G_test_firered"],
        {
            "text": "中文候选",
            "asr_transcript": "中文候选",
            "language": "zh",
            "language_confidence": 0.99,
            "lexical_units": [],
        },
        quality={"usable": True},
        applicability={"audio_sha256": scope["audio_sha256"]},
    )


class SpeakerV2AsrConcurrencyTest(unittest.TestCase):
    def test_moss_and_firered_are_in_flight_before_results_are_joined(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            audio_path = root / "sample.wav"
            _write_wav(audio_path)
            output_dir = root / "output"
            config = SpeakerEvidenceConfig(
                moss_config=object(),
                firered_asr_config=object(),
                enable_moss=True,
                enable_firered_asr=True,
                enable_vad=False,
                enable_campplus=False,
                enable_whisper=False,
                enable_sortformer=False,
                enable_pyannote=False,
                enable_ecapa=False,
                enable_brouhaha=False,
                enable_speaker_profile=False,
                verify_model_assets=False,
            )
            barrier = threading.Barrier(2)
            entered = set()

            def collect(source, scope, _config, _context, _verify):
                entered.add(source)
                barrier.wait(timeout=2.0)
                return _fake_asr_evidence(source, scope)

            with mock.patch(
                "tagger.pipelines.speaker_evidence._collect_asr_evidence",
                side_effect=collect,
            ):
                result = run_record(
                    _record(audio_path),
                    root,
                    output_dir,
                    config,
                    context={},
                )

            self.assertEqual(entered, {"moss", "firered_asr"})
            self.assertEqual(result["asr_selected_source"], "fireredasr2_aed")
            with gzip.open(result["fusion_artifact"], "rt", encoding="utf-8") as source:
                fusion = json.load(source)
            self.assertEqual(
                fusion["asr_route"]["language_route"], "non_english_or_mixed"
            )
            self.assertEqual(
                set(fusion["asr_candidates"]), {"moss", "firered"}
            )
            self.assertEqual(
                fusion["asr_candidates"]["moss"]["text"], "moss candidate"
            )
            self.assertEqual(
                fusion["asr_candidates"]["firered"]["text"], "中文候选"
            )


if __name__ == "__main__":
    unittest.main()
