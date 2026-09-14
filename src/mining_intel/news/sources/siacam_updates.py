"""SIACAM investment announcements, viewed through the news lens.

Not a network source in its own right: the real fetch already happened in
`mining_intel.pipeline.run_all()`, which populates `announcements`. This
class reads that table and emits one RawItem per announcement, tagged with
everything we already know precisely (province, mineral, company,
project_key) so the generic text-based filter/classify/link steps aren't
needed for it - those are for free-text media sources.

Reuses the SAME internal name as the structured-data scraper
(`SecretariaMineriaScraper.SOURCE_NAME`) since it is the same real-world
source, just surfaced as news too.
"""

import sqlite3

from mining_intel.news.sources.base import NewsSource
from mining_intel.processing.dedup import split_provinces


class SiacamAnnouncementsNewsSource(NewsSource):
    INTERNAL_NAME = "secretaria_mineria_siacam"
    DISPLAY_NAME = "Secretaría de Minería"
    SOURCE_URL = "https://www.argentina.gob.ar/economia/mineria/siacam"
    OFFICIAL = True

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def fetch(self) -> list[sqlite3.Row]:
        # Join to the *current* project_key rather than trusting the stored
        # numeric announcements.project_id long-term - `projects.id` is
        # reassigned on every rebuild, but project_key is stable (see
        # schema.sql's note on `news_events.project_key`).
        return self._conn.execute(
            """
            SELECT a.*, p.project_key AS project_key
            FROM announcements a
            LEFT JOIN projects p ON p.id = a.project_id
            """
        ).fetchall()

    def parse(self, raw: list[sqlite3.Row]) -> list[dict]:
        items = []
        for row in raw:
            amount = row["investment_usd"]
            amount_text = f"USD {amount:,.0f}" if amount else "monto no informado"
            provinces = split_provinces(row["province"] or "")
            province = provinces[0] if provinces else None

            items.append(
                {
                    "title": f"Anuncio de inversión: {row['name'] or row['company']} ({row['province']})",
                    "url": row["source_url"] or self.SOURCE_URL,
                    "published_at": row["announced_date"],
                    "summary_raw": (
                        f"{row['company']} anunció {amount_text} para el proyecto "
                        f"{row['name']} ({row['mineral']}, {row['province']}). "
                        f"Etapa declarada en el anuncio: {row['stage']}."
                    ),
                    "category": "INVESTMENT",
                    "official": True,
                    "province": province,
                    "mineral": row["mineral"],
                    "company": row["company"],
                    "project_key": row["project_key"],
                    "investment_usd": amount,
                    "content_hash_seed": f"siacam-announcement:{row['external_id']}",
                }
            )
        return items
