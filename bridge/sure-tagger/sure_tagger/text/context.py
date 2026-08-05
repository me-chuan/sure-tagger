def sample_sort_key(record):
    sample = record.get("sample", {})
    meta = sample.get("native_metadata", {})
    audio = sample.get("audio", {})
    start = audio.get("start_sec")
    if start is None:
        start = -1
    meeting_id = meta.get("meeting_id") or meta.get("audio_id") or ""
    return (meeting_id, float(start), meta.get("speaker_id", ""), sample.get("sample_id", ""))


class ContextBuilder(object):
    def __init__(self, records):
        self.records = sorted(records, key=sample_sort_key)
        self.by_meeting = {}
        for rec in self.records:
            meta = rec["sample"]["native_metadata"]
            meeting_id = meta.get("meeting_id") or meta.get("audio_id") or ""
            self.by_meeting.setdefault(meeting_id, []).append(rec)

    def build(self, record, meeting_window_sec=120, speaker_neighbor_segments=3, max_context_chars=6000):
        sample = record["sample"]
        meta = sample["native_metadata"]
        meeting_id = meta.get("meeting_id") or meta.get("audio_id") or ""
        speaker_id = meta.get("speaker_id", "")
        start = sample.get("audio", {}).get("start_sec")
        end = sample.get("audio", {}).get("end_sec")
        current_text = sample.get("text", {}).get("transcript", "")
        meeting_records = self.by_meeting.get(meeting_id, [])
        granularity = meta.get("granularity", "sample")

        meeting_window = []
        speaker_window = []
        if start is not None and end is not None:
            lo = float(start) - float(meeting_window_sec)
            hi = float(end) + float(meeting_window_sec)
            for rec in meeting_records:
                audio = rec["sample"].get("audio", {})
                rec_start = audio.get("start_sec")
                rec_end = audio.get("end_sec")
                if rec_start is None or rec_end is None:
                    continue
                if float(rec_end) >= lo and float(rec_start) <= hi:
                    meeting_window.append(rec)

        same_speaker = [r for r in meeting_records if r["sample"]["native_metadata"].get("speaker_id") == speaker_id]
        ids = [r["sample"]["sample_id"] for r in same_speaker]
        try:
            idx = ids.index(sample["sample_id"])
            lo_i = max(0, idx - int(speaker_neighbor_segments))
            hi_i = min(len(same_speaker), idx + int(speaker_neighbor_segments) + 1)
            speaker_window = same_speaker[lo_i:hi_i]
        except ValueError:
            speaker_window = [record]

        meeting_text = self._records_to_text(meeting_window, max_context_chars)
        speaker_text = self._records_to_text(speaker_window, max_context_chars // 2)
        evidence_scope = "meeting_window" if meeting_window else "sample"
        if granularity == "utterance":
            evidence_scope = "utterance_context" if meeting_window else "utterance"

        return {
            "sample_text": current_text,
            "utterance_text": current_text,
            "utterance_start_sec": start,
            "utterance_end_sec": end,
            "speaker_id": speaker_id,
            "meeting_id": meeting_id,
            "target_granularity": granularity,
            "meeting_window_text": meeting_text,
            "speaker_window_text": speaker_text,
            "neighbor_window_text": meeting_text,
            "same_speaker_window_text": speaker_text,
            "evidence_scope": evidence_scope,
            "evidence_sample_count": len(meeting_window) if meeting_window else 1,
        }

    def _records_to_text(self, records, max_chars):
        parts = []
        total = 0
        for rec in records:
            sample = rec["sample"]
            meta = sample["native_metadata"]
            text = sample.get("text", {}).get("transcript", "")
            if not text:
                continue
            prefix = "%s: " % meta.get("speaker_id", "?")
            piece = prefix + text
            if total + len(piece) > max_chars:
                break
            parts.append(piece)
            total += len(piece)
        return "\n".join(parts)
