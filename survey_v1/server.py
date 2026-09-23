#!/usr/bin/env python3
"""Local listening survey for the combined 30-sample preview."""

from __future__ import annotations

import argparse
import json
import random
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT.parent / "auk_saasr_preview_v3"
STATIC_ROOT = ROOT / "static"
DB_PATH = ROOT / "survey.sqlite3"
EXCLUDED_POSITIONS = {4, 11, 25, 27}
LOCK = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_samples() -> list[dict]:
    sure = {row["sample_id"]: row for row in read_jsonl(DATA_ROOT / "sure_tagger" / "index.jsonl")}
    captioner = {row["sample_id"]: row for row in read_jsonl(DATA_ROOT / "captioner" / "index.jsonl")}
    selected = []
    for position in range(1, 31):
        if position in EXCLUDED_POSITIONS:
            continue
        sure_rows = [row for row in sure.values() if row["combined_position"] == position]
        captioner_rows = [row for row in captioner.values() if row["combined_position"] == position]
        if len(sure_rows) != 1 or len(captioner_rows) != 1:
            raise RuntimeError(f"missing paired row at position {position}")
        s, c = sure_rows[0], captioner_rows[0]
        if s["sample_id"] != c["sample_id"]:
            raise RuntimeError(f"paired sample mismatch at position {position}")
        selected.append({
            "position": position,
            "sample_id": s["sample_id"],
            "reference": f"/media/{s['combined_real_reference']}",
            "sure": f"/media/{s['combined_audio']}",
            "captioner": f"/media/{c['combined_audio']}",
        })
    return selected


