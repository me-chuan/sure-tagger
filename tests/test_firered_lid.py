"""Tests for the FireRed LID language-content tool."""

import unittest

from tagger.tools.language_content.firered_lid_detector import (
    FireRedLidConfig,
    FireRedLidError,
    validate_lid_output,
)


class FireRedLidToolTest(unittest.TestCase):
    def test_validate_accepts_upstream_output(self):
        summary = validate_lid_output(
            {
                "uttid": "sample",
                "lang": "en",
                "confidence": 0.996,
                "dur_s": 18.436,
                "rtf": "0.0860",  # upstream formats rtf as a display string
                "wav": "audio.wav",
            }
        )
        self.assertEqual(summary["lang"], "en")
        self.assertEqual(summary["confidence"], 0.996)
        self.assertEqual(summary["rtf"], 0.086)

    def test_validate_accepts_region_code(self):
        summary = validate_lid_output({"lang": "zh-xinan", "confidence": 0.9})
        self.assertEqual(summary["lang"], "zh-xinan")

    def test_validate_rejects_empty_lang(self):
        with self.assertRaises(FireRedLidError):
            validate_lid_output({"lang": "", "confidence": 0.9})

    def test_validate_rejects_out_of_range_confidence(self):
        with self.assertRaises(FireRedLidError):
            validate_lid_output({"lang": "en", "confidence": 1.5})

    def test_validate_rejects_non_numeric_dur(self):
        with self.assertRaises(FireRedLidError):
            validate_lid_output({"lang": "en", "confidence": 0.9, "dur_s": "long"})


if __name__ == "__main__":
    unittest.main()
