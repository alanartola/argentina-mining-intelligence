import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from mining_intel.config import DB_PATH, SCHEMA_PATH


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open a sqlite3 connection with the schema applied.

    This is the only module that knows the database is sqlite3 - callers
    (pipeline, app pages) go through here or through `db.queries` so that a
    future move to PostgreSQL/Supabase only touches this file.
    """
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


@contextmanager
def connection(db_path: Optional[Path] = None):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