SAMPLES = load_samples()
SAMPLE_BY_ID = {sample["sample_id"]: sample for sample in SAMPLES}


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            assignment_json TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sample_id TEXT NOT NULL,
            selected_label TEXT NOT NULL,
            selected_method TEXT,
            submitted_at TEXT NOT NULL,
            UNIQUE(session_id, sample_id),
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        )
    """)
    conn.commit()
    return conn


def make_session() -> dict:
    question_order = list(SAMPLES)
    random.SystemRandom().shuffle(question_order)
    assignment = []
    for question_number, sample in enumerate(question_order, 1):
        candidates = [("sure_tagger", sample["sure"]), ("captioner", sample["captioner"])]
        random.SystemRandom().shuffle(candidates)
        assignment.append({
            "question_number": question_number,
            "sample_id": sample["sample_id"],
            "position": sample["position"],
            "reference": sample["reference"],
            "options": {
                "A": {"audio": candidates[0][1], "method": candidates[0][0]},
                "B": {"audio": candidates[1][1], "method": candidates[1][0]},
            },
        })
    session_id = uuid.uuid4().hex
    with LOCK:
        conn = connect()
        conn.execute(
            "INSERT INTO sessions(session_id, created_at, assignment_json) VALUES (?, ?, ?)",
            (session_id, utc_now(), json.dumps(assignment, ensure_ascii=False)),
        )
        conn.commit()
        conn.close()
    public_questions = []
    for item in assignment:
        public_questions.append({
            "question_number": item["question_number"],
            "reference": item["reference"],
            "options": {label: {"audio": option["audio"]} for label, option in item["options"].items()},
        })
    return {"session_id": session_id, "questions": public_questions}


def submit_session(payload: dict) -> dict:
    session_id = str(payload.get("session_id") or "")
    answers = payload.get("answers")
    if not session_id or not isinstance(answers, list):
        raise ValueError("session_id and answers are required")
    with LOCK:
        conn = connect()
        row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if row is None:
            conn.close()
            raise ValueError("unknown session")
        if row["completed_at"]:
            conn.close()
            raise ValueError("session already submitted")
        assignment = json.loads(row["assignment_json"])
        by_question = {item["question_number"]: item for item in assignment}
        if len(answers) != len(assignment):
            conn.close()
            raise ValueError("all questions must be answered")
        seen = set()
        records = []
        for answer in answers:
            number = int(answer.get("question_number", 0))
            label = str(answer.get("selected", ""))
            item = by_question.get(number)
            if item is None or number in seen or label not in {"A", "B", "unsure"}:
                conn.close()
                raise ValueError("invalid answer set")
            seen.add(number)
            method = item["options"].get(label, {}).get("method") if label in {"A", "B"} else None
            records.append((session_id, item["sample_id"], label, method, utc_now()))
        conn.executemany(
            "INSERT INTO responses(session_id, sample_id, selected_label, selected_method, submitted_at) VALUES (?, ?, ?, ?, ?)",
            records,
        )
        conn.execute("UPDATE sessions SET completed_at = ? WHERE session_id = ?", (utc_now(), session_id))
        conn.commit()
        conn.close()
    return {"ok": True, "answered": len(records)}


def submit_answer(payload: dict) -> dict:
    session_id = str(payload.get("session_id") or "")
    selected = str(payload.get("selected") or "")
    try:
        question_number = int(payload.get("question_number", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid question number") from exc
    if not session_id or selected not in {"A", "B", "unsure"}:
        raise ValueError("session_id, question_number and selected are required")

    with LOCK:
        conn = connect()
        try:
            session = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if session is None:
                raise ValueError("unknown session")
            assignment = json.loads(session["assignment_json"])
            item = next(
                (row for row in assignment if row["question_number"] == question_number),
                None,
            )
            if item is None:
                raise ValueError("invalid question number")

            method = item["options"].get(selected, {}).get("method") if selected in {"A", "B"} else None
            existing = conn.execute(
                "SELECT selected_label FROM responses WHERE session_id = ? AND sample_id = ?",
                (session_id, item["sample_id"]),
            ).fetchone()
            if session["completed_at"]:
                if existing is not None and existing["selected_label"] == selected:
                    return {
                        "ok": True,
                        "answered": len(assignment),
                        "total": len(assignment),
                        "complete": True,
                    }
                raise ValueError("session already completed")

            conn.execute(
                """
                INSERT INTO responses(
                    session_id, sample_id, selected_label, selected_method, submitted_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id, sample_id) DO UPDATE SET
                    selected_label = excluded.selected_label,
                    selected_method = excluded.selected_method,
                    submitted_at = excluded.submitted_at
                """,
                (session_id, item["sample_id"], selected, method, utc_now()),
            )
            answered = conn.execute(
                "SELECT COUNT(*) AS n FROM responses WHERE session_id = ?", (session_id,)
            ).fetchone()["n"]
            complete = answered == len(assignment)
            if complete:
                conn.execute(
                    "UPDATE sessions SET completed_at = ? WHERE session_id = ?",
                    (utc_now(), session_id),
                )
            conn.commit()
        finally:
            conn.close()
    return {"ok": True, "answered": answered, "total": len(assignment), "complete": complete}


def get_stats() -> dict:
    with LOCK:
        conn = connect()
        sessions = conn.execute("SELECT COUNT(*) AS n FROM sessions WHERE completed_at IS NOT NULL").fetchone()["n"]
        started = conn.execute("SELECT COUNT(*) AS n FROM sessions").fetchone()["n"]
        rows = conn.execute("""
            SELECT sample_id, selected_method, selected_label, COUNT(*) AS n
            FROM responses GROUP BY sample_id, selected_method, selected_label
        """).fetchall()
        conn.close()
    per_sample = {}
    totals = {"sure_tagger": 0, "captioner": 0, "unsure": 0}
    for row in rows:
        sample = per_sample.setdefault(row["sample_id"], {"sure_tagger": 0, "captioner": 0, "unsure": 0})
        key = row["selected_method"] if row["selected_label"] in {"A", "B"} else "unsure"
        sample[key] += row["n"]
        totals[key] += row["n"]
    per_sample_rates = []
    for counts in per_sample.values():
        decisions = counts["sure_tagger"] + counts["captioner"]
        if decisions:
            per_sample_rates.append({
                "sure_tagger": counts["sure_tagger"] / decisions * 100,
                "captioner": counts["captioner"] / decisions * 100,
            })
    rate_count = len(per_sample_rates)
    return {
        "started": started,
        "completed": sessions,
        "questions_per_submission": len(SAMPLES),
        "total_responses": sum(totals.values()),
        "totals": totals,
        "rate_basis": "mean_per_sample",
        "rated_samples": rate_count,
        "rates": {
            "sure_tagger": round(
                sum(row["sure_tagger"] for row in per_sample_rates) / rate_count, 2
            ) if rate_count else 0,
            "captioner": round(
                sum(row["captioner"] for row in per_sample_rates) / rate_count, 2
            ) if rate_count else 0,
        },
        "per_sample": [
            {"position": SAMPLE_BY_ID[sid]["position"], "sample_id": sid, **counts}
            for sid, counts in sorted(per_sample.items(), key=lambda item: SAMPLE_BY_ID[item[0]]["position"])
        ],
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_ROOT), **kwargs)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/session":
            try:
                self._json(HTTPStatus.OK, make_session())
            except Exception as exc:
                self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
            return
        if parsed.path == "/api/stats":
            self._json(HTTPStatus.OK, get_stats())
            return
        if parsed.path.startswith("/media/"):
            relative = parsed.path.removeprefix("/media/")
            candidate = (DATA_ROOT / relative).resolve()
            if DATA_ROOT.resolve() not in candidate.parents or not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.path = "/__media__"
            self._serve_file(candidate)
            return
        if parsed.path == "/stats":
            self.path = "/stats.html"
        return super().do_GET()

    def _serve_file(self, path: Path) -> None:
        try:
            total_size = path.stat().st_size
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        start = 0
        end = total_size - 1
        status = HTTPStatus.OK
        range_header = self.headers.get("Range", "")
        if range_header.startswith("bytes="):
            # Audio elements commonly request a byte range while buffering.
            range_spec = range_header.removeprefix("bytes=").split(",", 1)[0].strip()
            try:
                start_text, end_text = range_spec.split("-", 1)
                if start_text:
                    start = int(start_text)
                    end = int(end_text) if end_text else end
                else:
                    suffix_length = int(end_text)
                    start = max(total_size - suffix_length, 0)
                end = min(end, total_size - 1)
                if start < 0 or start > end or start >= total_size:
                    raise ValueError
                status = HTTPStatus.PARTIAL_CONTENT
            except (TypeError, ValueError):
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{total_size}")
                self.end_headers()
                return

        content_length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(content_length))
        self.send_header("Accept-Ranges", "bytes")
        if status == HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        if self.command == "HEAD":
            return
        try:
            with path.open("rb") as stream:
                stream.seek(start)
                remaining = content_length
                while remaining:
                    chunk = stream.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            return

    def do_HEAD(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/media/"):
            relative = parsed.path.removeprefix("/media/")
            candidate = (DATA_ROOT / relative).resolve()
            if DATA_ROOT.resolve() not in candidate.parents or not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._serve_file(candidate)
            return
        if parsed.path == "/stats":
            self.path = "/stats.html"
        return super().do_HEAD()

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/answer", "/api/submit"}:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = submit_answer(payload) if parsed.path == "/api/answer" else submit_session(payload)
            self._json(HTTPStatus.OK, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except sqlite3.IntegrityError as exc:
            self._json(HTTPStatus.CONFLICT, {"error": str(exc)})
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    def log_message(self, fmt, *args):
        return


def main() -> None:
    global DB_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=DB_PATH, help="SQLite database path")
    args = parser.parse_args()
    DB_PATH = args.db.expanduser().resolve()
    connect().close()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"survey: http://{args.host}:{args.port}", flush=True)
    print(f"stats:  http://{args.host}:{args.port}/stats", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
