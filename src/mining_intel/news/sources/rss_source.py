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


def _strip_leading_junk(raw):
    """Some servers prepend stray content before the actual feed (observed
    live: Mendoza's `prensa/feed/` returns a `<script>...</script>` snippet
    before the real `<?xml ...?><rss>`, which breaks a strict XML parser
    with "junk after document element"). Slice from the earliest real feed
    start marker found, if any junk precedes it. Accepts `str` or `bytes`
    (tests commonly stub `fetch` with a plain `str`; real HTTP responses
    come back as `bytes` - see `RssNewsSource.fetch`).
    """
    markers = (b"<?xml", b"<rss", b"<feed") if isinstance(raw, bytes) else ("<?xml", "<rss", "<feed")
    candidates = [raw.find(marker) for marker in markers]
    candidates = [i for i in candidates if i > 0]
    return raw[min(candidates):] if candidates else raw


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
        root = ElementTree.fromstring(_strip_leading_junk(raw))
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
    AUTOMATION_METHOD = "RSS"
    SOURCE_TYPE = "Medio"


class AmbitoEnergiaSource(RssNewsSource):
    INTERNAL_NAME = "ambito_energia"
    DISPLAY_NAME = "Ámbito Financiero (Energy Report)"
    SOURCE_URL = "https://www.ambito.com/energia/91"
    FEED_URL = "https://www.ambito.com/rss/pages/energia.xml"
    OFFICIAL = False
    AUTOMATION_METHOD = "RSS"
    SOURCE_TYPE = "Medio"


class SaltaMineriaSource(RssNewsSource):
    INTERNAL_NAME = "salta_mineria"
    DISPLAY_NAME = "Ministerio de Producción y Minería de Salta"
    SOURCE_URL = "https://produccionsalta.gob.ar/"
    FEED_URL = "https://produccionsalta.gob.ar/feed/"
    OFFICIAL = True
    AUTOMATION_METHOD = "RSS"
    SOURCE_TYPE = "Provincial"


class SantaCruzMineriaSource(RssNewsSource):
    INTERNAL_NAME = "santa_cruz_mineria"
    DISPLAY_NAME = "Gobierno de Santa Cruz (Secretaría de Minería)"
    SOURCE_URL = "https://minpro.santacruz.gob.ar/category/mineria/"
    FEED_URL = "https://minpro.santacruz.gob.ar/category/mineria/feed/"
    OFFICIAL = True
    AUTOMATION_METHOD = "RSS"
    SOURCE_TYPE = "Provincial"


class MendozaPrensaSource(RssNewsSource):
    """General provincial press feed - Mendoza's own mining directorate site
    (informacionoficial.mendoza.gob.ar) returned 403 (bot protection) during
    investigation. This is the province's general press RSS instead; it
    covers all ministries, so real mining relevance is decided by the same
    strict `news.filters.is_mining_relevant` used for every free-text
    source (same pattern already used for Ámbito's general energy feed).
    """

    INTERNAL_NAME = "mendoza_mineria"
    DISPLAY_NAME = "Gobierno de Mendoza"
    SOURCE_URL = "https://www.mendoza.gov.ar/prensa/"
    FEED_URL = "https://www.mendoza.gov.ar/prensa/feed/"
    OFFICIAL = True
    AUTOMATION_METHOD = "RSS"
    SOURCE_TYPE = "Provincial"
