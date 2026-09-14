import sys
from pathlib import Path

import pytest

# Streamlit adds `app/` to sys.path at runtime (it's the entrypoint script's
# directory), which is how pages import `style`. Tests need the same so
# `import style` works here too, without changing the app's structure.
APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


@pytest.fixture(autouse=True)
def _stub_news_source_network_calls(monkeypatch):
    """Safety net so no test ever makes a real HTTP request, even one that
    doesn't explicitly monkeypatch every source `news.pipeline.run_daily`
    now registers. A test exercising a specific source's real parsing logic
    calls `.parse(sample)` directly, which this doesn't touch.
    """
    from mining_intel.news.sources.boletin_oficial import BoletinOficialSource
    from mining_intel.news.sources.cnv_aif import CnvHechosRelevantesSource
    from mining_intel.news.sources.jujuy_mineria import JujuyMineriaSource
    from mining_intel.news.sources.rss_source import MendozaPrensaSource, SantaCruzMineriaSource

    empty_rss = b"<rss version='2.0'><channel></channel></rss>"

    monkeypatch.setattr(BoletinOficialSource, "fetch", lambda self: "<html></html>")
    monkeypatch.setattr(JujuyMineriaSource, "fetch", lambda self: "<html></html>")
    monkeypatch.setattr(SantaCruzMineriaSource, "fetch", lambda self: empty_rss)
    monkeypatch.setattr(MendozaPrensaSource, "fetch", lambda self: empty_rss)
    monkeypatch.setattr(
        CnvHechosRelevantesSource, "fetch", lambda self: {"html": "<html></html>", "known_companies": []}
    )
