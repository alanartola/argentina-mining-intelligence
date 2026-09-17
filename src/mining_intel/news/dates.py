"""Best-effort parsing of an event's own real-world date, across the
mismatched formats different sources report it in - SIACAM's free-text
"MM/YY YYYY", ISO datetimes from RSS/CNV/Boletín, plain ISO dates from San
Juan tenders. Used to tell a genuinely new event from an old one merely
*seen* for the first time today: SIACAM's announcements dataset covers
years of history, all inserted with today's `detected_at` the day that
source was added, so using `detected_at` alone would show a 2022
announcement as "today's news" forever.
"""

import re

import pandas as pd

_SIACAM_RE = re.compile(r"^(\d{2})/\d{2}\s+(\d{4})$")


def parse_event_date(publication_date) -> pd.Timestamp | None:
    """The event's real-world date if `publication_date` can be parsed,
    else `None` - callers should fall back to `detected_at` in that case
    (sources like Jujuy's press page don't report a date at all).
    """
    if not publication_date:
        return None
    text = str(publication_date).strip()
    if not text:
        return None

    match = _SIACAM_RE.match(text)
    if match:
        month, year = match.groups()
        try:
            return pd.Timestamp(year=int(year), month=int(month), day=1, tz="UTC")
        except ValueError:
            return None

    parsed = pd.to_datetime(text, errors="coerce", utc=True)
    return None if pd.isna(parsed) else parsed


def effective_date_series(events: pd.DataFrame) -> pd.Series:
    """One timestamp per row of `get_news_events_df()`: the event's own
    parsed `publication_date` where available, else `detected_at` - the
    column every "is this recent" filter (daily brief, last-7-days feed)
    should use instead of `detected_at` alone.
    """
    published = events["publication_date"].map(parse_event_date)
    detected = pd.to_datetime(events["detected_at"], errors="coerce", utc=True)
    return published.where(published.notna(), detected)
