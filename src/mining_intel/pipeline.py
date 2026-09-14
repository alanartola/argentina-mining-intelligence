import logging
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from mining_intel.db.connection import connection
from mining_intel.processing.dedup import build_projects
from mining_intel.processing.normalize import normalize_announcements, normalize_tenders
from mining_intel.scrapers.base import BaseScraper
from mining_intel.scrapers.boletin_san_juan import SanJuanTendersScraper
from mining_intel.scrapers.secretaria_mineria import SecretariaMineriaScraper

logger = logging.getLogger(__name__)

SCRAPERS: list[BaseScraper] = [
    SecretariaMineriaScraper(),
    SanJuanTendersScraper(),
]

_ANNOUNCEMENT_COLUMNS = [
    "external_id", "source", "name", "company", "province", "mineral",
    "stage", "investment_usd", "announced_date", "source_url", "last_updated",
]

_TENDER_COLUMNS = [
    "external_id", "source", "title", "province", "entity",
    "publish_date", "closing_date", "budget_ars", "status", "url",
    "last_updated",
]

_PROJECT_COLUMNS = [
    "project_key", "name", "primary_province", "mineral", "stage",
    "total_investment_usd", "announcement_count", "lat", "lon", "last_updated",
]


def _upsert(conn: sqlite3.Connection, table: str, columns: list[str], df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    for column in columns:
        if column not in df.columns:
            df[column] = None
    df = df[columns]

    placeholders = ", ".join("?" for _ in columns)
    column_list = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO {table} ({column_list}) VALUES ({placeholders})"
    conn.executemany(sql, df.itertuples(index=False, name=None))
    return len(df)


def rebuild_projects(conn: sqlite3.Connection) -> int:
    """Recompute the deduplicated `projects` (and `project_provinces`) tables
    from the full `announcements` history.

    Cheap to run from scratch every time (tens to low hundreds of rows), so
    there is no incremental-merge complexity: this always reflects exactly
    what `processing.dedup.build_projects` would produce from the current
    `announcements` table.
    """
    announcements_df = pd.read_sql_query("SELECT * FROM announcements", conn)
    projects_df, provinces_df, external_id_to_key = build_projects(announcements_df)

    conn.execute("DELETE FROM project_provinces")
    conn.execute("DELETE FROM projects")

    if projects_df.empty:
        return 0

    projects_df = projects_df.copy()
    projects_df["last_updated"] = datetime.now(timezone.utc).isoformat()
    _upsert(conn, "projects", _PROJECT_COLUMNS, projects_df)

    key_to_id = {
        row["project_key"]: row["id"]
        for row in conn.execute("SELECT id, project_key FROM projects").fetchall()
    }

    if not provinces_df.empty:
        provinces_df = provinces_df.copy()
        provinces_df["project_id"] = provinces_df["project_key"].map(key_to_id)
        conn.executemany(
            "INSERT OR IGNORE INTO project_provinces (project_id, province) VALUES (?, ?)",
            provinces_df[["project_id", "province"]].itertuples(index=False, name=None),
        )

    conn.executemany(
        "UPDATE announcements SET project_id = ? WHERE external_id = ?",
        [(key_to_id.get(key), external_id) for external_id, key in external_id_to_key.items()],
    )

    return len(projects_df)


def run_all(db_path: Optional[Path] = None) -> None:
    """Run every registered scraper, load its records into sqlite, then
    rebuild the deduplicated projects view.

    A failure in one source (site redesign, timeout, etc.) is logged to
    `scrape_runs` and does not stop the other sources from updating - this
    is what keeps the daily GitHub Actions job resilient as more sources are
    added over time.
    """
    with connection(db_path) as conn:
        for scraper in SCRAPERS:
            started_at = datetime.now(timezone.utc).isoformat()
            try:
                raw_records = scraper.run()
                if scraper.TARGET_TABLE == "announcements":
                    df = normalize_announcements(raw_records, source=scraper.SOURCE_NAME)
                    count = _upsert(conn, "announcements", _ANNOUNCEMENT_COLUMNS, df)
                else:
                    df = normalize_tenders(raw_records, source=scraper.SOURCE_NAME)
                    count = _upsert(conn, "tenders", _TENDER_COLUMNS, df)

                conn.execute(
                    "INSERT INTO scrape_runs "
                    "(source, started_at, finished_at, records_found, status, error) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        scraper.SOURCE_NAME,
                        started_at,
                        datetime.now(timezone.utc).isoformat(),
                        count,
                        "ok",
                        None,
                    ),
                )
                logger.info("%s: %d records", scraper.SOURCE_NAME, count)
            except Exception as exc:  # noqa: BLE001 - isolate one source's failure from the rest
                conn.execute(
                    "INSERT INTO scrape_runs "
                    "(source, started_at, finished_at, records_found, status, error) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        scraper.SOURCE_NAME,
                        started_at,
                        datetime.now(timezone.utc).isoformat(),
                        0,
                        "error",
                        str(exc),
                    ),
                )
                logger.error("%s failed: %s", scraper.SOURCE_NAME, exc)
                logger.debug(traceback.format_exc())

        n_projects = rebuild_projects(conn)
        logger.info("projects rebuilt: %d unique projects", n_projects)
