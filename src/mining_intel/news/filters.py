"""Exclusive mining-relevance filter.

Applied only to free-text sources (RSS media/provincial press releases).
Items that already arrive with a structured `category` (SIACAM
announcements, San Juan tenders) skip this filter entirely - they come
from sources that are mining-only by construction.

Deliberately strict: a bare mention of "minería" is NOT enough by itself.
Real example that motivated this - a Salta government press release about a
fintech meetup passed the old filter only because it was published under
the letterhead "Ministerios de Producción y Minería" (the ministry's own
combined name), even though the article has nothing to do with mining. The
fix is requiring *concrete* evidence: a named mineral, an explicit
mining-specific phrase ("proyecto minero", "empresa minera", "licitación
minera", "Secretaría/Ministerio de Minería" as the actual subject, etc.),
or a generic mining term paired with a disambiguating one - never a lone
generic word like "financiamiento", "inversión", "infraestructura",
"empresa" or a province name.
"""

import re

# Each mineral/phrase must match as a whole word/phrase (word-boundary
# regex), not merely as a substring - otherwise "oro" would match inside
# "incorporó" or "deterioro". This alone matters as much as the keyword
# list itself for keeping the filter strict.
MINING_KEYWORDS = [
    # Minerals/commodities - unambiguous on their own.
    "litio", "cobre", "oro", "plata", "uranio", "potasio", "boratos", "borato",
    "carbonato de litio", "zinc", "plomo", "molibdeno", "cianuro",
    # Explicit mining-specific multi-word phrases - never institutional
    # boilerplate, always about the mining activity itself.
    "proyecto minero", "empresa minera", "licitacion minera", "concesion minera",
    "yacimiento minero", "rigi minero", "inversion minera", "proveedor minero",
    "permiso ambiental minero", "adquisicion de proyecto minero",
    "infraestructura minera", "secretaria de mineria", "ministerio de mineria",
    "camara minera", "catastro minero", "actividad minera", "sector minero",
    "industria minera", "produccion minera",
    # Unambiguous mining-specific single term.
    "cateo",
]

# These are shared with other industries (oil & gas, telecom, geography in
# general) and are never sufficient alone - only counted when paired with a
# disambiguating mining term elsewhere in the same text.
_AMBIGUOUS_TERMS = ["exploracion", "explotacion", "concesion", "yacimiento", "salar"]
_DISAMBIGUATING_TERMS = [
    "mineria", "minero", "minera", "litio", "cobre", "oro", "plata", "uranio",
    "potasio", "borato", "zinc", "plomo",
]


def _normalize(text: str) -> str:
    text = (text or "").lower()
    replacements = str.maketrans("áéíóúñ", "aeioun")
    return text.translate(replacements)


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms)


def is_mining_relevant(text: str) -> bool:
    """True only for text with concrete evidence of Argentine mining.

    Generic words (financiamiento, inversión, infraestructura, empresa, a
    bare province name, or "minería" only as part of a combined ministry
    name) are never enough by themselves - see the module docstring.
    """
    normalized = _normalize(text)
    if _contains_any(normalized, MINING_KEYWORDS):
        return True
    if _contains_any(normalized, _AMBIGUOUS_TERMS) and _contains_any(normalized, _DISAMBIGUATING_TERMS):
        return True
    return False
