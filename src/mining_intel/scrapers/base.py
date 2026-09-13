from abc import ABC, abstractmethod
from typing import Any


class BaseScraper(ABC):
    """Contract every data source implements.

    `pipeline.py` treats all sources uniformly through this interface, so
    adding a new source (another province, another dataset) never requires
    touching existing scrapers - only adding a new module.
    """

    SOURCE_NAME: str
    TARGET_TABLE: str  # "projects" or "tenders"

    @abstractmethod
    def fetch(self) -> Any:
        """Retrieve raw data from the source (HTTP response body, etc.)."""

    @abstractmethod
    def parse(self, raw: Any) -> list[dict]:
        """Turn raw source data into records shaped for `processing.normalize`."""

    def run(self) -> list[dict]:
        return self.parse(self.fetch())
