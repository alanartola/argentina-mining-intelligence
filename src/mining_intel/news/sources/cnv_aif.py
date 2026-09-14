"""CNV - Autopista de Información Financiera, Hechos Relevantes.

`cnv.gov.ar/sitioWeb/HechosRelevantes` is plain server-rendered HTML -
DataTables.js there only adds client-side pagination/sorting (confirmed by
reading its JS: no AJAX URL configured, the table is already in the HTML
response). The "EMPRESAS" tab (`#1a`) has a real table with a genuine
public document URL per row (`aif2.cnv.gov.ar/Presentations/publicview/{guid}`).

Per the request, this must never ingest "toda la CNV": only rows whose
ENTIDAD matches a company already known from `announcements.company` are
kept, via `_known_companies()` (same DB-aware pattern as
`siacam_updates.py`). Most days that will legitimately be zero matches -
Argentina's major mining operators (Barrick, Rio Tinto, Ganfeng, Lundin,
Glencore, etc.) are mostly foreign multinationals not CNV-registered. A
verified check against ~340 live rows found zero matches, which is the
correct, expected result - not a bug or a sign the source doesn't work.
"""

import re
import sqlite3
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from mining_intel.config import REQUEST_TIMEOUT, USER_AGENT
from mining_intel.news.sources.base import NewsSource

_STOPWORDS = {
    "s", "a", "sa", "sau", "sacif", "srl", "saic", "group", "ltd", "inc", "corp",
    "corporation", "mining", "resources", "gold", "silver", "lithium", "argentina",
    "de", "del", "la", "el", "y", "the", "compania", "compañia",
}

_CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("ACQUISITION", ["adquisicion", "compra de acciones", "fusion", "toma de control"]),
    ("FINANCING", ["obligaciones negociables", "emision", "financiamiento", "calificacion de riesgo", "deuda"]),
    ("INVESTMENT", ["inversion"]),
    ("PROJECT_UPDATE", ["proyecto"]),
    ("COMPANY_UPDATE", ["asamblea", "directorio", "hecho relevante", "societaria"]),
]

_MONTHS_ES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


_ACCENTS = str.maketrans("áéíóúñ", "aeioun")


def _normalize(text: str) -> str:
    return (text or "").lower().translate(_ACCENTS)


def _tokens(text: str) -> set[str]:
    normalized = re.sub(r"[^a-z0-9 ]", " ", _normalize(text))
    return {tok for tok in normalized.split() if len(tok) >= 4 and tok not in _STOPWORDS}


def _infer_category(descripcion: str) -> str:
    normalized = _normalize(descripcion)
    for category, keywords in _CATEGORY_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return category
    return "OTHER"


def _parse_cnv_date(value: str) -> str | None:
    match = re.match(r"(\d{1,2})\s+([a-záéíóú]{3})\.?\s+(\d{4})\s+(\d{1,2}):(\d{2})", (value or "").strip().lower())
    if not match:
        return None
    day, mon_abbr, year, hour, minute = match.groups()
    month = _MONTHS_ES.get(mon_abbr)
    if not month:
        return None
    try:
        return datetime(int(year), month, int(day), int(hour), int(minute)).isoformat()
    except ValueError:
        return None


class CnvHechosRelevantesSource(NewsSource):
    INTERNAL_NAME = "cnv_aif"
    DISPLAY_NAME = "CNV / AIF (Hechos Relevantes)"
    SOURCE_URL = "https://www.cnv.gov.ar/sitioWeb/HechosRelevantes"
    OFFICIAL = True
    AUTOMATION_METHOD = "HTML"
    SOURCE_TYPE = "Regulador"

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def _known_companies(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT DISTINCT company FROM announcements WHERE company IS NOT NULL AND company != ''"
        ).fetchall()
        return [row["company"] for row in rows]

    def fetch(self) -> dict:
        response = requests.get(
            self.SOURCE_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return {"html": response.text, "known_companies": self._known_companies()}

    def parse(self, raw: dict) -> list[dict]:
        soup = BeautifulSoup(raw["html"], "html.parser")
        # `find(id=...)`, not `.select("#1a ...")`: CSS identifiers can't
        # start with a digit, so soupsieve rejects "#1a" as a selector even
        # though it's a perfectly valid HTML id attribute.
        empresas_tab = soup.find(id="1a")
        empresas_table = empresas_tab.find("table") if empresas_tab else None
        if empresas_table is None:
            return []

        known_company_tokens = [_tokens(company) for company in raw["known_companies"]]
        if not known_company_tokens:
            return []

        items = []
        for row in empresas_table.select("tbody tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            fecha = cells[0].get_text(strip=True)
            entidad = cells[1].get_text(strip=True)
            descripcion = cells[2].get_text(strip=True)
            documento_id = cells[3].get_text(strip=True)

            entidad_tokens = _tokens(entidad)
            if not any(entidad_tokens & company_tokens for company_tokens in known_company_tokens):
                continue

            doc_link = row.select_one("a[href*='publicview']")
            url = doc_link.get("href") if doc_link else self.SOURCE_URL

            items.append(
                {
                    "title": f"{entidad}: {descripcion}"[:200],
                    "url": url,
                    "published_at": _parse_cnv_date(fecha),
                    "summary_raw": descripcion,
                    "category": _infer_category(descripcion),
                    "official": True,
                    "company": entidad,
                    "content_hash_seed": f"cnv-hecho:{documento_id}",
                }
            )
        return items
