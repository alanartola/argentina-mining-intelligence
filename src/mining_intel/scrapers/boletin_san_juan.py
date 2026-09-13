import json
import re
from datetime import datetime, timezone

import requests

from mining_intel.config import (
    REQUEST_TIMEOUT,
    SAN_JUAN_MINERIA_ORG_ID,
    SAN_JUAN_TENDERS_URL,
    USER_AGENT,
)
from mining_intel.scrapers.base import BaseScraper

_OBJ_PATTERN = re.compile(r"var obj\s*=\s*(\{.*\});", re.DOTALL)
_DOTNET_DATE = re.compile(r"/Date\((-?\d+)\)/")


def _parse_dotnet_date(value):
    """Convert a .NET-style '/Date(1670295600000)/' timestamp to an ISO date."""
    if not value:
        return None
    match = _DOTNET_DATE.search(value)
    if not match:
        return None
    millis = int(match.group(1))
    return datetime.fromtimestamp(millis / 1000, tz=timezone.utc).date().isoformat()


class SanJuanTendersScraper(BaseScraper):
    """Licitaciones/compras del Ministerio de Minería, Portal Compras Públicas San Juan.

    The portal has no separate JSON/AJAX endpoint: filtering by "Organismo"
    POSTs to index.php and the results come back embedded in the HTML as an
    inline `var obj = {...};` blob that the page's own DataTables script
    reads client-side. We parse that blob directly instead of the (empty)
    server-rendered <table>. Verified live on 2026-09-13 with
    ministerio=2524 ("MINISTERIO DE MINERÍA").
    """

    SOURCE_NAME = "san_juan_licitaciones_mineria"
    TARGET_TABLE = "tenders"

    def fetch(self) -> str:
        response = requests.post(
            SAN_JUAN_TENDERS_URL,
            data={
                "estado": "",
                "tipo": "",
                "ministerio": SAN_JUAN_MINERIA_ORG_ID,
                "urllic": "",
                "xfechacompra": "",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.text

    def parse(self, raw: str) -> list[dict]:
        match = _OBJ_PATTERN.search(raw)
        if not match:
            return []

        data = json.loads(match.group(1))
        rows = data.get("licitaciones", {}).get("res", [])

        records = []
        for row in rows:
            records.append(
                {
                    "external_id": str(row.get("ID_PUBLICACION")),
                    "title": (row.get("OBJETO") or "").strip(),
                    "province": "San Juan",
                    "entity": row.get("INSTITUCION") or row.get("ORGANICA"),
                    "publish_date": _parse_dotnet_date(row.get("F_PUBLICACION")),
                    "closing_date": _parse_dotnet_date(row.get("F_APERTURA")),
                    "budget_ars": row.get("PRESUPUESTO"),
                    "status": row.get("ESTADOS"),
                    "url": SAN_JUAN_TENDERS_URL,
                }
            )
        return records
