from mining_intel.news.link_project import extract_province, match_project

_PROJECTS = [("josemaria", "Josemaría"), ("veladero", "Veladero"), ("fenix", "Fenix")]


def test_match_project_finds_unambiguous_mention():
    assert match_project("Lundin avanza con la construcción de Josemaría en San Juan", _PROJECTS) == "josemaria"


def test_match_project_is_case_and_accent_insensitive():
    assert match_project("veladero amplia su produccion de oro", _PROJECTS) == "veladero"


def test_match_project_returns_none_when_no_project_named():
    assert match_project("El gobierno anunció medidas económicas generales", _PROJECTS) is None


def test_match_project_never_guesses_between_multiple_candidates():
    text = "Un resumen semanal menciona tanto a Josemaría como a Veladero y Fenix"
    assert match_project(text, _PROJECTS) is None


def test_extract_province_unambiguous():
    assert extract_province("El proyecto se ubica en la provincia de Salta") == "Salta"


def test_extract_province_none_when_absent():
    assert extract_province("Noticia sin mención de ninguna provincia") is None


def test_extract_province_none_when_multiple_mentioned():
    assert extract_province("El proyecto abarca Salta y Catamarca") is None
