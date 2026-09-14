"""Collapse SIACAM investment announcements into unique mining projects.

The same real project (e.g. "Veladero") is announced repeatedly over the
years, often under slightly different company spellings ("Barrick Gold" vs
"Barrick Gold - Shandong Gold"). This module groups announcements that are
the same *project* while keeping every announcement row intact - dedup only
ever produces a `projects` view derived from `announcements`, it never
deletes or merges the underlying historical records.
"""

import re
import unicodedata
from collections import Counter

import pandas as pd

from mining_intel.processing.normalize import get_province_centroid, normalize_province

# Manual corrections for cases where the same project is spelled so
# differently across announcements that normalization alone can't match them
# (accents/case/whitespace are already handled by `normalize_project_key`).
# Empty for the current dataset - no such case was found - but kept as the
# extension point requested for "aliases si existen": add entries as
# {normalized_variant: canonical_normalized_key}.
PROJECT_KEY_ALIASES: dict[str, str] = {}


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_project_key(name: str) -> str | None:
    """Case/accent/whitespace/punctuation-insensitive identity key for a project name.

    Returns None for a blank name - callers must not group blank-name
    announcements together, since they represent unrelated, simply
    unnamed, announcements (see `_group_key`).
    """
    name = (name or "").strip()
    if not name:
        return None

    key = _strip_accents(name).lower()
    key = re.sub(r"[^a-z0-9]+", " ", key).strip()
    key = re.sub(r"\s+", " ", key)
    return PROJECT_KEY_ALIASES.get(key, key)


def split_provinces(raw_province: str) -> list[str]:
    """Split a combined value like "Salta/ Catamarca" into real provinces."""
    parts = re.split(r"[/,]", raw_province or "")
    provinces = [normalize_province(part) for part in parts]
    return [p for p in provinces if p]


def _group_key(row: pd.Series) -> str:
    key = normalize_project_key(row["name"])
    if key is None:
        # No project name in the source row: never merge with other unnamed
        # rows, each is its own singleton "project".
        return f"__unnamed__{row['external_id']}"
    return key


def _most_common(values: pd.Series):
    values = [v for v in values if v]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def _latest_stage(group: pd.DataFrame) -> str | None:
    with_dates = group.dropna(subset=["announced_date"])
    if with_dates.empty:
        return _most_common(group["stage"])
    # `announced_date` is a free-text "MM/YY YYYY" string; sort lexicographically
    # on the trailing 4-digit year, falling back to row order for same-year ties.
    with_dates = with_dates.copy()
    with_dates["_year"] = with_dates["announced_date"].str.extract(r"(\d{4})")
    with_dates = with_dates.sort_values("_year", kind="stable")
    return with_dates.iloc[-1]["stage"]


def build_projects(announcements_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Group `announcements_df` rows into unique projects.

    Returns (projects_df, project_provinces_df, external_id_to_project_key) -
    the last item lets the pipeline write `announcements.project_id` back
    once the `projects` rows have real ids.
    """
    if announcements_df.empty:
        return pd.DataFrame(), pd.DataFrame(), {}

    df = announcements_df.copy()
    df["_group_key"] = df.apply(_group_key, axis=1)

    project_rows = []
    province_rows = []
    external_id_to_key: dict[str, str] = {}

    for group_key, group in df.groupby("_group_key"):
        raw_names = [n for n in group["name"] if n and n.strip()]
        display_name = max(raw_names, key=len) if raw_names else (group.iloc[0]["company"] or "Sin nombre")

        provinces: list[str] = []
        for raw_province in group["province"]:
            for province in split_provinces(raw_province):
                if province not in provinces:
                    provinces.append(province)

        primary_province = _most_common(
            [p for raw_province in group["province"] for p in split_provinces(raw_province)]
        )
        centroid = get_province_centroid(primary_province) if primary_province else None

        project_rows.append(
            {
                "project_key": group_key,
                "name": display_name,
                "primary_province": primary_province,
                "mineral": _most_common(group["mineral"]),
                "stage": _latest_stage(group),
                "total_investment_usd": group["investment_usd"].fillna(0).sum(),
                "announcement_count": len(group),
                "lat": centroid[0] if centroid else None,
                "lon": centroid[1] if centroid else None,
            }
        )

        for province in provinces:
            province_rows.append({"project_key": group_key, "province": province})

        for external_id in group["external_id"]:
            external_id_to_key[external_id] = group_key

    projects_df = pd.DataFrame(project_rows)
    provinces_df = pd.DataFrame(province_rows)
    return projects_df, provinces_df, external_id_to_key
