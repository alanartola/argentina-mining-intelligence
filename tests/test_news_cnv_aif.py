from mining_intel.news.sources.cnv_aif import CnvHechosRelevantesSource, _infer_category, _parse_cnv_date

_SAMPLE_HTML = """
<html><body>
<div id="1a">
  <table>
    <thead><tr><th>FECHA</th><th>ENTIDAD</th><th>DESCRIPCIÓN</th><th>DOCUMENTO</th><th></th></tr></thead>
    <tbody>
      <tr>
        <td>12 sep. 2026 20:19</td>
        <td>BARRICK EXPLORACIONES ARGENTINA S.A..</td>
        <td>HECHO RELEVANTE - INVERSION EN PROYECTO VELADERO</td>
        <td>1001</td>
        <td><a href="https://aif2.cnv.gov.ar/Presentations/publicview/AAA-111">ver</a></td>
      </tr>
      <tr>
        <td>11 sep. 2026 18:00</td>
        <td>RIZOBACTER ARGENTINA S.A..</td>
        <td>INFORMACIÓN SOCIETARIA - CONVOCA ASAMBLEA</td>
        <td>1002</td>
        <td><a href="https://aif2.cnv.gov.ar/Presentations/publicview/BBB-222">ver</a></td>
      </tr>
    </tbody>
  </table>
</div>
</body></html>
"""


def test_only_rows_matching_known_companies_are_kept():
    source = CnvHechosRelevantesSource(conn=None)
    items = source.parse({"html": _SAMPLE_HTML, "known_companies": ["Barrick Gold"]})

    assert len(items) == 1
    assert "BARRICK" in items[0]["company"]
    assert items[0]["url"] == "https://aif2.cnv.gov.ar/Presentations/publicview/AAA-111"
    assert items[0]["content_hash_seed"] == "cnv-hecho:1001"
    assert items[0]["category"] == "INVESTMENT"


def test_no_known_companies_means_no_items_never_ingest_everything():
    source = CnvHechosRelevantesSource(conn=None)
    items = source.parse({"html": _SAMPLE_HTML, "known_companies": []})
    assert items == []


def test_unrelated_company_is_never_matched():
    source = CnvHechosRelevantesSource(conn=None)
    items = source.parse({"html": _SAMPLE_HTML, "known_companies": ["Ganfeng Lithium"]})
    assert items == []


def test_infer_category_examples():
    assert _infer_category("INFORMACIÓN SOCIETARIA - CONVOCA ASAMBLEA GENERAL") == "COMPANY_UPDATE"
    assert _infer_category("EMISIÓN DE OBLIGACIONES NEGOCIABLES") == "FINANCING"
    assert _infer_category("ADQUISICIÓN DE ACTIVOS MINEROS") == "ACQUISITION"
    assert _infer_category("ALGO SIN PALABRAS CLAVE CONOCIDAS") == "OTHER"


def test_parse_cnv_date():
    assert _parse_cnv_date("12 sep. 2026 20:19") == "2026-09-12T20:19:00"
    assert _parse_cnv_date("garbage") is None
