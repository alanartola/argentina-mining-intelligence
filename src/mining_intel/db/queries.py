import re

import pandas as pd

from mining_intel.db.connection import get_connection
from mining_intel.enrichment.profiles import get_profile
from mining_intel.processing.dedup import split_provinces


def get_announcements_df() -> pd.DataFrame:
    """Raw, one-row-per-SIACAM-record investment announcements (never deduplicated)."""
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM announcements ORDER BY investment_usd DESC", conn)
    finally:
        conn.close()


def get_projects_df() -> pd.DataFrame:
    """Deduplicated unique mining projects, one row each, with their provinces joined in."""
    conn = get_connection()
    try:
        return pd.read_sql_query(
            """
            SELECT p.*, GROUP_CONCAT(pp.province, ', ') AS provinces
            FROM projects p
            LEFT JOIN project_provinces pp ON pp.project_id = p.id
            GROUP BY p.id
            ORDER BY p.total_investment_usd DESC
            """,
            conn,
        )
    finally:
        conn.close()


def get_tenders_df() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM tenders ORDER BY publish_date DESC", conn)
    finally:
        conn.close()


def get_province_summary_df() -> pd.DataFrame:
    """Per real Argentine province: unique projects, announcements, investment,
    minerals present and tender count.

    A project/announcement spanning more than one province (e.g. "Salta/
    Catamarca") is counted toward *each* real province it touches - that is
    the whole point of `project_provinces` - while `projects` itself still
    has exactly one row for it.
    """
    empty = pd.DataFrame(
        columns=["province", "unique_projects", "minerals", "announcements", "investment_usd", "tenders"]
    )

    conn = get_connection()
    try:
        project_provinces = pd.read_sql_query("SELECT * FROM project_provinces", conn)
        projects = pd.read_sql_query("SELECT * FROM projects", conn)
        announcements = pd.read_sql_query("SELECT province, investment_usd FROM announcements", conn)
        tenders = pd.read_sql_query("SELECT province FROM tenders", conn)
    finally:
        conn.close()

    if project_provinces.empty:
        return empty

    proj_with_province = project_provinces.merge(projects, left_on="project_id", right_on="id")
    province_projects = (
        proj_with_province.groupby("province")
        .agg(
            unique_projects=("project_id", "nunique"),
            minerals=("mineral", lambda s: ", ".join(sorted({m for m in s if m}))),
        )
        .reset_index()
    )

    exploded_rows = [
        {"province": province, "investment_usd": row["investment_usd"] or 0}
        for _, row in announcements.iterrows()
        for province in split_provinces(row["province"])
    ]
    if exploded_rows:
        exploded = pd.DataFrame(exploded_rows)
        province_announcements = (
            exploded.groupby("province")
            .agg(announcements=("investment_usd", "count"), investment_usd=("investment_usd", "sum"))
            .reset_index()
        )
    else:
        province_announcements = pd.DataFrame(columns=["province", "announcements", "investment_usd"])

    if not tenders.empty:
        tender_rows = [
            {"province": province}
            for _, row in tenders.iterrows()
            for province in split_provinces(row["province"])
        ]
        province_tenders = pd.DataFrame(tender_rows).groupby("province").size().reset_index(name="tenders")
    else:
        province_tenders = pd.DataFrame(columns=["province", "tenders"])

    summary = province_projects.merge(province_announcements, on="province", how="left")
    summary = summary.merge(province_tenders, on="province", how="left")
    summary["announcements"] = summary["announcements"].fillna(0).astype(int)
    summary["investment_usd"] = summary["investment_usd"].fillna(0.0)
    summary["tenders"] = summary["tenders"].fillna(0).astype(int)
    return summary.sort_values("investment_usd", ascending=False).reset_index(drop=True)


def _announcement_sort_key(date_str: str) -> tuple[int, int]:
    """Best-effort chronological key for the free-text "MM/YY YYYY" dates
    SIACAM announcements carry - a plain string sort would wrongly order by
    month before year.
    """
    date_str = date_str or ""
    year_match = re.search(r"(\d{4})", date_str)
    month_match = re.match(r"(\d{2})/", date_str.strip())
    return (int(year_match.group(1)) if year_match else 0, int(month_match.group(1)) if month_match else 0)


def get_project_detail(project_id: int) -> dict | None:
    """Everything the ficha de proyecto needs for one project: its record,
    its real provinces, its full announcement history (chronological), and
    its curated profile if one exists (never fabricated - see
    `mining_intel.enrichment.profiles`).
    """
    conn = get_connection()
    try:
        project_row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if project_row is None:
            return None

        provinces = [
            row["province"]
            for row in conn.execute(
                "SELECT province FROM project_provinces WHERE project_id = ? ORDER BY province",
                (project_id,),
            ).fetchall()
        ]
        announcements = pd.read_sql_query(
            "SELECT * FROM announcements WHERE project_id = ?", conn, params=(project_id,)
        )
    finally:
        conn.close()

    if not announcements.empty:
        announcements = announcements.assign(
            _sort_key=announcements["announced_date"].map(_announcement_sort_key)
        ).sort_values("_sort_key").drop(columns="_sort_key")

    project = dict(project_row)
    project["provinces"] = provinces
    project["announcements"] = announcements
    project["profile"] = get_profile(project["project_key"])
    return project
