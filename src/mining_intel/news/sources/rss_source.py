"""Generic RSS ingestion - stdlib only (xml.etree + email.utils), no new
pip dependency. Concrete sources below just set FEED_URL/INTERNAL_NAME/
DISPLAY_NAME/SOURCE_URL; the mining-relevance filtering happens later in
`news.filters`, not here - a source's job is only to report what it
publishes.
"""

import re
from email.utils import parsedate_to_datetime
from html import unescape
from xml.etree import ElementTree

import requests

from mining_intel.config import REQUEST_TIMEOUT, USER_AGENT
from mining_intel.news.sources.base import NewsSource

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return unescape(_TAG_RE.sub(" ", text or "")).strip()


def _parse_pubdate(value: str) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return None


class RssNewsSource(NewsSource):
    FEED_URL: str

    def fetch(self) -> bytes:
        response = requests.get(
            self.FEED_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        # Raw bytes, not `.text`: requests sometimes mis-guesses the charset
        # from HTTP headers alone (observed real mojibake on one of these
        # feeds). Handing ElementTree the bytes lets it honor the feed's own
        # `<?xml ... encoding="UTF-8"?>` declaration instead.
        return response.content

    def parse(self, raw: bytes) -> list[dict]:
        root = ElementTree.fromstring(raw)
        items = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not title or not link:
                continue
            items.append(
                {
                    "title": title,
                    "url": link,
                    "published_at": _parse_pubdate(item.findtext("pubDate")),
                    "summary_raw": _strip_html(item.findtext("description") or ""),
                }
            )
        return items


class MineriaYDesarrolloSource(RssNewsSource):
    INTERNAL_NAME = "mineria_y_desarrollo"
    DISPLAY_NAME = "Minería & Desarrollo"
    SOURCE_URL = "https://www.mineriaydesarrollo.com/"
    FEED_URL = "https://www.mineriaydesarrollo.com/rss/mineria/"
    OFFICIAL = False


class AmbitoEnergiaSource(RssNewsSource):
    INTERNAL_NAME = "ambito_energia"
    DISPLAY_NAME = "Ámbito Financiero (Energy Report)"
    SOURCE_URL = "https://www.ambito.com/energia/91"
    FEED_URL = "https://www.ambito.com/rss/pages/energia.xml"
    OFFICIAL = False


class SaltaMineriaSource(RssNewsSource):
    INTERNAL_NAME = "salta_mineria"
    DISPLAY_NAME = "Ministerio de Producción y Minería de Salta"
    SOURCE_URL = "https://produccionsalta.gob.ar/"
    FEED_URL = "https://produccionsalta.gob.ar/feed/"
    OFFICIAL = True
