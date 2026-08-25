"""SQLite persistence for affect, events, memories. Spaces wipe /data unless a bucket is mounted."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "ara_eve.sqlite"


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = path or DEFAULT_DB
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS affect_state (
            user_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            pleasure REAL,
            wanting REAL,
            last_peak_at REAL,
            contact_need REAL,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS affect_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            turn_id TEXT,
            appraisal_json TEXT,
            delta_pleasure REAL,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            text TEXT,
            affect_at_write REAL,
            hot INTEGER,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            affect_at_write REAL,
            created_at TEXT
        );
        """
    )
    conn.commit()


def save_affect(conn: sqlite3.Connection, user_id: str, snapshot: dict) -> None:
    pad_p = float(snapshot.get("pad", {}).get("p", 0))
    conn.execute(
        """
        INSERT INTO affect_state(user_id, payload, pleasure, wanting, last_peak_at, contact_need, updated_at)
        VALUES(?,?,?,?,?,?,datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            payload=excluded.payload,
            pleasure=excluded.pleasure,
            wanting=excluded.wanting,
            last_peak_at=excluded.last_peak_at,
            contact_need=excluded.contact_need,
            updated_at=datetime('now')
        """,
        (
            user_id,
            json.dumps(snapshot),
            pad_p,
            float(snapshot.get("wanting", 0)),
            float(snapshot.get("last_peak_at", -1)),
            float(snapshot.get("needs", {}).get("social", 0)),
        ),
    )
    conn.commit()


def log_event(conn: sqlite3.Connection, user_id: str, turn_id: str, appraisal: dict, delta: float) -> None:
    conn.execute(
        "INSERT INTO affect_events(user_id, turn_id, appraisal_json, delta_pleasure, created_at) VALUES(?,?,?,?,datetime('now'))",
        (user_id, turn_id, json.dumps(appraisal), delta),
    )
    conn.commit()


def add_memory(conn: sqlite3.Connection, user_id: str, text: str, affect: float, hot: bool) -> None:
    conn.execute(
        "INSERT INTO memories(user_id, text, affect_at_write, hot, created_at) VALUES(?,?,?,?,datetime('now'))",
        (user_id, text, affect, 1 if hot else 0),
    )
    conn.commit()


def recent_memories(conn: sqlite3.Connection, user_id: str, mood_p: float, limit: int = 8) -> list[str]:
    rows = conn.execute(
        "SELECT text, affect_at_write, hot FROM memories WHERE user_id=? ORDER BY hot DESC, abs(affect_at_write - ?) ASC, id DESC LIMIT ?",
        (user_id, mood_p, limit),
    ).fetchall()
    return [str(row["text"]) for row in rows]
