CREATE TABLE IF NOT EXISTS projects (
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
    lat REAL,
    lon REAL,
    source_url TEXT,
    last_updated TEXT NOT NULL,
    UNIQUE (source, external_id)
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
