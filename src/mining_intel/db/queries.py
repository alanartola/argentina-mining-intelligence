import re

import pandas as pd

from mining_intel.db.connection import get_connection
from mining_intel.enrichment.profiles import get_profile
from mining_intel.news import dates, ranking
from mining_intel.news.dedup import normalize_title
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


def get_news_events_df() -> pd.DataFrame:
    """Detected mining-related novelties, most recently detected first.

    Ordered by `detected_at` (always an ISO timestamp we set ourselves)
    rather than `publication_date`, which arrives in inconsistent formats
    across sources (SIACAM's free-text "MM/YY YYYY" vs. RSS's ISO dates)
    and so can't be sorted reliably as a plain string.

    Joins on `projects.project_key` (stable) rather than trusting a stored
    numeric id - `projects.id` is reassigned on every pipeline rebuild, so
    resolving the current project id/name at read time is what keeps old
    news events correctly linked after `projects` gets rebuilt.
    """
    conn = get_connection()
    try:
        return pd.read_sql_query(
            """
            SELECT ne.*, p.id AS project_id, p.name AS project_name, ns.display_name AS source_display_name
            FROM news_events ne
            LEFT JOIN projects p ON p.project_key = ne.project_key
            LEFT JOIN news_sources ns ON ns.internal_name = ne.source_internal_name
            ORDER BY ne.detected_at DESC, ne.id DESC
            """,
            conn,
        )
    finally:
        conn.close()


def get_daily_briefing(limit: int = 3, hours: int = 24, max_fallback_hours: int = 24 * 7) -> pd.DataFrame:
    """Top `limit` most important mining-news events for the Home "Daily
    Brief" - not the latest `limit` events, the most *important* ones.

    Three filters, in order:
    1. Only CRITICAL/HIGH events qualify as "importante" - MEDIUM/LOW never
       fill out the count, matching the product requirement to show fewer
       than `limit` (even zero) rather than pad with lower-value items.
    2. Restricted by the event's own real-world date (`dates.parse_event_date`
       on `publication_date`, falling back to `detected_at` when it can't be
       parsed) to the last `hours` (default 24h). Filtering on `detected_at`
       alone would be wrong here: SIACAM's announcements dataset covers
       years of history, all inserted with today's `detected_at` the day
       that source was added, so a 2022 announcement would otherwise show up
       as "hoy" forever. If the `hours` window is empty - e.g. viewed a few
       hours after a run that landed just outside it - falls back to the
       most recent calendar day that has any qualifying event, capped at
       `max_fallback_hours` (default one week) so the brief still never
       surfaces a stale event as today's news - an empty brief is the
       correct result once a full week has passed with no CRITICAL/HIGH news.
    3. Ranked by `news.ranking.score_event`, keeping only the highest-scoring
       event per project (`project_key`, or per normalized title when an
       event isn't linked to a project) - several same-day filings about one
       project never crowd out everything else.
    """
    events = get_news_events_df()
    if events.empty:
        return events

    events = events[events["relevance"].isin(["CRITICAL", "HIGH"])]
    if events.empty:
        return events

    events = events.assign(
        detected_at_dt=pd.to_datetime(events["detected_at"], errors="coerce", utc=True),
        event_date_dt=dates.effective_date_series(events),
    )
    events = events.dropna(subset=["event_date_dt"])
    if events.empty:
        return events

    now = pd.Timestamp.now(tz="UTC")
    fallback_cutoff = now - pd.Timedelta(hours=max_fallback_hours)
    events = events[events["event_date_dt"] >= fallback_cutoff]
    if events.empty:
        return events

    cutoff = now - pd.Timedelta(hours=hours)
    window = events[events["event_date_dt"] >= cutoff]
    if window.empty:
        latest_date = events["event_date_dt"].dt.date.max()
        window = events[events["event_date_dt"].dt.date == latest_date]
    if window.empty:
        return window

    window = window.copy()
    window["score"] = window.apply(ranking.score_event, axis=1)
    window["_dedup_key"] = window["project_key"].fillna(window["title"].map(normalize_title))
    window = window.sort_values(["score", "event_date_dt"], ascending=[False, False])
    window = window.drop_duplicates("_dedup_key", keep="first")

    return window.head(limit).drop(columns=["_dedup_key"])


def get_news_sources_df() -> pd.DataFrame:
    """Health/status of every news source, including the ones we
    deliberately don't run (UNSUPPORTED/MANUAL) - see
    `mining_intel.news.unsupported_sources`.

    "última novedad detectada" isn't a stored column - it's computed here
    via MAX(news_events.detected_at) per source, so there's no extra write
    path for something fully derivable from `news_events`.
    """
    conn = get_connection()
    try:
        return pd.read_sql_query(
            """
            SELECT ns.*, latest.title AS last_new_event_title, latest.detected_at AS last_new_event_at
            FROM news_sources ns
            LEFT JOIN (
                SELECT ne.source_internal_name, ne.title, ne.detected_at
                FROM news_events ne
                INNER JOIN (
                    SELECT source_internal_name, MAX(detected_at) AS max_detected_at
                    FROM news_events
                    GROUP BY source_internal_name
                ) m ON m.source_internal_name = ne.source_internal_name AND m.max_detected_at = ne.detected_at
            ) latest ON latest.source_internal_name = ns.internal_name
            ORDER BY ns.display_name
            """,
            conn,
        )
    finally:
        conn.close()
