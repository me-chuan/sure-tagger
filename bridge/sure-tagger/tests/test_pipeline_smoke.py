import os
import unittest

from sure_tagger.cli import build_parser, pipeline_tag_names
from sure_tagger.datasets.ami import parse_words_file, resolve_href
from sure_tagger.meeting_manifest import aggregate_meeting_records
from sure_tagger.schemas import validate_manifest_record
from sure_tagger.tags.topic import (
    load_taxonomy,
    merge_chunk_payloads,
    resolve_topic_schema_path,
    split_text_for_llm,
    validate_topic_payload,
)
from sure_tagger.text.normalize import join_tokens
from sure_tagger.text.tokenizer import punctuation_counts, word_tokens


ROOT = "/hpc_stor03/sjtu_home/huifei.wang/sure-tagger"


class PipelineSmokeTest(unittest.TestCase):
    def test_join_tokens(self):
        text = join_tokens(["Hi", ",", "I", "'m", "David", "."])
        self.assertIn("Hi,", text)
        self.assertTrue(text.endswith("."))

    def test_word_and_punctuation_counts(self):
        text = "Hi, I'm David."
        self.assertEqual(len(word_tokens(text)), 3)
        counts = punctuation_counts(text)
        self.assertEqual(counts["comma"], 1)
        self.assertTrue(counts["has_terminal_punctuation"])

    def test_ami_href_resolution(self):
        words_path = os.path.join(ROOT, "AMI/amicorpus/annotations/words/ES2002a.A.words.xml")
        words = parse_words_file(words_path)
        items = resolve_href("ES2002a.A.words.xml#id(ES2002a.A.words0)..id(ES2002a.A.words12)", words)
        self.assertEqual(items[0]["text"], "Hi")
        self.assertEqual(items[-1]["text"], ".")

    def test_manifest_record_shape(self):
        record = {
            "corpus": {"dataset_name": "X"},
            "sample": {
                "sample_id": "X:1",
                "audio": {"path": "a.wav", "start_sec": 0.0, "end_sec": 1.0},
                "text": {"transcript": "hello"},
                "native_metadata": {},
                "provenance": {"source_path": "x", "source_split": ""},
            },
        }
        self.assertTrue(validate_manifest_record(record))

    def test_topic_taxonomy_validation(self):
        taxonomy = load_taxonomy(os.path.join(ROOT, "configs/topic_taxonomy_general.yaml"))
        payload = {
            "major_topic": "academic_research",
            "minor_topic": "computer_science",
            "confidence": 0.9,
            "topic_keywords": ["ASR"],
            "proper_nouns": ["AMI"],
            "reason_short": "test",
        }
        clean = validate_topic_payload(payload, taxonomy)
        self.assertEqual(clean["major_topic"], "academic_research")

    def test_meeting_manifest_aggregation(self):
        records = [
            {
                "corpus": {"dataset_name": "AMI", "native_metadata": {}},
                "sample": {
                    "sample_id": "AMI:M1:A:s2",
                    "audio": {"path": "m1.wav", "start_sec": 10.0, "end_sec": 12.0},
                    "text": {"transcript": "second turn"},
                    "native_metadata": {"meeting_id": "M1", "speaker_id": "A", "meeting_type": "scenario"},
                    "provenance": {"source_path": "segments.xml", "source_split": ""},
                },
            },
            {
                "corpus": {"dataset_name": "AMI", "native_metadata": {}},
                "sample": {
                    "sample_id": "AMI:M1:B:s1",
                    "audio": {"path": "m1.wav", "start_sec": 1.0, "end_sec": 2.0},
                    "text": {"transcript": "first turn"},
                    "native_metadata": {"meeting_id": "M1", "speaker_id": "B", "meeting_type": "scenario"},
                    "provenance": {"source_path": "segments.xml", "source_split": ""},
                },
            },
        ]
        meetings = aggregate_meeting_records(records, source_manifest_path="manifest.jsonl")
        self.assertEqual(len(meetings), 1)
        meeting = meetings[0]
        self.assertTrue(validate_manifest_record(meeting))
        self.assertEqual(meeting["sample"]["sample_id"], "AMI:M1")
        self.assertEqual(meeting["sample"]["native_metadata"]["granularity"], "meeting")
        self.assertEqual(meeting["sample"]["native_metadata"]["source_sample_count"], 2)
        self.assertTrue(meeting["sample"]["text"]["speaker_labeled_transcript"].splitlines()[0].endswith("B: first turn"))

    def test_topic_chunk_split_and_merge(self):
        chunks = split_text_for_llm("A: alpha\nB: beta\nC: gamma", 12)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 12 for chunk in chunks))
        taxonomy = load_taxonomy(os.path.join(ROOT, "configs/topic_taxonomy_general.yaml"))
        merged = merge_chunk_payloads([
            {
                "major_topic": "technology_engineering",
                "minor_topic": "product_design",
                "confidence": 0.8,
                "topic_keywords": ["remote", "design"],
                "proper_nouns": ["AMI"],
                "reason_short": "test",
            },
            {
                "major_topic": "business_management",
                "minor_topic": "project_management",
                "confidence": 0.5,
                "topic_keywords": ["schedule"],
                "proper_nouns": [],
                "reason_short": "test",
            },
        ], taxonomy, [100, 20])
        self.assertEqual(merged["major_topic"], "technology_engineering")
        self.assertEqual(merged["minor_topic"], "product_design")

    def test_topic_schema_can_be_disabled_for_compatible_gateways(self):
        self.assertIsNone(resolve_topic_schema_path({"use_json_schema": False}))
        self.assertIsNone(resolve_topic_schema_path({"model": {"use_json_schema": "false"}}))
        self.assertEqual(
            resolve_topic_schema_path({"schema_path": "custom_schema.json"}),
            "custom_schema.json",
        )

    def test_run_meeting_pipeline_tag_defaults(self):
        parser = build_parser()
        args = parser.parse_args([
            "run-meeting-pipeline",
            "--dataset", "ami",
            "--root", os.path.join(ROOT, "AMI"),
        ])
        self.assertEqual(pipeline_tag_names(args), ["language", "word_count", "punctuation", "filler", "repetition"])
        args = parser.parse_args([
            "run-meeting-pipeline",
            "--dataset", "ami",
            "--root", os.path.join(ROOT, "AMI"),
            "--include-topic",
        ])
        self.assertIn("topic", pipeline_tag_names(args))


if __name__ == "__main__":
    unittest.main()
