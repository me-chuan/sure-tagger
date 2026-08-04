import json


TOPIC_PROMPT_VERSION = "topic_hierarchical_v0.3.0"


def build_topic_prompt(taxonomy, transcript_text, context, dataset_metadata=None):
    payload = {
        "task": "Classify an ASR transcript unit into one major_topic and one minor_topic.",
        "rules": [
            "Return strict JSON only.",
            "Use exactly one major_topic and one minor_topic from the taxonomy.",
            "minor_topic must belong to the chosen major_topic.",
            "Extract topic_keywords and proper_nouns only from the transcript/context.",
            "If evidence is insufficient, use other/insufficient_context.",
            "Do not invent proper nouns.",
            "For meeting-level input, choose the dominant topic of the whole meeting, not the meeting-management process unless that is the real content.",
            "For chunk input, classify only the provided chunk; a later deterministic merge will choose the meeting-level result.",
        ],
        "output_schema_summary": {
            "major_topic": "string",
            "minor_topic": "string",
            "confidence": "number in [0, 1]",
            "topic_keywords": "array of strings",
            "proper_nouns": "array of strings",
            "reason_short": "short explanation",
        },
        "taxonomy": taxonomy,
        "dataset_metadata": dataset_metadata or {},
        "transcript_text": transcript_text or "",
        "context": context or {},
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
