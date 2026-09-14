"""Best-effort, confidence-gated linking of a news item to a known province
and/or project. Never guesses: ambiguous or absent matches resolve to None
rather than to an assumed relationship.
"""

import re
import unicodedata

from mining_intel.config import PROVINCE_CENTROIDS

_MIN_PROJECT_NAME_LEN = 5


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def extract_province(text: str) -> str | None:
    """Returns a real province name only if exactly one is unambiguously
    mentioned (whole-word match) in `text`.
    """
    normalized = _normalize(text)
    matches = {
        province
        for province in PROVINCE_CENTROIDS
        if re.search(rf"\b{re.escape(_normalize(province))}\b", normalized)
    }
    return matches.pop() if len(matches) == 1 else None


def match_project(text: str, projects: list[tuple[str, str]]) -> str | None:
    """`projects`: iterable of (project_key, project_name) - `project_key`
    is `projects.project_key`, the *stable* identifier, not the numeric id
    (which is reassigned on every pipeline rebuild - see schema.sql).

    Returns a project_key only when exactly one known project name is
    unambiguously mentioned (whole-word, case/accent-insensitive). Very
    short/generic names are skipped as too unreliable to match on.
    """
    normalized_text = _normalize(text)
    matches = set()
    for project_key, name in projects:
        if not name or len(name) < _MIN_PROJECT_NAME_LEN:
            continue
        if re.search(rf"\b{re.escape(_normalize(name))}\b", normalized_text):
            matches.add(project_key)
    return matches.pop() if len(matches) == 1 else None
