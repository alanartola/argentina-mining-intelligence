"""Shared visual identity for the Streamlit dashboard.

Pure presentation: theme CSS plus small HTML helpers (hero header, KPI
cards, badges). Nothing here touches data access or business logic - pages
still get their data from `mining_intel.db.queries` and just render it
through these helpers.
"""

import streamlit as st

from mining_intel.config import SOURCE_DISPLAY_NAMES

NAVY = "#16233E"
NAVY_LIGHT = "#22385F"
COPPER = "#B5651D"
GOLD = "#C9A227"
SLATE = "#5B6472"
BG = "#F4F5F7"
BORDER = "#E3E5EA"
TEXT = "#1B2233"
TEXT_MUTED = "#6B7280"

CHART_PRIMARY = NAVY_LIGHT
CHART_SECONDARY = COPPER

_BADGE_COLORS = {
    "navy": ("#E7ECF5", NAVY),
    "copper": ("#F5E6D8", "#8A4B14"),
    "gold": ("#F7EFD3", "#8A6D10"),
    "slate": ("#EEF0F2", SLATE),
    "green": ("#E3F3EA", "#1F7A4D"),
    "amber": ("#FBEFD9", "#8A6116"),
    "red": ("#FBE7E7", "#B23A3A"),
}

_STATUS_KIND = {
    "adjudicadas": "green",
    "adjudicada": "green",
    "proceso de adjudicación": "navy",
    "proceso de apertura": "navy",
    "desierta": "amber",
    "fracasada": "red",
    "desistido": "red",
}

_STAGE_KIND = {
    "construcción": "green",
    "ampliación": "navy",
    "exploración": "amber",
    "extensión vida útil": "navy",
    "mejora proceso": "copper",
}


