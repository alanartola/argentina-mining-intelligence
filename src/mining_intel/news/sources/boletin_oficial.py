"""Boletín Oficial de la República Argentina - Primera Sección (leyes,
decretos, resoluciones).

The public search (`busquedaAvanzada`) is client-rendered - no public API
was found for it (unlike CABA's Boletín Oficial, which has one). But
`/seccion/primera` itself is a plain server-rendered listing with a real
descriptive line per aviso (verified with a bare `requests.get`, no JS
needed), so that's what this scrapes.

`/seccion/tercera` (contrataciones) is also plain HTML but each entry is
only "Licitación Pública NNNN/YYYY" with no descriptive text - not usable
for keyword filtering without fetching every single detail page, so it's
intentionally out of scope for now rather than guessed at.

No pre-set `category`: most avisos here have nothing to do with mining, so
this must go through the normal `news.filters.is_mining_relevant` check
like any other free-text source - only avisos that actually mention mining
survive, then `news.classify.infer_category` labels them (defaults to
OFFICIAL_PUBLICATION for an official source with no more specific match).
"""

import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from mining_intel.config import REQUEST_TIMEOUT, USER_AGENT
from mining_intel.news.sources.base import NewsSource

_AVISO_LINK_RE = re.compile(r"^/detalleAviso/primera/(\d+)/(\d{8})$")


class BoletinOficialSource(NewsSource):
    INTERNAL_NAME = "boletin_oficial_nacional"
    DISPLAY_NAME = "Boletín Oficial"
    SOURCE_URL = "https://www.boletinoficial.gob.ar/seccion/primera"
    OFFICIAL = True
    AUTOMATION_METHOD = "HTML"
    SOURCE_TYPE = "Nacional"

    def fetch(self) -> str:
        response = requests.get(
            self.SOURCE_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.text

    def parse(self, raw: str) -> list[dict]:
        soup = BeautifulSoup(raw, "html.parser")
        items = []
        seen_ids = set()

        for link in soup.select("a[href^='/detalleAviso/primera/']"):
            match = _AVISO_LINK_RE.match(link.get("href", ""))
            if not match:
                continue
            aviso_id, date_str = match.groups()
            if aviso_id in seen_ids:
                continue
            seen_ids.add(aviso_id)

            organismo_el = link.select_one(".item")
            detail_texts = [
                el.get_text(strip=True) for el in link.select(".item-detalle small") if el.get_text(strip=True)
            ]
            organismo = organismo_el.get_text(strip=True) if organismo_el else ""
            # The first `.item-detalle` is the norm number ("Decreto 983/2026");
            # a second one (when present) is the actual descriptive text.
            norma = detail_texts[0] if detail_texts else ""
            descripcion = detail_texts[1] if len(detail_texts) > 1 else norma

            try:
                published_at = datetime.strptime(date_str, "%Y%m%d").date().isoformat()
            except ValueError:
                published_at = None

            title = f"{organismo} - {norma}".strip(" -") or f"Aviso {aviso_id}"

            items.append(
                {
                    "title": title,
                    "url": f"https://www.boletinoficial.gob.ar/detalleAviso/primera/{aviso_id}/{date_str}",
                    "published_at": published_at,
                    "summary_raw": descripcion or norma,
                    "official": True,
                    "content_hash_seed": f"boletin-oficial-primera:{aviso_id}",
                }
            )
        return items
