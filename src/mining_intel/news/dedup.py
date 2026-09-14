"""Deduplication for news events.

Two distinct layers:
1. `content_hash` - identifies "this exact record from this exact source"
   (stable across daily runs), enforced as a UNIQUE column on `news_events`.
   This is the primary "already seen, don't re-insert" guard.
2. `find_similar_event` - a secondary, cross-source pass: when a different
   source covers the same real-world event with a different URL/title, fold
   it into the existing event's `additional_sources` instead of creating a
   second row for the same story.
"""

import hashlib
import re
import unicodedata
from difflib import SequenceMatcher

_PUNCT_RE = re.compile(r"[^a-z0-9 ]+")

SIMILARITY_THRESHOLD = 0.82


def normalize_title(title: str) -> str:
    text = unicodedata.normalize("NFKD", (title or "").strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _PUNCT_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def content_hash(title: str, url: str, seed: str | None = None) -> str:
    """`seed` (e.g. "siacam-announcement:<external_id>") is used for
    structured sources where we have a stable natural id - more robust than
    hashing free text that could be re-worded slightly between fetches.
    """
    basis = seed if seed else f"{normalize_title(title)}|{url}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def find_similar_event(title: str, url: str, existing_events: list[dict]) -> dict | None:
    """`existing_events`: iterable of {"id", "title", "source_url", ...}.

    Returns the first existing event that looks like the same real-world
    story (identical URL, or title similarity above threshold), else None.
    """
    for event in existing_events:
        if event.get("source_url") == url:
            return event
        if title_similarity(title, event.get("title", "")) >= SIMILARITY_THRESHOLD:
            return event
    return None
