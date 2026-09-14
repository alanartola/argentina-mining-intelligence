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
