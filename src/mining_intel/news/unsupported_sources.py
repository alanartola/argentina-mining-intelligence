"""Sources we investigated but do not run - never faked as connected.

Each entry is real research, not a placeholder: it's the reason we found
during evaluation for why the source can't be automated reliably right now.
`news.pipeline.run_daily` writes these into `news_sources` once so the
"Fuentes" view is complete and honest, without needing a scraper to run
just to populate a status row.

Reuters and Bloomberg were explicitly de-prioritized for this iteration
(paywall/restricted access, not attempted). Boletín Oficial, CNV/AIF,
Jujuy, Santa Cruz and Mendoza moved OUT of this list into real
`NewsSource` implementations after re-investigation found a genuine,
stable way to consult each of them - see `news/sources/`.
"""

UNSUPPORTED_SOURCES = [
    {
        "internal_name": "ministerio_economia_rigi",
        "display_name": "Ministerio de Economía / RIGI",
        "state": "UNSUPPORTED",
        "automation_method": "MANUAL",
        "source_type": "Nacional",
        "reason": (
            "El panel público (argentina.gob.ar/economia/rigi) solo expone conteos agregados "
            "por sector (ej. \"Minería: 12 proyectos aprobados\") mediante un dashboard Drupal. "
            "El mapa interactivo de proyectos es un widget embebido complejo: revisamos las "
            "solicitudes de red y los scripts embebidos de la página y no encontramos un "
            "endpoint de datos por proyecto. Sin un listado por proyecto no hay forma de "
            "detectar novedades puntuales de forma reproducible."
        ),
    },
    {
        "internal_name": "catamarca_mineria",
        "display_name": "Gobierno de Catamarca",
        "state": "UNSUPPORTED",
        "automation_method": "MANUAL",
        "source_type": "Provincial",
        "reason": (
            "Probamos legislacionminera.catamarca.gob.ar y portal.catamarca.gob.ar "
            "directamente (no solo /feed): ambos devuelven 403 (protección anti-bots a nivel "
            "de infraestructura, no un endpoint puntual roto). No se intenta evadir la protección."
        ),
    },
    {
        "internal_name": "reuters",
        "display_name": "Reuters",
        "state": "UNSUPPORTED",
        "automation_method": "MANUAL",
        "source_type": "Medio",
        "reason": "Contenido con acceso restringido; no se intenta evadir restricciones de acceso.",
    },
    {
        "internal_name": "bloomberg",
        "display_name": "Bloomberg",
        "state": "UNSUPPORTED",
        "automation_method": "MANUAL",
        "source_type": "Medio",
        "reason": "Contenido con paywall; no se intenta evadir restricciones de acceso.",
    },
]
