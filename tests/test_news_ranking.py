from mining_intel.news.ranking import score_event


def _event(**overrides):
    base = {
        "relevance": "LOW",
        "category": "NEWS",
        "official": False,
        "title": "",
        "summary": "",
    }
    base.update(overrides)
    return base


def test_critical_outranks_high():
    critical = score_event(_event(relevance="CRITICAL"))
    high = score_event(_event(relevance="HIGH"))
    assert critical > high


def test_investment_category_and_amount_add_weight():
    baseline = score_event(_event(relevance="CRITICAL", category="NEWS"))
    with_category = score_event(_event(relevance="CRITICAL", category="INVESTMENT"))
    with_amount = score_event(
        _event(relevance="CRITICAL", category="INVESTMENT", summary="La empresa invertira USD 500,000,000 en la planta")
    )
    assert with_category > baseline
    assert with_amount > with_category


def test_priority_topic_keywords_add_weight():
    plain = score_event(_event(relevance="HIGH", title="Actualización corporativa de la empresa"))
    litio = score_event(_event(relevance="HIGH", title="La empresa anunció una ampliación de su planta de litio"))
    assert litio > plain


def test_keyword_matching_respects_word_boundaries():
    # "oro" must not fire on a word that merely contains it as a substring.
    no_match = score_event(_event(relevance="LOW", title="El directorio incorporó un nuevo gerente"))
    match = score_event(_event(relevance="LOW", title="Comenzó la producción de oro en el yacimiento"))
    assert match > no_match


def test_official_source_adds_weight():
    unofficial = score_event(_event(relevance="MEDIUM", official=False))
    official = score_event(_event(relevance="MEDIUM", official=True))
    assert official > unofficial
