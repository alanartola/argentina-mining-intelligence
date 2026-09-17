import pandas as pd

from mining_intel.news.dates import effective_date_series, parse_event_date


def test_parses_siacam_month_year_format():
    parsed = parse_event_date("04/23 2023")
    assert parsed == pd.Timestamp(2023, 4, 1, tz="UTC")


def test_parses_iso_datetime():
    parsed = parse_event_date("2026-09-15T22:31:21+00:00")
    assert parsed == pd.Timestamp("2026-09-15T22:31:21", tz="UTC")


def test_parses_plain_iso_date():
    assert parse_event_date("2026-09-15") == pd.Timestamp(2026, 9, 15, tz="UTC")


def test_returns_none_for_missing_or_unparseable():
    assert parse_event_date(None) is None
    assert parse_event_date("") is None
    assert parse_event_date("not a date") is None


def test_effective_date_series_prefers_publication_date_over_detected_at():
    events = pd.DataFrame(
        {
            "publication_date": ["04/23 2023", None, "not a date"],
            "detected_at": [
                "2026-09-14T02:01:12+00:00",
                "2026-09-14T02:01:12+00:00",
                "2026-09-14T02:01:12+00:00",
            ],
        }
    )
    result = effective_date_series(events)
    assert result.iloc[0] == pd.Timestamp(2023, 4, 1, tz="UTC")
    assert result.iloc[1] == pd.Timestamp("2026-09-14T02:01:12", tz="UTC")
    assert result.iloc[2] == pd.Timestamp("2026-09-14T02:01:12", tz="UTC")
