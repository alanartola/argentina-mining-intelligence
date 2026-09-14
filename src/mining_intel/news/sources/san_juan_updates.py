"""San Juan mining tenders, viewed through the news lens.

Same idea as `siacam_updates.py`: reads the already-populated `tenders`
table (from `mining_intel.pipeline.run_all()`) instead of hitting the
network again, and emits one RawItem per tender with structured fields
pre-filled.
"""

import sqlite3

from mining_intel.news.sources.base import NewsSource


class SanJuanTendersNewsSource(NewsSource):
    INTERNAL_NAME = "san_juan_licitaciones_mineria"
    DISPLAY_NAME = "Ministerio de Minería de San Juan"
    SOURCE_URL = "https://licitaciones.sanjuan.gob.ar/"
    OFFICIAL = True

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def fetch(self) -> list[sqlite3.Row]:
        return self._conn.execute("SELECT * FROM tenders").fetchall()

    def parse(self, raw: list[sqlite3.Row]) -> list[dict]:
        items = []
        for row in raw:
            budget = row["budget_ars"]
            budget_text = f"$ {budget:,.0f}" if budget else "presupuesto no informado"
            items.append(
                {
                    "title": f"Licitación: {row['title'][:120]}",
                    "url": row["url"] or self.SOURCE_URL,
                    "published_at": row["publish_date"],
                    "summary_raw": (
                        f"{row['entity']} publicó una licitación en {row['province']} "
                        f"por {budget_text}. Estado: {row['status']}."
                    ),
                    "category": "TENDER",
                    "official": True,
                    "province": row["province"],
                    "content_hash_seed": f"san-juan-tender:{row['external_id']}",
                    "raw_status": row["status"],
                }
            )
        return items
