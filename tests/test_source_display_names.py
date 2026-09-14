from style import source_label, source_link

from mining_intel.config import SOURCE_DISPLAY_NAMES


def test_known_slugs_map_to_human_labels():
    assert source_label("secretaria_mineria_siacam") == "Secretaría de Minería"
    assert source_label("san_juan_licitaciones_mineria") == "Ministerio de Minería de San Juan"


def test_source_link_never_shows_the_raw_slug_for_known_sources():
    html = source_link("secretaria_mineria_siacam")
    assert "secretaria_mineria_siacam" not in html
    assert "Secretaría de Minería" in html
    assert "href=" in html


def test_unknown_slug_falls_back_to_itself_instead_of_disappearing():
    assert source_label("un_slug_futuro_no_mapeado") == "un_slug_futuro_no_mapeado"


def test_display_names_config_has_label_and_url_for_every_entry():
    for slug, info in SOURCE_DISPLAY_NAMES.items():
        assert info.get("label"), f"missing label for {slug}"
        assert info.get("url"), f"missing url for {slug}"
