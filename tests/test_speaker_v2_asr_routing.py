"""Tests for the dual MOSS/FireRed speaker-v2 ASR selection policy."""

import unittest

from tagger.pipelines.speaker_evidence import (
    _classify_asr_language,
    _select_speaker_asr,
)


def _candidate(source, text, status="estimated", language=None, usable=True):
    payload = {"asr_transcript": text}
    if source == "fireredasr2_aed":
        payload["text"] = text
        if language is not None:
            payload["language"] = language
    return {
        "source": {"name": source},
        "status": status,
        "quality": {"usable": usable},
        "payload": payload,
    }


class SpeakerV2AsrRoutingTest(unittest.TestCase):
    def test_pure_english_selects_moss_and_keeps_firered_candidate(self):
        result = _select_speaker_asr(
            [
                _candidate("moss_transcribe_diarize", "MOSS English"),
                _candidate("fireredasr2_aed", "FireRed English", language="en"),
            ]
        )

        self.assertEqual(result["text"], "MOSS English")
        self.assertEqual(result["route"]["selected_source"], "moss_transcribe_diarize")
        self.assertEqual(result["route"]["selected_model"], "moss")
        self.assertEqual(result["route"]["language_route"], "pure_english")
        self.assertIn("moss", result["candidates"])
        self.assertIn("firered", result["candidates"])

    def test_non_english_and_mixed_text_selects_firered(self):
        for text in ("这是中文结果", "hello 世界", "Привет мир"):
            with self.subTest(text=text):
                result = _select_speaker_asr(
                    [
                        _candidate("moss_transcribe_diarize", "MOSS text"),
                        _candidate("fireredasr2_aed", text),
                    ]
                )

                self.assertEqual(result["text"], text)
                self.assertEqual(result["route"]["selected_model"], "firered")
                self.assertEqual(
                    result["route"]["language_route"], "non_english_or_mixed"
                )
                self.assertFalse(result["route"]["fallback"])

    def test_non_english_language_metadata_overrides_ascii_script(self):
        route, reason, source = _classify_asr_language(
            "bonjour tout le monde", language="fr"
        )

        self.assertEqual(route, "non_english_or_mixed")
        self.assertIn("metadata", reason)
        self.assertEqual(source, "firered_lid")

    def test_ascii_without_lid_metadata_stays_unknown_and_uses_firered(self):
        result = _select_speaker_asr(
            [
                _candidate("moss_transcribe_diarize", "MOSS English"),
                _candidate("fireredasr2_aed", "bonjour tout le monde"),
            ]
        )

        self.assertEqual(result["text"], "bonjour tout le monde")
        self.assertEqual(result["route"]["selected_model"], "firered")
        self.assertEqual(result["route"]["language_route"], "unknown")
        self.assertEqual(
            result["route"]["language_source"], "firered_lid_unavailable"
        )
        self.assertFalse(result["route"]["fallback"])

    def test_lid_error_is_visible_in_candidate_and_route(self):
        firered = _candidate(
            "fireredasr2_aed", "hello world", language=None
        )
        firered["payload"]["language_error"] = "FireRed LID unavailable"
        result = _select_speaker_asr(
            [_candidate("moss_transcribe_diarize", "MOSS text"), firered]
        )

        self.assertEqual(result["route"]["language_route"], "unknown")
        self.assertEqual(
            result["route"]["language_error"], "FireRed LID unavailable"
        )
        self.assertEqual(
            result["candidates"]["firered"]["language_error"],
            "FireRed LID unavailable",
        )
        self.assertEqual(result["route"]["selected_model"], "firered")

    def test_moss_fallback_is_recorded_when_firered_unavailable(self):
        result = _select_speaker_asr(
            [
                _candidate("moss_transcribe_diarize", "English fallback"),
                _candidate(
                    "fireredasr2_aed",
                    "",
                    status="error",
                    usable=False,
                ),
            ]
        )

        self.assertEqual(result["text"], "English fallback")
        self.assertEqual(result["route"]["selected_model"], "moss")
        self.assertEqual(result["route"]["language_route"], "unknown")
        self.assertTrue(result["route"]["fallback"])
        self.assertIn("unavailable", result["route"]["reason"])

    def test_firered_fallback_is_recorded_when_moss_unavailable_for_english(self):
        result = _select_speaker_asr(
            [
                _candidate(
                    "moss_transcribe_diarize",
                    "",
                    status="error",
                    usable=False,
                ),
                _candidate("fireredasr2_aed", "hello world", language="en"),
            ]
        )

        self.assertEqual(result["text"], "hello world")
        self.assertEqual(result["route"]["selected_model"], "firered")
        self.assertEqual(result["route"]["language_route"], "pure_english")
        self.assertTrue(result["route"]["fallback"])
        self.assertIn("fallback", result["route"]["reason"])

    def test_both_missing_returns_empty_text_and_availability_reason(self):
        result = _select_speaker_asr(
            [
                _candidate(
                    "moss_transcribe_diarize", "", status="error", usable=False
                ),
                _candidate(
                    "fireredasr2_aed", "", status="error", usable=False
                ),
            ]
        )

        self.assertEqual(result["text"], "")
        self.assertIsNone(result["route"]["selected_source"])
        self.assertIsNone(result["route"]["selected_model"])
        self.assertEqual(result["route"]["language_route"], "unknown")
        self.assertFalse(result["route"]["fallback"])
        self.assertIn("both ASR candidates unavailable", result["route"]["reason"])

    def test_punctuation_only_and_empty_transcripts_are_unknown(self):
        for text in ("", "...?! 123", "---"):
            with self.subTest(text=text):
                route, reason, source = _classify_asr_language(text)
                self.assertEqual(route, "unknown")
                self.assertIn("no alphabetic", reason)
                self.assertEqual(source, "fallback")


if __name__ == "__main__":
    unittest.main()
