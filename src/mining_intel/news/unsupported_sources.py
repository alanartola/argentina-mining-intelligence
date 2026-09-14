"""Sources we investigated but do not run - never faked as connected.

Each entry is real research, not a placeholder: it's the reason we found
during evaluation for why the source can't be automated reliably right now.
`news.pipeline.run_daily` writes these into `news_sources` once so the
"Fuentes" view is complete and honest, without needing a scraper to run
just to populate a status row.
"""

UNSUPPORTED_SOURCES = [
    {
        "internal_name": "boletin_oficial_nacional",
        "display_name": "Boletín Oficial de la República Argentina",
        "state": "UNSUPPORTED",
        "reason": (
            "La búsqueda avanzada (busquedaAvanzada) se renderiza del lado del cliente; "
            "no encontramos una API JSON pública equivalente a la de CABA."
        ),
    },
    {
        "internal_name": "cnv_aif",
        "display_name": "CNV - Autopista de Información Financiera (Hechos Relevantes)",
        "state": "UNSUPPORTED",
        "reason": "No encontramos una API de datos abiertos pública para Hechos Relevantes.",
    },
    {
        "internal_name": "rigi_economia",
        "display_name": "RIGI (Ministerio de Economía)",
        "state": "UNSUPPORTED",
        "reason": (
            "El panel público solo expone conteos agregados por sector (ej. \"Minería: 12 "
            "proyectos aprobados\"), sin un listado por proyecto que permita detectar novedades puntuales."
        ),
    },
    {
        "internal_name": "catamarca_gobierno",
        "display_name": "Gobierno de Catamarca / Minería",
        "state": "UNSUPPORTED",
        "reason": "Los endpoints de feed probados devolvieron 403 (protección anti-bots); no se intentó evadir.",
    },
    {
        "internal_name": "jujuy_gobierno",
        "display_name": "Gobierno de Jujuy / Minería",
        "state": "MANUAL",
        "reason": "No se encontró un feed funcional en los dominios/rutas probadas en esta pasada.",
    },
    {
        "internal_name": "santa_cruz_gobierno",
        "display_name": "Gobierno de Santa Cruz / Minería",
        "state": "MANUAL",
        "reason": "No se encontró un feed funcional en los dominios/rutas probadas en esta pasada.",
    },
    {
        "internal_name": "mendoza_gobierno",
        "display_name": "Gobierno de Mendoza",
        "state": "MANUAL",
        "reason": "El feed RSS responde 200 pero no devolvió items durante la validación (0 registros).",
    },
    {
        "internal_name": "reuters",
        "display_name": "Reuters",
        "state": "UNSUPPORTED",
        "reason": "Contenido con acceso restringido; no se intenta evadir restricciones de acceso.",
    },
    {
        "internal_name": "bloomberg",
        "display_name": "Bloomberg",
        "state": "UNSUPPORTED",
        "reason": "Contenido con paywall; no se intenta evadir restricciones de acceso.",
    },
]
