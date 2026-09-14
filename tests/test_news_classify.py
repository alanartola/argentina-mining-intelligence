from mining_intel.news.classify import classify_relevance, infer_category


def test_infer_category_tender():
    assert infer_category("Se publicó una nueva licitación para el Ministerio de Minería") == "TENDER"


def test_infer_category_rigi():
    assert infer_category("El proyecto obtuvo la aprobación del RIGI") == "RIGI"


def test_infer_category_defaults_to_news_or_official():
    assert infer_category("La empresa presentó resultados trimestrales", official=False) == "NEWS"
    assert infer_category("La provincia realizó un anuncio institucional", official=True) == "OFFICIAL_PUBLICATION"


def test_classify_relevance_critical_examples():
    level, reason = classify_relevance("El proyecto fue adjudicado tras el proceso de licitación")
    assert level == "CRITICAL"
    assert reason

    level, reason = classify_relevance("Se aprobó el nuevo proyecto minero en San Juan")
    assert level == "CRITICAL"
    assert reason


def test_classify_relevance_high_examples():
    level, reason = classify_relevance("La empresa anunció una ampliación de su planta de litio")
    assert level == "HIGH"
    assert reason


def test_classify_relevance_medium_examples():
    level, reason = classify_relevance("La compañía presentó los resultados de exploración del trimestre")
    assert level == "MEDIUM"
    assert reason


def test_classify_relevance_low_default():
    level, reason = classify_relevance("Artículo de opinión sobre la historia de la minería en Argentina")
    assert level == "LOW"
    assert reason


def test_classify_relevance_investment_amount_thresholds():
    level, _ = classify_relevance("Anuncio de inversión", category="INVESTMENT", investment_usd=500_000_000)
    assert level == "CRITICAL"

    level, _ = classify_relevance("Anuncio de inversión", category="INVESTMENT", investment_usd=20_000_000)
    assert level == "HIGH"


def test_classify_relevance_tender_adjudicated_is_critical():
    level, reason = classify_relevance("Licitación adjudicada al proveedor ganador", category="TENDER")
    assert level == "CRITICAL"
    assert "adjud" in reason.lower()
