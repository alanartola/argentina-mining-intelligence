from mining_intel.news.sources.jujuy_mineria import JujuyMineriaSource

_SAMPLE_HTML = """
<html><body>
<article class="row">
  <div class="col-5"><figure class="article-img"><a href="https://prensa.jujuy.gob.ar/mineria/nota-1">img</a></figure></div>
  <div class="col-7">
    <div class="article-title"><h2><a href="https://prensa.jujuy.gob.ar/mineria/nota-1" class="a-article-link">El Ministerio de Minería informa inscripciones 2026</a></h2></div>
    <div class="article-excerp"><a href="https://prensa.jujuy.gob.ar/mineria/nota-1"><p class="ignore-parser">Deberán inscribirse los productores mineros.</p></a></div>
  </div>
</article>
<article class="row">
  <div class="col-5"><figure class="article-img"><a href="https://prensa.jujuy.gob.ar/salud/nota-2">img</a></figure></div>
  <div class="col-7">
    <div class="article-title"><h2><a href="https://prensa.jujuy.gob.ar/salud/nota-2" class="a-article-link">Operativo de salud en Rinconadillas</a></h2></div>
    <div class="article-excerp"><a href="https://prensa.jujuy.gob.ar/salud/nota-2"><p class="ignore-parser">Atención médica gratuita para la comunidad.</p></a></div>
  </div>
</article>
</body></html>
"""


def test_parses_title_url_and_excerpt():
    items = JujuyMineriaSource().parse(_SAMPLE_HTML)
    assert len(items) == 2

    mining_item = next(i for i in items if "nota-1" in i["url"])
    assert mining_item["title"] == "El Ministerio de Minería informa inscripciones 2026"
    assert "productores mineros" in mining_item["summary_raw"]
    assert mining_item["official"] is True
    assert "category" not in mining_item


def test_non_mining_item_is_filtered_out_by_the_generic_filter():
    from mining_intel.news.filters import is_mining_relevant

    items = JujuyMineriaSource().parse(_SAMPLE_HTML)
    relevant_urls = [i["url"] for i in items if is_mining_relevant(f"{i['title']}. {i['summary_raw']}")]
    assert relevant_urls == ["https://prensa.jujuy.gob.ar/mineria/nota-1"]
