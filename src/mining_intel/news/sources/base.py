"""Contract every news source implements.

Mirrors `mining_intel.scrapers.base.BaseScraper` on purpose: same
fetch/parse split, same "one class per source" shape, so this reads as an
extension of the existing pipeline rather than a separate system.

A `RawItem` (the dicts `parse()` returns) has at least:
    title, url, published_at (ISO date string or None), summary_raw
"""

from abc import ABC, abstractmethod
from typing import Any


class NewsSource(ABC):
    INTERNAL_NAME: str
    DISPLAY_NAME: str
    SOURCE_URL: str
    OFFICIAL: bool = False
    # How the source is actually consulted (API/RSS/DATASET/HTML/SEARCH) and
    # a coarse grouping (Nacional/Provincial/Regulador/Medio) - shown as-is
    # in the "Fuentes" data-quality view, never implying a stronger
    # guarantee than what's really there.
    AUTOMATION_METHOD: str = "HTML"
    SOURCE_TYPE: str = "Medio"

    @abstractmethod
    def fetch(self) -> Any:
        """Retrieve raw data from the source (HTTP response body, etc.)."""

    @abstractmethod
    def parse(self, raw: Any) -> list[dict]:
        """Turn raw source data into a list of RawItem dicts."""

    def run(self) -> list[dict]:
        return self.parse(self.fetch())
