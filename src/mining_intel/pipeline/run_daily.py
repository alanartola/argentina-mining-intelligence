"""Single daily entrypoint for the whole app: `python -m mining_intel.pipeline.run_daily`.

One command, one run, everything the daily update needs:
1. refresh structured data - SIACAM announcements + San Juan tenders
   (`mining_intel.pipeline.run_all`)
2. rebuild deduplicated projects (part of `run_all`, via
   `mining_intel.processing.dedup`)
3. run the news monitor - fetch every source, keep only genuine mining
   content, deduplicate, classify relevance, link to projects/provinces,
   and save (`mining_intel.news.pipeline.run_daily`)

This replaces the earlier `scripts/run_update.py` + `scripts/run_daily_news.py`
pair as the one command GitHub Actions (and a human) should run for the
daily update - no more juggling multiple entrypoints.
"""

import logging

from mining_intel.news.pipeline import run_daily as run_news_daily
from mining_intel.pipeline import run_all


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    logging.info("Paso 1/2: actualizando datos estructurados (SIACAM, San Juan, proyectos)...")
    run_all()

    logging.info("Paso 2/2: ejecutando el monitor de novedades...")
    summary = run_news_daily()

    logging.info(
        "Fuentes consultadas: %d (exitosas: %d, fallidas: %d)",
        summary["sources_consulted"], summary["sources_ok"], summary["sources_failed"],
    )
    logging.info("Publicaciones procesadas: %d", summary["total_fetched"])
    logging.info("Descartadas por no ser minería: %d", summary["total_filtered_out"])
    logging.info("Duplicados descartados: %d", summary["total_duplicates"])
    logging.info("Novedades nuevas: %d", summary["total_new_events"])
    for internal_name, info in summary["sources"].items():
        logging.info("  %s: %s", internal_name, info)
    for error in summary["errors"]:
        logging.error("  error: %s", error)


if __name__ == "__main__":
    main()
