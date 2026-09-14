"""Numeric importance scoring, for ranking within `classify.classify_relevance`'s
tiers rather than replacing them.

The CRITICAL/HIGH/MEDIUM/LOW tier already decides *whether* an event matters
(and is kept fully explainable - see `classify.py`). What it can't do is put
two CRITICAL events in order: a routine SIACAM record and a $2B copper
announcement both land as CRITICAL, but only one belongs in a 3-item daily
brief. `score_event` adds that ordering on top of the same already-stored
fields - no re-classification, no new columns.
"""

import re

_ACCENTS = str.maketrans("áéíóúñ", "aeioun")

_TIER_BASE = {"CRITICAL": 100.0, "HIGH": 70.0, "MEDIUM": 40.0, "LOW": 10.0}

_CATEGORY_WEIGHT = {
    "RIGI": 22.0,
    "INVESTMENT": 18.0,
    "CONSTRUCTION": 16.0,
    "FINANCING": 14.0,
    "REGULATION": 14.0,
    "CONCESSION": 10.0,
    "TENDER": 10.0,
    "PERMIT": 8.0,
    "PROJECT_UPDATE": 6.0,
    "COMPANY_UPDATE": 4.0,
    "OFFICIAL_PUBLICATION": 2.0,
    "NEWS": 0.0,
}

# Business-priority topics for the daily brief: inversiones, nuevos
# proyectos, ampliaciones, producción, exportaciones, minerales
# estratégicos, M&A, financiamiento, licitaciones y cambios regulatorios.
# Matched as whole words/phrases against normalized (accent-stripped) text -
# not a bare substring - so "oro" never fires on "incorporó" (see the same
# precaution in `news.filters`).
_TOPIC_KEYWORDS: dict[str, float] = {
    "ampliacion": 10.0,
    "nuevo proyecto": 12.0,
    "produccion": 6.0,
    "exportacion": 8.0,
    "litio": 6.0,
    "cobre": 6.0,
    "oro": 4.0,
    "plata": 4.0,
    "uranio": 6.0,
    "fusion": 10.0,
    "adquisicion": 10.0,
    "financiamiento": 8.0,
    "licitacion": 6.0,
    "decreto": 6.0,
    "resolucion": 6.0,
    "rigi": 10.0,
}

_OFFICIAL_BONUS = 5.0

_USD_RE = re.compile(r"usd\s*([\d.,]+)")
_MAX_INVESTMENT_BONUS = 30.0
_INVESTMENT_BONUS_DIVISOR = 20_000_000.0


def _normalize(text: str) -> str:
    return (text or "").lower().translate(_ACCENTS)


def _topic_bonus(normalized_text: str) -> float:
    return sum(
        weight
        for keyword, weight in _TOPIC_KEYWORDS.items()
        if re.search(rf"\b{re.escape(keyword)}\b", normalized_text)
    )


def _investment_bonus(normalized_text: str) -> float:
    match = _USD_RE.search(normalized_text)
    if not match:
        return 0.0
    digits = match.group(1).replace(".", "").replace(",", "")
    if not digits.isdigit():
        return 0.0
    return min(_MAX_INVESTMENT_BONUS, float(digits) / _INVESTMENT_BONUS_DIVISOR)


def score_event(row) -> float:
    """`row`: anything dict-like with `.get` - a plain dict, sqlite3.Row cast
    to dict, or a pandas Series (one row of `get_news_events_df()`) all work.
    Needs `relevance`, `category`, `official`, `title`, `summary`.
    """
    relevance = (row.get("relevance") or "LOW").upper()
    category = (row.get("category") or "NEWS").upper()
    normalized_text = _normalize(f"{row.get('title') or ''} {row.get('summary') or ''}")

    score = _TIER_BASE.get(relevance, _TIER_BASE["LOW"])
    score += _CATEGORY_WEIGHT.get(category, 0.0)
    score += _topic_bonus(normalized_text)
    score += _investment_bonus(normalized_text)
    if row.get("official"):
        score += _OFFICIAL_BONUS
    return score
