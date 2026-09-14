"""Daily mining-news monitor orchestration.

Run order: fetch -> (mining filter, free-text sources only) -> classify
category/relevance -> link province/project -> dedup (exact hash, then
fuzzy cross-source fold) -> upsert `news_events` -> record source health in
`news_sources`. One source's failure never stops the others (same
resilience pattern as `mining_intel.pipeline.run_all`).
"""

import json
import logging
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from mining_intel.db.connection import connection
from mining_intel.news import classify, dedup, filters, link_project
from mining_intel.news.sources.base import NewsSource
from mining_intel.news.sources.rss_source import AmbitoEnergiaSource, MineriaYDesarrolloSource, SaltaMineriaSource
from mining_intel.news.sources.san_juan_updates import SanJuanTendersNewsSource
from mining_intel.news.sources.siacam_updates import SiacamAnnouncementsNewsSource
from mining_intel.news.unsupported_sources import UNSUPPORTED_SOURCES

logger = logging.getLogger(__name__)

RSS_SOURCE_CLASSES: list[type[NewsSource]] = [
    MineriaYDesarrolloSource,
    AmbitoEnergiaSource,
    SaltaMineriaSource,
]


def _load_projects(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    return [(row["project_key"], row["name"]) for row in conn.execute("SELECT project_key, name FROM projects").fetchall()]


def _existing_events(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, title, source_url, additional_sources FROM news_events").fetchall()
    return [dict(row) for row in rows]


def _upsert_source_status(
    conn: sqlite3.Connection,
    internal_name: str,
    display_name: str,
    state: str,
    success: bool,
    count: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    existing = conn.execute(
        "SELECT last_success_at FROM news_sources WHERE internal_name = ?", (internal_name,)
    ).fetchone()
    last_success_at = now if success else (existing["last_success_at"] if existing else None)

    conn.execute(
        """
        INSERT INTO news_sources
            (internal_name, display_name, state, last_run_at, last_success_at, last_document_count, last_error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(internal_name) DO UPDATE SET
            display_name = excluded.display_name,
            state = excluded.state,
            last_run_at = excluded.last_run_at,
            last_success_at = excluded.last_success_at,
            last_document_count = excluded.last_document_count,
            last_error = excluded.last_error
        """,
        (internal_name, display_name, state, now, last_success_at, count, error),
    )


def _process_item(conn: sqlite3.Connection, source: NewsSource, item: dict, projects: list[tuple[str, str]]) -> bool:
    """Returns True if a new `news_events` row was inserted."""
    title = item["title"]
    url = item["url"]
    text_for_rules = f"{title}. {item.get('summary_raw', '')}"

    is_structured = "category" in item
    if not is_structured and not filters.is_mining_relevant(text_for_rules):
        return False

    category = item.get("category") or classify.infer_category(text_for_rules, official=source.OFFICIAL)
    relevance, reason = classify.classify_relevance(
        text_for_rules, category=category, investment_usd=item.get("investment_usd")
    )

    province = item.get("province") or link_project.extract_province(text_for_rules)
    project_key = item.get("project_key")
    if project_key is None:
        project_key = link_project.match_project(text_for_rules, projects)

    content_hash_value = dedup.content_hash(title, url, seed=item.get("content_hash_seed"))
    now = datetime.now(timezone.utc).isoformat()

    existing_row = conn.execute(
        "SELECT id, raw_text FROM news_events WHERE content_hash = ?", (content_hash_value,)
    ).fetchone()
    if existing_row is not None:
        if (existing_row["raw_text"] or "") != text_for_rules:
            conn.execute(
                "UPDATE news_events SET summary = ?, raw_text = ?, updated_at = ?, status = 'UPDATED' WHERE id = ?",
                (item.get("summary_raw"), text_for_rules, now, existing_row["id"]),
            )
        return False

    # Cross-source fuzzy folding only makes sense for free-text sources,
    # where two outlets can genuinely cover the same real-world story under
    # different URLs. Structured sources (content_hash_seed set) each have
    # their own authoritative per-record identity and share one generic
    # landing-page URL across all their records - matching on that would
    # wrongly fold every unrelated announcement/tender into a single event.
    similar = None if item.get("content_hash_seed") else dedup.find_similar_event(title, url, _existing_events(conn))
    if similar is not None:
        try:
            existing_list = json.loads(similar.get("additional_sources") or "[]")
        except ValueError:
            existing_list = []
        existing_list.append({"source": source.INTERNAL_NAME, "url": url})
        conn.execute(
            "UPDATE news_events SET additional_sources = ? WHERE id = ?",
            (json.dumps(existing_list, ensure_ascii=False), similar["id"]),
        )
        return False

    conn.execute(
        """
        INSERT INTO news_events (
            content_hash, title, summary, source_internal_name, source_url,
            publication_date, detected_at, category, relevance, relevance_reason,
            province, project_key, company, mineral, official, status, additional_sources, raw_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', '[]', ?)
        """,
        (
            content_hash_value,
            title,
            item.get("summary_raw"),
            source.INTERNAL_NAME,
            url,
            item.get("published_at"),
            now,
            category,
            relevance,
            reason,
            province,
            project_key,
            item.get("company"),
            item.get("mineral"),
            1 if item.get("official", source.OFFICIAL) else 0,
            text_for_rules,
        ),
    )
    return True


def run_daily(db_path: Optional[Path] = None) -> dict:
    """Run every registered news source once. Returns a per-source summary."""
    summary: dict = {"sources": {}, "total_new_events": 0}

    with connection(db_path) as conn:
        projects = _load_projects(conn)

        sources: list[NewsSource] = [
            SiacamAnnouncementsNewsSource(conn),
            SanJuanTendersNewsSource(conn),
        ] + [cls() for cls in RSS_SOURCE_CLASSES]

        for source in sources:
            try:
                items = source.run()
                new_count = sum(_process_item(conn, source, item, projects) for item in items)
                _upsert_source_status(
                    conn, source.INTERNAL_NAME, source.DISPLAY_NAME, "ACTIVE", True, count=len(items)
                )
                summary["sources"][source.INTERNAL_NAME] = {
                    "fetched": len(items),
                    "new_events": new_count,
                    "status": "ok",
                }
                summary["total_new_events"] += new_count
                logger.info("%s: %d fetched, %d new events", source.INTERNAL_NAME, len(items), new_count)
            except Exception as exc:  # noqa: BLE001 - isolate one source's failure from the rest
                _upsert_source_status(
                    conn, source.INTERNAL_NAME, source.DISPLAY_NAME, "FAILED", False, error=str(exc)
                )
                summary["sources"][source.INTERNAL_NAME] = {
                    "fetched": 0,
                    "new_events": 0,
                    "status": "error",
                    "error": str(exc),
                }
                logger.error("%s failed: %s", source.INTERNAL_NAME, exc)
                logger.debug(traceback.format_exc())

        for entry in UNSUPPORTED_SOURCES:
            exists = conn.execute(
                "SELECT 1 FROM news_sources WHERE internal_name = ?", (entry["internal_name"],)
            ).fetchone()
            if exists is None:
                conn.execute(
                    "INSERT INTO news_sources (internal_name, display_name, state, last_error) VALUES (?, ?, ?, ?)",
                    (entry["internal_name"], entry["display_name"], entry["state"], entry["reason"]),
                )

    return summary
