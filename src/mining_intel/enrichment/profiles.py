"""Hand-curated, source-cited descriptive profiles for a handful of projects.

This is NOT a scraper: SIACAM and the provincial procurement portal only
publish structured figures (company, amount, province, stage), never a
narrative description of what a project is. To show the "ficha de proyecto"
working with real content - without inventing anything - each entry below
was written from real, cited sources (official provincial mining portals,
company/industry press) checked on `retrieved_at`. Every fact stated in a
`summary` is attributable to one of that entry's `sources`.

Any project NOT listed here has no curated profile: the UI must show the
literal fallback "Información descriptiva pendiente de incorporar." rather
than inventing one - see `get_profile`.

Keyed by `processing.dedup.normalize_project_key(name)` so a profile stays
attached to its project regardless of exactly which raw-name spelling the
dedup step picked as the display name.
"""

from mining_intel.processing.dedup import normalize_project_key

_RETRIEVED_AT = "2026-09-13"

_RAW_PROFILES = {
    "Josemaría": {
        "summary": (
            "Josemaría es un yacimiento de cobre, oro y plata ubicado en el departamento de "
            "Iglesia, San Juan, a unos 475 km de la capital provincial y próximo al límite con "
            "Chile. Es desarrollado por Lundin Mining junto con BHP como socio, y se encuentra "
            "en etapa de construcción tras obtener la Declaración de Impacto Ambiental para su "
            "corredor vial y su interconexión eléctrica en alta tensión. Según estimaciones de "
            "la empresa, la vida útil del yacimiento ronda los 19 años, con el cobre como "
            "principal producto y oro y plata como subproductos."
        ),
        "department_locality": "Departamento Iglesia, San Juan (extremo noroeste de la provincia, cercano al límite con Chile)",
        "owner": "Lundin Mining (vía subsidiaria local)",
        "operator": "Lundin Mining",
        "partners": ["BHP"],
        "contractors": [],
        "sources": [
            {
                "name": "Gobierno de San Juan - Secretaría de Estado de Minería (sisanjuan.gob.ar)",
                "url": "https://sisanjuan.gob.ar/mineria/2021-02-21/29741-proyecto-josemaria-el-emprendimiento-que-revolucionara-la-mineria-en-san-juan",
                "retrieved_at": _RETRIEVED_AT,
            },
            {
                "name": "Ámbito Financiero",
                "url": "https://www.ambito.com/energia/san-juan-josemaria-obtuvo-nuevo-hito-la-construccion-del-proyecto-cobre-oro-y-plata-n6097995",
                "retrieved_at": _RETRIEVED_AT,
            },
        ],
    },
    "Veladero": {
        "summary": (
            "Veladero es una mina de oro y plata en producción, ubicada en el departamento de "
            "Iglesia, San Juan, a gran altitud (entre 4.000 y 4.850 msnm). Es operada "
            "conjuntamente por Barrick y Shandong Gold Mining, socios en partes iguales desde "
            "que la minera china adquirió el 50% en abril de 2017. En 2025 ambas empresas "
            "anunciaron una inversión de USD 400 millones bajo el régimen RIGI para ampliar la "
            "capacidad de acopio y tratamiento de mineral, con el objetivo de sumar 1,6 millones "
            "de onzas de oro adicionales entre 2025 y 2028. La operación emplea a unas 3.800 "
            "personas, el 91% residentes de San Juan."
        ),
        "department_locality": "Departamento Iglesia, San Juan (4.000-4.850 msnm, ~374 km al noroeste de la capital provincial)",
        "owner": "Barrick / Shandong Gold Mining (sociedad 50/50 desde 2017)",
        "operator": "Barrick (operación conjunta con Shandong Gold)",
        "partners": ["Shandong Gold Mining"],
        "contractors": [],
        "sources": [
            {
                "name": "Ámbito Financiero",
                "url": "https://www.ambito.com/energia/barrick-shandong-gold-presento-un-rigi-us400-millones-ampliar-la-mina-oro-veladero-n6178022",
                "retrieved_at": _RETRIEVED_AT,
            },
            {
                "name": "Tiempo de San Juan",
                "url": "https://www.tiempodesanjuan.com/mineria/como-la-mina-sanjuanina-veladero-ayudo-barrick-tener-mayor-produccion-oro-n429986",
                "retrieved_at": _RETRIEVED_AT,
            },
        ],
    },
    "Fenix": {
        "summary": (
            "Fénix es la operación de litio más grande y antigua de Argentina, ubicada en el "
            "Salar del Hombre Muerto, departamento Antofagasta de la Sierra, Catamarca, a unos "
            "4.000 msnm. Produce cloruro y carbonato de litio desde 1998. Los anuncios de "
            "inversión de 2021-2022 fueron realizados por Livent, empresa que en 2023 se "
            "fusionó con la australiana Allkem para formar Arcadium Lithium, actual responsable "
            "del proyecto. Según prensa especializada, un acuerdo de expansión busca llevar la "
            "producción de 11.000 a 40.000 toneladas anuales de litio."
        ),
        "department_locality": "Salar del Hombre Muerto, departamento Antofagasta de la Sierra, Catamarca (el salar es compartido con Salta)",
        "owner": "Arcadium Lithium (Livent hasta la fusión con Allkem en 2023)",
        "operator": "Arcadium Lithium",
        "partners": [],
        "contractors": [],
        "sources": [
            {
                "name": "Infobae",
                "url": "https://www.infobae.com/economia/2024/09/09/viaje-al-corazon-de-fenix-en-el-salar-del-hombre-muerto-asi-funciona-la-operacion-de-litio-mas-grande-de-la-argentina/",
                "retrieved_at": _RETRIEVED_AT,
            },
        ],
    },
    "Centenario Ratones": {
        "summary": (
            "Centenario Ratones es la primera planta de litio de Salta, ubicada en el salar "
            "homónimo del departamento Los Andes, a más de 3.800 msnm y unos 290 km al oeste de "
            "la ciudad de Salta. Es desarrollada por Eramine Sudamérica, subsidiaria del grupo "
            "francés Eramet (50,1%), en sociedad con la empresa china Tsingshan (49,9%). Tiene "
            "una capacidad estimada de 24.000 toneladas anuales de carbonato de litio y en 2025 "
            "realizó sus primeras exportaciones."
        ),
        "department_locality": "Salar Centenario Ratones, departamento Los Andes, Salta (~290 km al oeste de la ciudad de Salta)",
        "owner": "Eramet (50,1%) / Tsingshan (49,9%), vía Eramine Sudamérica",
        "operator": "Eramine Sudamérica",
        "partners": ["Tsingshan"],
        "contractors": [],
        "sources": [
            {
                "name": "Ministerio de Producción y Minería de Salta",
                "url": "https://produccionsalta.gob.ar/proyecto-centenario-ratones-salta-comenzara-a-exportar-litio-en-2025/",
                "retrieved_at": _RETRIEVED_AT,
            },
            {
                "name": "Rumbo Minero",
                "url": "https://www.rumbominero.com/argentina/eramet-nueva-planta-de-litio-centenario-ratones/",
                "retrieved_at": _RETRIEVED_AT,
            },
        ],
    },
    "Salar del Rincón": {
        "summary": (
            "Salar del Rincón (proyecto \"Rincón\") es un desarrollo de litio por extracción "
            "directa (DLE) de Rio Tinto en la puna salteña, cerca de Tolar Grande. La compañía "
            "adquirió Rincón Mining Pty Ltd en marzo de 2022 por USD 825 millones y prevé una "
            "inversión cercana a los USD 2.700 millones para una planta con capacidad de 53.000 "
            "toneladas anuales de carbonato de litio grado batería. Una primera etapa, "
            "\"Rincón 3000\", comenzó a producir 3.000 toneladas anuales hacia fines de 2024, y "
            "el proyecto solicitó su adhesión al régimen RIGI para la etapa de planta comercial."
        ),
        "department_locality": "Puna salteña, zona del Salar del Rincón cercana a Tolar Grande (departamento no confirmado en las fuentes consultadas)",
        "owner": "Rio Tinto (vía Rincón Mining Pty Ltd, adquirida en marzo de 2022)",
        "operator": "Rio Tinto",
        "partners": [],
        "contractors": [],
        "sources": [
            {
                "name": "Ámbito Financiero",
                "url": "https://www.ambito.com/energia/rio-tinto-pidio-la-adhesion-al-rigi-su-proyecto-litio-el-salar-del-rincon-n6118045",
                "retrieved_at": _RETRIEVED_AT,
            },
            {
                "name": "Ministerio de Producción y Minería de Salta",
                "url": "https://produccionsalta.gob.ar/rio-tinto-confirmo-la-intencion-de-construir-una-planta-de-carbonato-de-litio-en-salta-con-una-inversion-de-2-mil-millones-de-dolares/",
                "retrieved_at": _RETRIEVED_AT,
            },
        ],
    },
}

PROJECT_PROFILES: dict[str, dict] = {
    normalize_project_key(raw_name): profile for raw_name, profile in _RAW_PROFILES.items()
}


def get_profile(project_key: str) -> dict | None:
    return PROJECT_PROFILES.get(project_key)
