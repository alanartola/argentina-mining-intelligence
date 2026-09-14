-- One row per unique real-world mining project, derived by
-- `processing.dedup` from `announcements`. Rebuilt from scratch on every
-- pipeline run, so ids are not stable across runs (fine for a single-user
-- local app - navigation always re-resolves project_id within one session).
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL UNIQUE,
    name TEXT,
    primary_province TEXT,
    mineral TEXT,
    stage TEXT,
    total_investment_usd REAL,
    announcement_count INTEGER NOT NULL,
    lat REAL,
    lon REAL,
    last_updated TEXT NOT NULL
);

-- One row per raw SIACAM investment-announcement record. Historical, never
-- collapsed - a real mining project shows up here multiple times as new
-- investment gets announced over the years. `project_id` links each
-- announcement to its deduplicated project above.
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    source TEXT NOT NULL,
    name TEXT,
    company TEXT,
    province TEXT,
    mineral TEXT,
    stage TEXT,
    investment_usd REAL,
    announced_date TEXT,
    source_url TEXT,
    last_updated TEXT NOT NULL,
    project_id INTEGER REFERENCES projects (id),
    UNIQUE (source, external_id)
);

-- Many-to-many: a multi-province project (e.g. "Salta/ Catamarca") gets one
-- row per real province here, so province-level counts are correct while
-- `projects` still has exactly one row for the project itself.
CREATE TABLE IF NOT EXISTS project_provinces (
    project_id INTEGER NOT NULL REFERENCES projects (id),
    province TEXT NOT NULL,
    UNIQUE (project_id, province)
);

CREATE TABLE IF NOT EXISTS tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    source TEXT NOT NULL,
    title TEXT,
    province TEXT,
    entity TEXT,
    publish_date TEXT,
    closing_date TEXT,
    budget_ars REAL,
    status TEXT,
    url TEXT,
    last_updated TEXT NOT NULL,
    UNIQUE (source, external_id)
);

CREATE TABLE IF NOT EXISTS scrape_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    records_found INTEGER,
    status TEXT NOT NULL,
    error TEXT
);

-- One row per detected mining-related novelty (news.pipeline.run_daily).
-- `content_hash` is the primary new-vs-seen guard: a run never re-inserts a
-- hash it already has, and only flips `status` to UPDATED when the fetched
-- text differs materially from what's stored. `project_key`/`province` are
-- only ever set when `news.link_project` is confident - never guessed.
--
-- `project_key` (not `projects.id`) on purpose: `projects` is fully
-- rebuilt on every `run_all()` call and its autoincrement ids are NOT
-- stable across rebuilds (see the comment on `projects` above), but a
-- persisted `news_events` row must keep pointing at the right project
-- indefinitely. `project_key` IS stable, so the current numeric id/name are
-- resolved by joining on it at read time (`db.queries.get_news_events_df`),
-- never trusted from a stored id.
CREATE TABLE IF NOT EXISTS news_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT,
    source_internal_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    publication_date TEXT,
    detected_at TEXT NOT NULL,
    updated_at TEXT,
    category TEXT NOT NULL,
    relevance TEXT NOT NULL,
    relevance_reason TEXT,
    province TEXT,
    project_key TEXT,
    company TEXT,
    mineral TEXT,
    official INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'NEW',
    additional_sources TEXT,
    raw_text TEXT
);

-- Status/health of every news source, including the ones we deliberately
-- don't run (UNSUPPORTED/MANUAL) - so the "Fuentes" view is honest about
-- what is and isn't actually connected, never silently omitting a source.
CREATE TABLE IF NOT EXISTS news_sources (
    internal_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    state TEXT NOT NULL,
    last_run_at TEXT,
    last_success_at TEXT,
    last_document_count INTEGER,
    last_error TEXT
);
