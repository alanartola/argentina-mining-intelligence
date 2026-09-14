"""Rule-based, explainable category and relevance classification.

Every decision returns the rule that fired as plain text, stored verbatim
as `relevance_reason` - the point is that a person can always see *why* an
item got its classification, not just the label.
"""

_ACCENTS = str.maketrans("áéíóúñ", "aeioun")


def _normalize(text: str) -> str:
    return (text or "").lower().translate(_ACCENTS)


CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("TENDER", ["licitacion", "concurso de precios", "compulsa abreviada"]),
    ("RIGI", ["rigi"]),
    ("PERMIT", ["permiso ambiental", "declaracion de impacto ambiental", "dia ambiental"]),
    ("CONCESSION", ["concesion", "cateo"]),
    ("CONSTRUCTION", ["construccion", "obra civil"]),
    ("FINANCING", ["financiamiento", "emision de deuda", "bono verde", "credito sindicado"]),
    ("REGULATION", ["decreto", "resolucion", "normativa", "regulacion"]),
    ("COMPANY_UPDATE", ["hecho relevante", "comunicado", "directorio"]),
    ("PROJECT_UPDATE", ["avance del proyecto", "actualizacion del proyecto", "informe de avance"]),
    ("INVESTMENT", ["inversion de", "invertira", "anuncio una inversion", "anunciaron una inversion"]),
]


def infer_category(text: str, official: bool = False) -> str:
    normalized = _normalize(text)
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return category
    return "OFFICIAL_PUBLICATION" if official else "NEWS"


_CRITICAL_RULES: list[tuple[str, str]] = [
    ("adjudic", 'Menciona "adjudicación"'),
    ("aprob", 'Menciona una aprobación (posible aprobación RIGI o regulatoria)'),
    ("nuevo proyecto", 'Menciona un "nuevo proyecto" minero'),
    ("adquisicion de proyecto", "Menciona adquisición de un proyecto"),
    ("inicio de construccion", 'Menciona "inicio de construcción"'),
    ("cambio regulatorio", "Menciona un cambio regulatorio importante"),
    ("seleccion de epc", "Menciona selección de EPC/contratista principal"),
    ("contratista principal", "Menciona selección de contratista principal"),
]

_HIGH_RULES: list[tuple[str, str]] = [
    ("ampliacion", 'Menciona una "ampliación"'),
    ("permiso", "Menciona un permiso"),
    ("avance de construccion", "Menciona avance de construcción"),
    ("financiamiento", "Menciona financiamiento"),
    ("nuevo proveedor", "Menciona un nuevo proveedor relevante"),
    ("actualizacion material", "Menciona una actualización material del proyecto"),
]

_MEDIUM_RULES: list[tuple[str, str]] = [
    ("resultado de exploracion", "Menciona resultados de exploración"),
    ("resultados de exploracion", "Menciona resultados de exploración"),
    ("actualizacion corporativa", "Menciona una actualización corporativa"),
    ("declaracion", "Menciona declaraciones de una empresa/funcionario"),
]

# Investment-amount thresholds (USD) for the structured INVESTMENT category,
# where we have an exact number instead of just keywords.
_CRITICAL_INVESTMENT_USD = 100_000_000
_HIGH_INVESTMENT_USD = 10_000_000


def classify_relevance(text: str, category: str | None = None, investment_usd: float | None = None) -> tuple[str, str]:
    """Return (relevance, relevance_reason)."""
    if category == "INVESTMENT" and investment_usd:
        if investment_usd >= _CRITICAL_INVESTMENT_USD:
            return "CRITICAL", (
                f"Categoría INVESTMENT con monto USD {investment_usd:,.0f} "
                f"≥ USD {_CRITICAL_INVESTMENT_USD:,.0f} (regla: inversión material)"
            )
        if investment_usd >= _HIGH_INVESTMENT_USD:
            return "HIGH", (
                f"Categoría INVESTMENT con monto USD {investment_usd:,.0f} "
                f"≥ USD {_HIGH_INVESTMENT_USD:,.0f} (regla: actualización material del proyecto)"
            )

    if category == "TENDER":
        normalized = _normalize(text)
        if "adjudic" in normalized:
            return "CRITICAL", 'Licitación con estado de adjudicación (regla: "adjudicación")'
        return "HIGH", "Nueva licitación minera detectada (regla: licitación relevante)"

    normalized = _normalize(text)
    for keyword, reason in _CRITICAL_RULES:
        if keyword in normalized:
            return "CRITICAL", reason
    for keyword, reason in _HIGH_RULES:
        if keyword in normalized:
            return "HIGH", reason
    for keyword, reason in _MEDIUM_RULES:
        if keyword in normalized:
            return "MEDIUM", reason

    return "LOW", "No coincide con ninguna regla de relevancia crítica/alta/media (regla por defecto)"
