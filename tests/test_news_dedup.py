from mining_intel.news.dedup import content_hash, find_similar_event, normalize_title, title_similarity


def test_content_hash_is_stable_for_same_title_and_url():
    a = content_hash("Nuevo proyecto de litio en Salta", "https://example.com/nota-1")
    b = content_hash("Nuevo proyecto de litio en Salta", "https://example.com/nota-1")
    assert a == b


def test_content_hash_differs_for_different_url():
    a = content_hash("Nuevo proyecto de litio en Salta", "https://example.com/nota-1")
    b = content_hash("Nuevo proyecto de litio en Salta", "https://example.com/nota-2")
    assert a != b


def test_content_hash_uses_seed_when_given():
    a = content_hash("Título A", "https://a.com/1", seed="siacam-announcement:123")
    b = content_hash("Título B distinto", "https://b.com/2", seed="siacam-announcement:123")
    assert a == b


def test_normalize_title_is_case_and_accent_insensitive():
    assert normalize_title("Río Tinto invertirá en Salta") == normalize_title("rio tinto invertira en salta")


def test_title_similarity_detects_near_duplicates():
    a = "Rio Tinto invertirá USD 2.700 millones en Salta"
    b = "Rio Tinto invertira US$2.700 millones en la provincia de Salta"
    assert title_similarity(a, b) > 0.7


def test_find_similar_event_matches_by_url():
    existing = [{"id": 1, "title": "Nota original", "source_url": "https://example.com/x"}]
    match = find_similar_event("Otro título totalmente distinto", "https://example.com/x", existing)
    assert match is not None
    assert match["id"] == 1


def test_find_similar_event_matches_by_title_similarity():
    existing = [
        {
            "id": 5,
            "title": "Rio Tinto invertirá USD 2.700 millones en Salta para su planta de litio",
            "source_url": "https://siteA.com/nota",
        }
    ]
    match = find_similar_event(
        "Rio Tinto invertira US$2.700 millones en Salta para su planta de litio",
        "https://siteB.com/otra-nota",
        existing,
    )
    assert match is not None
    assert match["id"] == 5


def test_find_similar_event_returns_none_for_unrelated_items():
    existing = [{"id": 1, "title": "Fénix amplía su producción en Catamarca", "source_url": "https://a.com/1"}]
    match = find_similar_event("Nueva licitación en San Juan para seguros", "https://b.com/2", existing)
    assert match is None
