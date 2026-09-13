from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mining.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "db" / "schema.sql"

USER_AGENT = "argentina-mining-intelligence/0.1 (+https://github.com/alanartola/argentina-mining-intelligence)"
REQUEST_TIMEOUT = 30

# Secretaría de Minería (SIACAM) - Anuncios de Inversión en el Sector Minero.
# Publicado como dataset abierto en datos.gob.ar; el CSV se sirve desde mecon.gob.ar.
SIACAM_INVESTMENTS_CSV_URL = "https://www.mecon.gob.ar/dataset/Anuncios-de-inversion.csv"

# Portal Compras Públicas de San Juan - licitaciones del Ministerio de Minería.
SAN_JUAN_TENDERS_URL = "https://licitaciones.sanjuan.gob.ar/index.php"
SAN_JUAN_MINERIA_ORG_ID = "2524"

# Centroides aproximados por provincia, usados como fallback cuando una fuente
# no publica coordenadas propias para un proyecto/licitación.
PROVINCE_CENTROIDS = {
    "Buenos Aires": (-36.6769, -60.5588),
    "Catamarca": (-28.4696, -65.7852),
    "Chaco": (-26.9944, -60.6591),
    "Chubut": (-43.3002, -68.0591),
    "Ciudad Autónoma de Buenos Aires": (-34.6037, -58.3816),
    "Córdoba": (-32.1429, -64.3487),
    "Corrientes": (-28.4652, -58.8341),
    "Entre Ríos": (-31.9998, -59.5626),
    "Formosa": (-25.1810, -59.6906),
    "Jujuy": (-23.6509, -65.3986),
    "La Pampa": (-37.0000, -65.5000),
    "La Rioja": (-29.4342, -66.8551),
    "Mendoza": (-34.9011, -68.8300),
    "Misiones": (-27.0000, -55.0000),
    "Neuquén": (-38.5000, -70.0000),
    "Río Negro": (-40.5000, -66.9000),
    "Salta": (-24.7859, -65.4117),
    "San Juan": (-31.5375, -68.5364),
    "San Luis": (-33.3000, -66.3000),
    "Santa Cruz": (-49.0000, -70.0000),
    "Santa Fe": (-31.6333, -60.7000),
    "Santiago del Estero": (-27.7834, -64.2642),
    "Tierra del Fuego": (-54.0000, -68.5000),
    "Tucumán": (-26.8241, -65.2226),
}

# Variantes/alias encontradas en fuentes reales, mapeadas al nombre canónico
# usado como clave en PROVINCE_CENTROIDS.
PROVINCE_ALIASES = {
    "caba": "Ciudad Autónoma de Buenos Aires",
    "capital federal": "Ciudad Autónoma de Buenos Aires",
    "bs as": "Buenos Aires",
    "bs. as.": "Buenos Aires",
    "tdf": "Tierra del Fuego",
    "rio negro": "Río Negro",
}
