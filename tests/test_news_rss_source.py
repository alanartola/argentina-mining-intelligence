from mining_intel.news.sources.rss_source import RssNewsSource

_VALID_RSS = (
    b"<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel>"
    b"<item><title>Nota de prueba</title><link>https://example.com/1</link>"
    b"<pubDate>Sun, 13 Sep 2026 10:00:00 GMT</pubDate>"
    b"<description>Resumen de prueba</description></item>"
    b"</channel></rss>"
)


def test_parses_a_well_formed_feed():
    items = RssNewsSource().parse(_VALID_RSS)
    assert len(items) == 1
    assert items[0]["title"] == "Nota de prueba"
    assert items[0]["url"] == "https://example.com/1"


def test_survives_stray_content_before_the_xml_declaration():
    """Regression: mendoza.gov.ar/prensa/feed/ was observed live to prepend
    a `<script>...</script>` snippet before the real `<?xml ...?><rss>`,
    which a strict XML parser rejects as "junk after document element".
    """
    junk_prefix = b"<script type='text/javascript'>var x = 1;</script>"
    items = RssNewsSource().parse(junk_prefix + _VALID_RSS)
    assert len(items) == 1
    assert items[0]["title"] == "Nota de prueba"


def test_feed_with_no_junk_is_unaffected():
    items = RssNewsSource().parse(_VALID_RSS)
    assert len(items) == 1