def inject_base_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BG};
        }}
        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}
        html, body, .stApp, [class*="css"] {{
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
        }}

        /* Hero header */
        .ami-hero {{
            background: linear-gradient(135deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
            border-radius: 14px;
            padding: 1.9rem 2.2rem;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 1.2rem;
            margin-bottom: 1.8rem;
            box-shadow: 0 8px 20px rgba(22, 35, 62, 0.18);
        }}
        .ami-hero-icon {{
            font-size: 2.6rem;
            line-height: 1;
        }}
        .ami-hero-tag {{
            font-size: 0.7rem;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: {GOLD};
            font-weight: 700;
            margin-bottom: 0.3rem;
        }}
        .ami-hero-title {{
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            margin: 0;
        }}
        .ami-hero-subtitle {{
            font-size: 0.95rem;
            color: rgba(255, 255, 255, 0.78);
            margin-top: 0.3rem;
        }}

        /* KPI cards */
        .ami-kpi-accent {{
            height: 4px;
            margin: -1rem -1rem 0.85rem -1rem;
            border-radius: 8px 8px 0 0;
        }}
        .ami-kpi-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {TEXT_MUTED};
            font-weight: 600;
            margin-bottom: 0.4rem;
        }}
        .ami-kpi-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: {TEXT};
            line-height: 1.15;
        }}
        .ami-kpi-help {{
            font-size: 0.76rem;
            color: {TEXT_MUTED};
            margin-top: 0.3rem;
        }}

        /* Section headers */
        .ami-section {{
            border-top: 1px solid {BORDER};
            padding-top: 1.3rem;
            margin-top: 0.4rem;
        }}
        .ami-section-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {TEXT};
            margin-bottom: 0.15rem;
        }}
        .ami-section-caption {{
            font-size: 0.85rem;
            color: {TEXT_MUTED};
            margin-bottom: 0.9rem;
        }}

        /* Badges */
        .ami-badge-row {{
            margin: 0.2rem 0 1rem 0;
            line-height: 2.1;
        }}
        .ami-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            margin: 0.12rem 0.3rem 0.12rem 0;
            white-space: nowrap;
        }}

        /* Sidebar branding */
        .ami-sidebar-brand {{
            padding: 0.9rem 0.2rem 1.1rem 0.2rem;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 0.8rem;
        }}
        .ami-sidebar-brand-title {{
            font-size: 1.02rem;
            font-weight: 700;
            color: {TEXT};
        }}
        .ami-sidebar-brand-sub {{
            font-size: 0.74rem;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.15rem;
        }}

        /* Tabs */
        [data-testid="stTabs"] button[role="tab"] {{
            font-weight: 600;
            color: {TEXT_MUTED};
        }}
        [data-testid="stTabs"] button[aria-selected="true"] {{
            color: {NAVY} !important;
            border-bottom-color: {COPPER} !important;
        }}

        /* KPI "Ver detalle" action buttons: real controls, styled as a quiet link */
        div[data-testid="stButton"] button {{
            background: transparent;
            border: none;
            color: {NAVY_LIGHT};
            font-weight: 600;
            font-size: 0.82rem;
            padding: 0.2rem 0;
            justify-content: flex-start;
        }}
        div[data-testid="stButton"] button:hover {{
            color: {COPPER};
            text-decoration: underline;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="ami-sidebar-brand">
            <div class="ami-sidebar-brand-title">⛏️ Mining Intelligence</div>
            <div class="ami-sidebar-brand-sub">Argentina · Business Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, icon: str = "⛏️", eyebrow: str | None = None) -> None:
    eyebrow_html = f'<div class="ami-hero-tag">{eyebrow}</div>' if eyebrow else ""
    st.markdown(
        f"""
        <div class="ami-hero">
            <div class="ami-hero-icon">{icon}</div>
            <div>
                {eyebrow_html}
                <div class="ami-hero-title">{title}</div>
                <div class="ami-hero-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, caption: str | None = None) -> None:
    caption_html = f'<div class="ami-section-caption">{caption}</div>' if caption else ""
    st.markdown(
        f"""
        <div class="ami-section">
            <div class="ami-section-title">{title}</div>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_action_row(items: list[dict]) -> None:
    """Render a row of clickable KPI cards.

    Each item: {"label", "value", "help" (optional), "accent" (optional hex),
    "action_label", "target_page", "query_params" (optional dict), "key"}.
    The card itself is a native `st.container(border=True)` (a real
    Streamlit element, not styled HTML) with a real `st.button` inside that
    performs the navigation - clicking anywhere that isn't the button just
    doesn't navigate, which is why the button is always visible as the
    explicit "Ver detalle" action.
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        accent = item.get("accent", NAVY)
        help_html = f'<div class="ami-kpi-help">{item["help"]}</div>' if item.get("help") else ""
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="ami-kpi-accent" style="background:{accent}"></div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="ami-kpi-label">{item['label']}</div>
                    <div class="ami-kpi-value">{item['value']}</div>
                    {help_html}
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(item.get("action_label", "Ver detalle →"), key=item["key"], use_container_width=True):
                    st.switch_page(item["target_page"], query_params=item.get("query_params"))


def badge(text: str, kind: str = "slate") -> str:
    bg, color = _BADGE_COLORS.get(kind, _BADGE_COLORS["slate"])
    return f'<span class="ami-badge" style="background:{bg};color:{color}">{text}</span>'


def badge_row(badges_html: list[str]) -> None:
    if not badges_html:
        return
    st.markdown(f'<div class="ami-badge-row">{"".join(badges_html)}</div>', unsafe_allow_html=True)


def status_kind(status: str) -> str:
    return _STATUS_KIND.get((status or "").strip().lower(), "slate")


def stage_kind(stage: str) -> str:
    return _STAGE_KIND.get((stage or "").strip().lower(), "slate")


_RELEVANCE_KIND = {
    "critical": "red",
    "high": "copper",
    "medium": "navy",
    "low": "slate",
}


def relevance_kind(relevance: str) -> str:
    return _RELEVANCE_KIND.get((relevance or "").strip().lower(), "slate")


def source_label(internal_name: str) -> str:
    """Plain-text human label for a source slug - for use inside st.dataframe
    cells, which can't render the HTML link from `source_link`.
    """
    info = SOURCE_DISPLAY_NAMES.get(internal_name)
    return info["label"] if info else internal_name


def source_link(internal_name: str) -> str:
    """Human label for a scraper's internal SOURCE_NAME slug, linked to the
    source's URL when known. Never shows the raw slug to the user - falls
    back to it only if a future source hasn't been mapped yet, so nothing
    silently disappears.
    """
    info = SOURCE_DISPLAY_NAMES.get(internal_name)
    if not info:
        return internal_name
    return f'<a href="{info["url"]}" target="_blank">{info["label"]}</a>'
