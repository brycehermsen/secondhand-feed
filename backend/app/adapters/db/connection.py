from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()


def json_dumps(data: object | None) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)


def json_loads(raw: str | None) -> object | None:
    if raw in (None, ""):
        return None
    return json.loads(raw)
