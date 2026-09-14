"""Shared visual identity for the Streamlit dashboard.

Pure presentation: theme CSS plus small HTML helpers (masthead, hero, KPI
cards, news cards, badges). Nothing here touches data access or business
logic - pages still get their data from `mining_intel.db.queries` and just
render it through these helpers.
"""

import streamlit as st

from mining_intel.config import SOURCE_DISPLAY_NAMES

NAVY = "#101B31"
NAVY_LIGHT = "#1E3358"
COPPER = "#AD5D22"
GOLD = "#B8901F"
SLATE = "#5B6472"
BG = "#F3F4F7"
SURFACE = "#FFFFFF"
BORDER = "#E4E6EC"
TEXT = "#141B2C"
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

_RELEVANCE_KIND = {
    "critical": "red",
    "high": "copper",
    "medium": "navy",
    "low": "slate",
}

_RELEVANCE_LABEL = {
    "critical": "Crítica",
    "high": "Alta",
    "medium": "Media",
    "low": "Baja",
}

_CATEGORY_LABEL = {
    "INVESTMENT": "Inversión",
    "RIGI": "RIGI",
    "PERMIT": "Permiso",
    "CONCESSION": "Concesión",
    "CONSTRUCTION": "Construcción",
    "FINANCING": "Financiamiento",
    "REGULATION": "Regulatorio",
    "COMPANY_UPDATE": "Empresa",
    "PROJECT_UPDATE": "Proyecto",
    "TENDER": "Licitación",
    "OFFICIAL_PUBLICATION": "Oficial",
    "NEWS": "Noticia",
}


