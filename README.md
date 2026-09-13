# Argentina Mining Intelligence

MVP de inteligencia minera para Argentina: recolecta datos abiertos de proyectos, inversiones y licitaciones del sector minero, y los expone en un dashboard interactivo con mapa.

## Stack

- Python para scraping, procesamiento y análisis (pandas)
- SQLite como base de datos inicial, pensada para migrar a PostgreSQL/Supabase más adelante sin reescribir la lógica de negocio
- Streamlit + Folium para el dashboard y el mapa interactivo
- GitHub Actions para correr la actualización de datos automáticamente todos los días

## Fuentes de datos (v1)

- **Secretaría de Minería (SIACAM)** — Anuncios de Inversión en el Sector Minero, dataset abierto publicado en [datos.gob.ar](https://datos.gob.ar/dataset?tags=Miner%C3%ADa).
- **Portal Compras Públicas de San Juan** — licitaciones y contrataciones del Ministerio de Minería.

Agregar una fuente nueva (otra provincia, catastro minero, etc.) es un módulo nuevo en `src/mining_intel/scrapers/` que implementa la interfaz `BaseScraper` — no requiere tocar los scrapers existentes.

## Uso

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Traer/actualizar los datos
python scripts/run_update.py

# Levantar el dashboard
streamlit run app/Home.py
```

## Tests

```bash
pytest
```

## Estructura

```
src/mining_intel/   # scraping, normalización y acceso a datos
app/                # dashboard Streamlit (Home + páginas)
scripts/            # entrypoint CLI usado localmente y por GitHub Actions
data/mining.db      # SQLite, actualizado automáticamente todos los días vía Actions
```
