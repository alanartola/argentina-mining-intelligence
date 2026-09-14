from mining_intel.news.filters import is_mining_relevant


def test_mining_keyword_is_relevant():
    assert is_mining_relevant("La empresa anunció una nueva inversión en el proyecto de litio en Salta")
    assert is_mining_relevant("El yacimiento de cobre en San Juan avanza en su etapa de construcción")


def test_pure_oil_gas_is_excluded():
    assert not is_mining_relevant("YPF anunció una inversión en Vaca Muerta para producción de petróleo y gas")
    assert not is_mining_relevant("Nueva emisión de deuda de YPF para financiar exploración de hidrocarburos")


def test_unrelated_topics_are_excluded():
    assert not is_mining_relevant("El Banco Central subió la tasa de interés de los plazos fijos")
    assert not is_mining_relevant("La cosecha de soja bate récords en la campaña 2026")


def test_oil_gas_mentioned_alongside_mining_is_kept():
    text = "Argentina Energy Week: se debatió sobre minería, litio y también sobre Vaca Muerta y petróleo"
    assert is_mining_relevant(text)


def test_institutional_ministry_name_alone_is_not_enough():
    """Regression: a Salta government press release about a fintech meetup
    passed the old filter only because it was published under the letterhead
    "Ministerios de Producción y Minería" (the joint ministry's own name),
    with no actual mining content in the article.
    """
    text = (
        "Importante convocatoria de empresas y emprendedores en Fintech Meetups en Salta. "
        "El encuentro reunió a referentes de la industria fintech (financiamiento y tecnología) "
        "para abordar las transformaciones que la tecnología impulsa en las formas de pagar, "
        "cobrar, invertir y acceder al financiamiento, tanto en el ámbito público como privado. "
        "Impulsada por los Ministerios de Producción y Minería, y de Economía y Servicios Públicos."
    )
    assert not is_mining_relevant(text)


def test_generic_words_alone_are_not_sufficient():
    assert not is_mining_relevant("La empresa anunció un plan de financiamiento para su próxima inversión")
    assert not is_mining_relevant("Salta presentó un nuevo plan de infraestructura provincial")
    assert not is_mining_relevant("La empresa realizó una inversión importante en infraestructura")
    assert not is_mining_relevant("El gobierno de Salta anunció financiamiento para pequeñas empresas")


def test_concrete_mining_phrases_are_sufficient():
    assert is_mining_relevant("Se aprobó un nuevo proyecto minero en la provincia")
    assert is_mining_relevant("La empresa minera presentó su plan de producción anual")
    assert is_mining_relevant("Se otorgó una concesión minera en la zona cordillerana")
    assert is_mining_relevant("La compañía solicitó un cateo en la región")
    assert is_mining_relevant("El proyecto obtuvo la adhesión al RIGI minero")
    assert is_mining_relevant("Se publicó una licitación minera para la compra de equipos")
    assert is_mining_relevant("La Secretaría de Minería confirmó el avance del proyecto")


def test_mineral_substring_false_positives_are_avoided():
    """Word-boundary matching: "oro" must not match inside "incorporó"/"deterioro"."""
    assert not is_mining_relevant("La empresa incorporó nuevas tecnologías de gestión administrativa")
    assert not is_mining_relevant("El deterioro de la infraestructura vial preocupa a los vecinos")
