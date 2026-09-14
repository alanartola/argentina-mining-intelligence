import re
from datetime import datetime, timezone

import pandas as pd

from mining_intel.config import PROVINCE_ALIASES, PROVINCE_CENTROIDS


def normalize_province(raw_name: str) -> str:
    """Map a scraped province string to the canonical name used across the app."""
    name = (raw_name or "").strip()
    if not name:
        return ""

    alias = PROVINCE_ALIASES.get(name.lower())
    if alias:
        return alias

    for canonical in PROVINCE_CENTROIDS:
        if canonical.lower() == name.lower():
            return canonical

    return name


def get_province_centroid(province: str):
    """Look up a plot point for `province`, tolerating multi-province values
    like "Salta/ Catamarca" (some SIACAM projects straddle a provincial
    border) by falling back to the first province named.
    """
    centroid = PROVINCE_CENTROIDS.get(province)
    if centroid:
        return centroid

    first_part = re.split(r"[/,]", province)[0].strip()
    if first_part and first_part != province:
        return PROVINCE_CENTROIDS.get(normalize_province(first_part))
    return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_announcements(records: list[dict], source: str) -> pd.DataFrame:
    """Clean up raw investment-announcement records (one row per SIACAM CSV line).

    Deduplication into unique projects happens later, in
    `processing.dedup`, over the full `announcements` table - this function
    only normalizes each announcement on its own.
    """
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["province"] = df["province"].map(normalize_province)

    df["source"] = source
    df["last_updated"] = _now_iso()
    return df.drop_duplicates(subset=["source", "external_id"])


def normalize_tenders(records: list[dict], source: str) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    if "province" in df.columns:
        df["province"] = df["province"].map(normalize_province)

    df["source"] = source
    df["last_updated"] = _now_iso()
    return df.drop_duplicates(subset=["source", "external_id"])
