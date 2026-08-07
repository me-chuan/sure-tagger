"""Registry for language-content tag tools."""

from tagger.tools.language_content import deterministic
from tagger.tools.language_content import topic


DETERMINISTIC_LANGUAGE_CONTENT_TOOL = {
    "tool_name": "deterministic_language_content",
    "tag_paths": [
        "language_content.language",
        "language_content.word_count",
        "language_content.punctuation",
        "language_content.repetition",
        "language_content.filler",
    ],
    "run": deterministic.run_all,
}

TOPIC_LANGUAGE_CONTENT_TOOL = {
    "tool_name": topic.TOOL_NAME,
    "tag_path": "language_content.topic",
    "run": topic.run,
}
