"""Secretaría de Minería e Hidrocarburos de Jujuy, via the provincial press
office's own "Minería" tag listing.

`prensa.jujuy.gob.ar/mineria-a254/1` is a plain server-rendered page
(verified with a bare `requests.get`, no JS needed) already scoped to the
"Minería" category by the source itself - real title + excerpt + article
URL per item. No feed (`/feed`, `/rss/mineria.xml`) exists on this CMS; the
site's own RSS directory (`/contenidos/rss.html`) lists feeds per ministry
but none for Minería specifically, so this listing page is the actual
stable entry point.

No pre-set `category`: even though the page is already mining-scoped, this
still goes through `news.filters.is_mining_relevant` for consistency with
every other free-text source (cheap, and correct either way).
"""

import requests
from bs4 import BeautifulSoup

from mining_intel.config import REQUEST_TIMEOUT, USER_AGENT
from mining_intel.news.sources.base import NewsSource


class JujuyMineriaSource(NewsSource):
    INTERNAL_NAME = "jujuy_mineria"
    DISPLAY_NAME = "Gobierno de Jujuy (Secretaría de Minería e Hidrocarburos)"
    SOURCE_URL = "https://prensa.jujuy.gob.ar/mineria-a254/1"
    OFFICIAL = True
    AUTOMATION_METHOD = "HTML"
    SOURCE_TYPE = "Provincial"

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

        for article in soup.select("article.row"):
            title_link = article.select_one(".article-title a")
            if not title_link:
                continue
            title = title_link.get_text(strip=True)
            url = title_link.get("href", "")
            if not title or not url:
                continue

            excerpt_el = article.select_one(".article-excerp p")
            summary = excerpt_el.get_text(strip=True) if excerpt_el else ""

            items.append(
                {
                    "title": title,
                    "url": url,
                    "published_at": None,
                    "summary_raw": summary,
                    "official": True,
                    "content_hash_seed": f"jujuy-mineria:{url}",
                }
            )
        return items
