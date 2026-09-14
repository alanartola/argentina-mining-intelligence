from mining_intel.db.connection import get_connection
from mining_intel.news import pipeline
from mining_intel.news.sources.rss_source import AmbitoEnergiaSource, MineriaYDesarrolloSource, SaltaMineriaSource


def _rss(items: list[tuple[str, str, str, str]]) -> str:
    """items: list of (title, link, pubDate, description)."""
    entries = "".join(
        f"<item><title>{title}</title><link>{link}</link><pubDate>{pubdate}</pubDate>"
        f"<description><![CDATA[{description}]]></description></item>"
        for title, link, pubdate, description in items
    )
    return f"<rss version='2.0'><channel><title>Test</title>{entries}</channel></rss>"


MINING_ITEM = (
    "Nueva inversión minera en Salta impulsa proyecto de litio",
    "https://example.com/nota-mineria",
    "Sun, 13 Sep 2026 10:00:00 GMT",
    "La empresa anunció una ampliación de su planta de litio en Salta.",
)
NON_MINING_ITEM = (
    "El dólar blue cerró estable en la city porteña",
    "https://example.com/nota-dolar",
    "Sun, 13 Sep 2026 10:05:00 GMT",
    "Nota sobre el mercado cambiario y las reservas del Banco Central.",
)


def test_run_daily_filters_and_inserts_only_mining_relevant_items(tmp_path, monkeypatch):
    monkeypatch.setattr(MineriaYDesarrolloSource, "fetch", lambda self: _rss([MINING_ITEM, NON_MINING_ITEM]))
    monkeypatch.setattr(AmbitoEnergiaSource, "fetch", lambda self: _rss([]))
    monkeypatch.setattr(SaltaMineriaSource, "fetch", lambda self: _rss([]))

    db_path = tmp_path / "news_test.db"
    summary = pipeline.run_daily(db_path=db_path)

    assert summary["total_new_events"] == 1

    conn = get_connection(db_path)
    try:
        events = conn.execute("SELECT * FROM news_events").fetchall()
        sources = {row["internal_name"]: row["state"] for row in conn.execute("SELECT * FROM news_sources")}
    finally:
        conn.close()

    assert len(events) == 1
    assert "litio" in events[0]["title"].lower()
    assert sources["mineria_y_desarrollo"] == "ACTIVE"


def test_run_daily_does_not_reinsert_already_seen_items(tmp_path, monkeypatch):
    monkeypatch.setattr(MineriaYDesarrolloSource, "fetch", lambda self: _rss([MINING_ITEM]))
    monkeypatch.setattr(AmbitoEnergiaSource, "fetch", lambda self: _rss([]))
    monkeypatch.setattr(SaltaMineriaSource, "fetch", lambda self: _rss([]))

    db_path = tmp_path / "news_test_repeat.db"
    first = pipeline.run_daily(db_path=db_path)
    second = pipeline.run_daily(db_path=db_path)

    assert first["total_new_events"] == 1
    assert second["total_new_events"] == 0

    conn = get_connection(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) AS c FROM news_events").fetchone()["c"]
    finally:
        conn.close()
    assert count == 1


def test_run_daily_isolates_source_failures(tmp_path, monkeypatch):
    def _boom(self):
        raise RuntimeError("feed unreachable")

    monkeypatch.setattr(MineriaYDesarrolloSource, "fetch", _boom)
    monkeypatch.setattr(AmbitoEnergiaSource, "fetch", lambda self: _rss([MINING_ITEM]))
    monkeypatch.setattr(SaltaMineriaSource, "fetch", lambda self: _rss([]))

    db_path = tmp_path / "news_test_failure.db"
    summary = pipeline.run_daily(db_path=db_path)

    assert summary["sources"]["mineria_y_desarrollo"]["status"] == "error"
    assert summary["sources"]["ambito_energia"]["status"] == "ok"
    assert summary["total_new_events"] == 1

    conn = get_connection(db_path)
    try:
        state = conn.execute(
            "SELECT state, last_error FROM news_sources WHERE internal_name = ?", ("mineria_y_desarrollo",)
        ).fetchone()
    finally:
        conn.close()
    assert state["state"] == "FAILED"
    assert "feed unreachable" in state["last_error"]


def test_structured_sources_are_never_folded_by_shared_generic_url(tmp_path, monkeypatch):
    """Regression test: every SIACAM announcement shares the same static
    landing-page URL (it's not a per-article permalink like RSS items have).
    The cross-source fuzzy-fold must not treat that shared URL as evidence
    two different projects' announcements are "the same story" - each
    structured record has its own authoritative content_hash_seed and must
    get its own news_events row.
    """
    monkeypatch.setattr(MineriaYDesarrolloSource, "fetch", lambda self: _rss([]))
    monkeypatch.setattr(AmbitoEnergiaSource, "fetch", lambda self: _rss([]))
    monkeypatch.setattr(SaltaMineriaSource, "fetch", lambda self: _rss([]))

    db_path = tmp_path / "news_test_shared_url.db"
    shared_url = "https://www.argentina.gob.ar/economia/mineria/siacam"
    conn = get_connection(db_path)
    try:
        for i, (name, province) in enumerate([("Veladero", "San Juan"), ("Olaroz", "Jujuy")]):
            conn.execute(
                """
                INSERT INTO announcements
                    (external_id, source, name, company, province, mineral, stage,
                     investment_usd, announced_date, source_url, last_updated)
                VALUES (?, 'secretaria_mineria_siacam', ?, 'Empresa', ?, 'Litio', 'Ampliación',
                        100000000, '01/20 2020', ?, '2026-09-13T00:00:00')
                """,
                (f"ext-{i}", name, province, shared_url),
            )
        conn.commit()
    finally:
        conn.close()

    summary = pipeline.run_daily(db_path=db_path)
    assert summary["sources"]["secretaria_mineria_siacam"]["new_events"] == 2

    conn = get_connection(db_path)
    try:
        events = conn.execute(
            "SELECT title FROM news_events WHERE source_internal_name = 'secretaria_mineria_siacam'"
        ).fetchall()
    finally:
        conn.close()
    titles = {row["title"] for row in events}
    assert len(events) == 2
    assert any("Veladero" in t for t in titles)
    assert any("Olaroz" in t for t in titles)


def test_run_daily_registers_unsupported_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(MineriaYDesarrolloSource, "fetch", lambda self: _rss([]))
    monkeypatch.setattr(AmbitoEnergiaSource, "fetch", lambda self: _rss([]))
    monkeypatch.setattr(SaltaMineriaSource, "fetch", lambda self: _rss([]))

    db_path = tmp_path / "news_test_unsupported.db"
    pipeline.run_daily(db_path=db_path)

    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT state FROM news_sources WHERE internal_name = ?", ("boletin_oficial_nacional",)
        ).fetchone()
    finally:
        conn.close()
    assert row["state"] == "UNSUPPORTED"