def inject_base_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500&display=swap');

        html, body, .stApp, [class*="css"] {{
            font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
        }}
        .stApp {{
            background-color: {BG};
        }}
        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1360px;
        }}
        header[data-testid="stHeader"] {{
            background: transparent;
        }}
        footer {{ visibility: hidden; height: 0; }}
        #MainMenu {{ visibility: hidden; }}
        h1, h2, h3 {{
            letter-spacing: -0.01em;
            color: {TEXT};
        }}
        .ami-num {{
            font-variant-numeric: tabular-nums;
        }}

        /* ---------------- Masthead (Home) ---------------- */
        .ami-masthead {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 1.5rem;
            flex-wrap: wrap;
            padding-bottom: 1.1rem;
            margin-bottom: 1.6rem;
            border-bottom: 3px solid {NAVY};
        }}
        .ami-masthead-eyebrow {{
            font-size: 0.72rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: {COPPER};
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        .ami-masthead-title {{
            font-size: 2.05rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: {TEXT};
            margin: 0;
            line-height: 1.1;
        }}
        .ami-masthead-meta {{
            text-align: right;
            font-size: 0.82rem;
            color: {TEXT_MUTED};
        }}
        .ami-masthead-meta strong {{
            color: {TEXT};
            font-weight: 600;
        }}

        /* ---------------- Hero (sub-pages) ---------------- */
        .ami-hero {{
            background: linear-gradient(135deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
            border-radius: 12px;
            padding: 1.5rem 1.9rem;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 1.1rem;
            margin-bottom: 1.7rem;
            box-shadow: 0 6px 16px rgba(16, 27, 49, 0.16);
        }}
        .ami-hero-icon {{
            font-size: 2.1rem;
            line-height: 1;
        }}
        .ami-hero-tag {{
            font-size: 0.68rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {GOLD};
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        .ami-hero-title {{
            font-size: 1.55rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            margin: 0;
        }}
        .ami-hero-subtitle {{
            font-size: 0.88rem;
            color: rgba(255, 255, 255, 0.78);
            margin-top: 0.2rem;
        }}

        /* ---------------- KPI cards ---------------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 10px !important;
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }}
        .ami-kpi-accent {{
            height: 3px;
            margin: -1rem -1rem 0.8rem -1rem;
            border-radius: 8px 8px 0 0;
        }}
        .ami-kpi-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {TEXT_MUTED};
            font-weight: 600;
            margin-bottom: 0.35rem;
        }}
        .ami-kpi-value {{
            font-size: 1.65rem;
            font-weight: 800;
            color: {TEXT};
            line-height: 1.15;
            font-variant-numeric: tabular-nums;
        }}
        .ami-kpi-help {{
            font-size: 0.74rem;
            color: {TEXT_MUTED};
            margin-top: 0.3rem;
        }}

        /* ---------------- Section headers ---------------- */
        .ami-section {{
            padding-left: 0.7rem;
            border-left: 3px solid {COPPER};
            margin-top: 0.3rem;
            margin-bottom: 0.9rem;
        }}
        .ami-section-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {TEXT};
            line-height: 1.3;
        }}
        .ami-section-caption {{
            font-size: 0.82rem;
            color: {TEXT_MUTED};
            margin-top: 0.1rem;
        }}

        /* ---------------- Badges ---------------- */
        .ami-badge-row {{
            margin: 0.2rem 0 1rem 0;
            line-height: 2.1;
        }}
        .ami-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            margin: 0.12rem 0.3rem 0.12rem 0;
            white-space: nowrap;
        }}

        /* ---------------- News brief cards ---------------- */
        .ami-news-card {{
            border-left: 4px solid {BORDER};
            padding: 0.15rem 0 0.15rem 1rem;
        }}
        .ami-news-card.critical {{ border-left-color: #B23A3A; }}
        .ami-news-card.high {{ border-left-color: {COPPER}; }}
        .ami-news-title {{
            font-size: 1.02rem;
            font-weight: 700;
            color: {TEXT};
            margin: 0.15rem 0 0.3rem 0;
            line-height: 1.35;
        }}
        .ami-news-title a {{
            color: {TEXT};
            text-decoration: none;
        }}
        .ami-news-title a:hover {{
            color: {COPPER};
            text-decoration: underline;
        }}
        .ami-news-meta {{
            font-size: 0.76rem;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.03em;
            font-weight: 600;
            margin-bottom: 0.45rem;
        }}
        .ami-news-summary {{
            font-size: 0.88rem;
            color: {TEXT};
            line-height: 1.5;
            margin-bottom: 0.4rem;
        }}
        .ami-news-link {{
            font-size: 0.8rem;
            font-weight: 600;
            color: {NAVY_LIGHT};
            text-decoration: none;
        }}
        .ami-news-link:hover {{
            color: {COPPER};
            text-decoration: underline;
        }}
        .ami-empty-note {{
            font-size: 0.88rem;
            color: {TEXT_MUTED};
            padding: 0.9rem 0;
        }}

        /* ---------------- Nav / module cards ---------------- */
        .ami-nav-icon {{
            font-size: 1.5rem;
            margin-bottom: 0.3rem;
        }}
        .ami-nav-title {{
            font-size: 0.94rem;
            font-weight: 700;
            color: {TEXT};
        }}
        .ami-nav-desc {{
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            margin-top: 0.15rem;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }}

        /* ---------------- Sidebar branding ---------------- */
        section[data-testid="stSidebar"] {{
            background-color: {SURFACE};
            border-right: 1px solid {BORDER};
        }}
        .ami-sidebar-brand {{
            padding: 0.85rem 0.2rem 1rem 0.2rem;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 0.6rem;
        }}
        .ami-sidebar-brand-title {{
            font-size: 1.0rem;
            font-weight: 800;
            color: {TEXT};
        }}
        .ami-sidebar-brand-sub {{
            font-size: 0.72rem;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.15rem;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {{
            border-radius: 8px;
            font-size: 0.86rem;
            font-weight: 500;
            color: {SLATE};
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {{
            background-color: {BG};
            color: {NAVY};
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: {NAVY};
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] * {{
            color: #FFFFFF !important;
        }}

        /* ---------------- Tabs / segmented control ---------------- */
        [data-testid="stTabs"] button[role="tab"] {{
            font-weight: 600;
            color: {TEXT_MUTED};
        }}
        [data-testid="stTabs"] button[aria-selected="true"] {{
            color: {NAVY} !important;
            border-bottom-color: {COPPER} !important;
        }}

        /* ---------------- Metrics ---------------- */
        [data-testid="stMetricValue"] {{
            font-weight: 800;
            color: {TEXT};
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: {TEXT_MUTED};
        }}

        /* KPI/nav "Ver detalle" action buttons: real controls, styled as a quiet link */
        div[data-testid="stButton"] button {{
            background: transparent;
            border: none;
            color: {NAVY_LIGHT};
            font-weight: 600;
            font-size: 0.8rem;
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


def masthead(title: str, eyebrow: str, meta_html: str = "") -> None:
    """Compact editorial header for the Home "Daily Brief" - deliberately
    not the gradient `hero()` box used on sub-pages, so Home reads as a
    briefing document rather than another module landing page.
    """
    meta_block = f'<div class="ami-masthead-meta">{meta_html}</div>' if meta_html else ""
    st.markdown(
        f"""
        <div class="ami-masthead">
            <div>
                <div class="ami-masthead-eyebrow">{eyebrow}</div>
                <div class="ami-masthead-title">{title}</div>
            </div>
            {meta_block}
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


def nav_grid(items: list[dict]) -> None:
    """Row of clickable module-access cards (icon, title, one-line
    description, "Abrir →" button) - replaces plain link/bullet lists for
    getting from Home into the rest of the app.

    Each item: {"icon", "title", "desc", "target_page", "key", "query_params" (optional)}.
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="ami-nav-icon">{item['icon']}</div>
                    <div class="ami-nav-title">{item['title']}</div>
                    <div class="ami-nav-desc">{item['desc']}</div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Abrir →", key=item["key"], use_container_width=True):
                    st.switch_page(item["target_page"], query_params=item.get("query_params"))


def relevance_label(relevance: str) -> str:
    return _RELEVANCE_LABEL.get((relevance or "").strip().lower(), relevance or "—")


def category_label(category: str) -> str:
    return _CATEGORY_LABEL.get((category or "").strip().upper(), category or "—")


def news_brief_card(
    title: str,
    url: str,
    source: str,
    date_text: str,
    summary: str,
    relevance: str,
    category: str,
) -> None:
    """One card in the Home "Lo más importante hoy" briefing list."""
    rel_key = (relevance or "").strip().lower()
    st.markdown(
        f"""
        <div class="ami-news-card {rel_key}">
            {badge(relevance_label(relevance), relevance_kind(relevance))}
            {badge(category_label(category), "slate")}
            <div class="ami-news-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="ami-news-meta">{source} · {date_text}</div>
            <div class="ami-news-summary">{summary}</div>
            <a class="ami-news-link" href="{url}" target="_blank">Leer nota completa →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
