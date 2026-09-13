import csv
import hashlib
import io

import requests

from mining_intel.config import REQUEST_TIMEOUT, SIACAM_INVESTMENTS_CSV_URL, USER_AGENT
from mining_intel.scrapers.base import BaseScraper


class SecretariaMineriaScraper(BaseScraper):
    """Anuncios de Inversión en el Sector Minero (SIACAM / Secretaría de Minería).

    Published as open data on datos.gob.ar (CKAN, organization
    "secretaria-de-mineria"); the CSV resource itself is served from
    mecon.gob.ar. Verified live on 2026-09-13 - columns as of that date:
    Empresa, Año, Fecha, Dólares, Mineral, Provincia, Concepto, Proyecto,
    Inversiones anunciadas desde dic-19 (acumulado).
    """

    SOURCE_NAME = "secretaria_mineria_siacam"
    TARGET_TABLE = "projects"

    def fetch(self) -> str:
        response = requests.get(
            SIACAM_INVESTMENTS_CSV_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response.encoding = "utf-8-sig"
        return response.text

    def parse(self, raw: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(raw))
        reader.fieldnames = [name.strip() for name in reader.fieldnames]

        records = []
        for row in reader:
            row = {key.strip(): (value or "").strip() for key, value in row.items()}

            company = row.get("Empresa", "")
            project = row.get("Proyecto", "")
            date = row.get("Fecha", "")
            year = row.get("Año", "")
            concept = row.get("Concepto", "")

            try:
                investment_usd = float(row.get("Dólares", "0") or 0)
            except ValueError:
                investment_usd = None

            external_id = hashlib.md5(
                f"{company}|{project}|{date}|{year}|{concept}".encode("utf-8")
            ).hexdigest()

            records.append(
                {
                    "external_id": external_id,
                    "name": project,
                    "company": company,
                    "province": row.get("Provincia", ""),
                    "mineral": row.get("Mineral", ""),
                    "stage": concept,
                    "investment_usd": investment_usd,
                    "announced_date": f"{date} {year}".strip(),
                    "source_url": "https://www.argentina.gob.ar/economia/mineria/siacam",
                }
            )
        return records
