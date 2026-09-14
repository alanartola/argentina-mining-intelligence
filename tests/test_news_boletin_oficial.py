from mining_intel.news.sources.boletin_oficial import BoletinOficialSource

_SAMPLE_HTML = """
<html><body>
<div class="row"><div class="col-md-12">
  <a href="/detalleAviso/primera/100001/20260911">
    <div class="linea-aviso">
      <p class="item">SECRETARIA DE MINERIA </p>
      <p class="item-detalle"><small>Resolución 45/2026</small></p>
      <p class="item-detalle"><small>RESOL-2026-45-APN-SM - Apruébase la concesión minera del proyecto Litio Norte.</small></p>
    </div>
  </a>
</div></div>
<div class="row"><div class="col-md-12">
  <a href="/detalleAviso/primera/100002/20260911">
    <div class="linea-aviso">
      <p class="item">MINISTERIO DE EDUCACION </p>
      <p class="item-detalle"><small>Resolución 12/2026</small></p>
      <p class="item-detalle"><small>RESOL-2026-12-APN-ME - Convocatoria a becas educativas.</small></p>
    </div>
  </a>
</div></div>
</body></html>
"""


def test_parses_avisos_with_organismo_norma_and_description():
    items = BoletinOficialSource().parse(_SAMPLE_HTML)
    assert len(items) == 2

    mining_item = next(i for i in items if "100001" in i["content_hash_seed"])
    assert "SECRETARIA DE MINERIA" in mining_item["title"]
    assert "concesión minera" in mining_item["summary_raw"]
    assert mining_item["url"] == "https://www.boletinoficial.gob.ar/detalleAviso/primera/100001/20260911"
    assert mining_item["published_at"] == "2026-09-11"
    assert mining_item["official"] is True
    assert "category" not in mining_item  # goes through the generic mining filter, not pre-classified


def test_only_mining_relevant_aviso_survives_the_full_pipeline_filter():
    from mining_intel.news.filters import is_mining_relevant

    items = BoletinOficialSource().parse(_SAMPLE_HTML)
    relevant = [i for i in items if is_mining_relevant(f"{i['title']}. {i['summary_raw']}")]
    assert len(relevant) == 1
    assert "100001" in relevant[0]["content_hash_seed"]


def test_deduplicates_repeated_links_on_the_same_page():
    html = _SAMPLE_HTML + _SAMPLE_HTML  # simulate the id appearing twice
    items = BoletinOficialSource().parse(html)
    assert len(items) == 2
