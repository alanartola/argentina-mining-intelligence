from mining_intel import pipeline
from mining_intel.db.connection import get_connection
from mining_intel.scrapers.boletin_san_juan import SanJuanTendersScraper
from mining_intel.scrapers.secretaria_mineria import SecretariaMineriaScraper

SAMPLE_CSV = (
    "Empresa,Año,Fecha ,Dólares,Mineral,Provincia,Concepto,Proyecto,Acumulado\n"
    "Test Co,2024,01/24,1000000,Litio,Salta,Construcción,Proyecto Test,1000000\n"
)

SAMPLE_HTML = """
<script>
var obj={"licitaciones":{"res":[{"ID_PUBLICACION":1,"F_PUBLICACION":"/Date(1700000000000)/","ESTADOS":"Proceso de Apertura","F_APERTURA":"/Date(1700100000000)/","TIPO":"LICITACION PUBLICA","INSTITUCION":"Ministerio de Minería","OBJETO":"Objeto de prueba","PRESUPUESTO":123456,"ORGANICA":"Ministerio de Minería"}]}};
</script>
"""


def test_pipeline_smoke(tmp_path, monkeypatch):
    monkeypatch.setattr(SecretariaMineriaScraper, "fetch", lambda self: SAMPLE_CSV)
    monkeypatch.setattr(SanJuanTendersScraper, "fetch", lambda self: SAMPLE_HTML)

    db_path = tmp_path / "test_mining.db"
    pipeline.run_all(db_path=db_path)

    conn = get_connection(db_path)
    try:
        announcements = conn.execute("SELECT * FROM announcements").fetchall()
        projects = conn.execute("SELECT * FROM projects").fetchall()
        project_provinces = conn.execute("SELECT * FROM project_provinces").fetchall()
        tenders = conn.execute("SELECT * FROM tenders").fetchall()
        runs = conn.execute("SELECT * FROM scrape_runs").fetchall()
    finally:
        conn.close()

    assert len(announcements) == 1
    assert announcements[0]["province"] == "Salta"
    assert announcements[0]["investment_usd"] == 1000000.0
    assert announcements[0]["project_id"] is not None

    assert len(projects) == 1
    assert projects[0]["name"] == "Proyecto Test"
    assert projects[0]["total_investment_usd"] == 1000000.0
    assert projects[0]["announcement_count"] == 1
    assert projects[0]["lat"] is not None
    assert announcements[0]["project_id"] == projects[0]["id"]

    assert len(project_provinces) == 1
    assert project_provinces[0]["province"] == "Salta"

    assert len(tenders) == 1
    assert tenders[0]["title"] == "Objeto de prueba"
    assert tenders[0]["province"] == "San Juan"

    assert len(runs) == 2
    assert all(run["status"] == "ok" for run in runs)


def test_pipeline_isolates_source_failures(tmp_path, monkeypatch):
    def _boom(self):
        raise RuntimeError("site is down")

    monkeypatch.setattr(SecretariaMineriaScraper, "fetch", _boom)
    monkeypatch.setattr(SanJuanTendersScraper, "fetch", lambda self: SAMPLE_HTML)

    db_path = tmp_path / "test_mining_partial.db"
    pipeline.run_all(db_path=db_path)

    conn = get_connection(db_path)
    try:
        runs = {row["source"]: row["status"] for row in conn.execute("SELECT * FROM scrape_runs")}
        tenders_count = conn.execute("SELECT COUNT(*) AS c FROM tenders").fetchone()["c"]
    finally:
        conn.close()

    assert runs["secretaria_mineria_siacam"] == "error"
    assert runs["san_juan_licitaciones_mineria"] == "ok"
    assert tenders_count == 1
