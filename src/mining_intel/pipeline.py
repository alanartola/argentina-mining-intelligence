import logging
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from mining_intel.db.connection import connection
from mining_intel.processing.normalize import normalize_projects, normalize_tenders
from mining_intel.scrapers.base import BaseScraper
from mining_intel.scrapers.boletin_san_juan import SanJuanTendersScraper
from mining_intel.scrapers.secretaria_mineria import SecretariaMineriaScraper

logger = logging.getLogger(__name__)

SCRAPERS: list[BaseScraper] = [
    SecretariaMineriaScraper(),
    SanJuanTendersScraper(),
]

_PROJECT_COLUMNS = [
    "external_id", "source", "name", "company", "province", "mineral",
    "stage", "investment_usd", "announced_date", "lat", "lon",
    "source_url", "last_updated",
]

_TENDER_COLUMNS = [
    "external_id", "source", "title", "province", "entity",
    "publish_date", "closing_date", "budget_ars", "status", "url",
    "last_updated",
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


def run_all(db_path: Optional[Path] = None) -> None:
    """Run every registered scraper and load its records into sqlite.

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
                if scraper.TARGET_TABLE == "projects":
                    df = normalize_projects(raw_records, source=scraper.SOURCE_NAME)
                    count = _upsert(conn, "projects", _PROJECT_COLUMNS, df)
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
