import sqlite3

import pytest

from mining_intel.db.connection import get_connection


def test_news_tables_are_created_by_schema(tmp_path):
    conn = get_connection(tmp_path / "schema_test.db")
    try:
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()
    assert "news_events" in tables
    assert "news_sources" in tables


def test_content_hash_is_enforced_unique(tmp_path):
    conn = get_connection(tmp_path / "unique_test.db")
    try:
        conn.execute(
            """
            INSERT INTO news_events
                (content_hash, title, source_internal_name, source_url, detected_at, category, relevance)
            VALUES ('hash-1', 'Título', 'test_source', 'https://example.com/1', '2026-09-13T00:00:00', 'NEWS', 'LOW')
            """
        )
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO news_events
                    (content_hash, title, source_internal_name, source_url, detected_at, category, relevance)
                VALUES ('hash-1', 'Otro título', 'test_source', 'https://example.com/2', '2026-09-13T01:00:00', 'NEWS', 'LOW')
                """
            )
    finally:
        conn.close()


def test_news_sources_has_automation_method_and_source_type_columns(tmp_path):
    conn = get_connection(tmp_path / "columns_test.db")
    try:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(news_sources)")}
    finally:
        conn.close()
    assert "automation_method" in columns
    assert "source_type" in columns


def test_news_sources_upsert_by_internal_name(tmp_path):
    conn = get_connection(tmp_path / "sources_test.db")
    try:
        conn.execute(
            "INSERT INTO news_sources (internal_name, display_name, state) VALUES ('src', 'Fuente', 'ACTIVE')"
        )
        conn.execute(
            """
            INSERT INTO news_sources (internal_name, display_name, state)
            VALUES ('src', 'Fuente', 'FAILED')
            ON CONFLICT(internal_name) DO UPDATE SET state = excluded.state
            """
        )
        row = conn.execute("SELECT state FROM news_sources WHERE internal_name = 'src'").fetchone()
        count = conn.execute("SELECT COUNT(*) AS c FROM news_sources WHERE internal_name = 'src'").fetchone()["c"]
    finally:
        conn.close()
    assert row["state"] == "FAILED"
    assert count == 1
