from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from mining_intel.db.queries import (
    get_announcements_df,
    get_daily_briefing,
    get_projects_df,
    get_province_summary_df,
    get_tenders_df,
)
from style import (
    CHART_PRIMARY,
    CHART_SECONDARY,
    GOLD,
    NAVY,
    inject_base_styles,
    kpi_action_row,
    masthead,
    nav_grid,
    news_brief_card,
    section_header,
    sidebar_brand,
)

st.set_page_config(page_title="Argentina Mining Intelligence", page_icon="⛏️", layout="wide")

inject_base_styles()
sidebar_brand()

_TODAY = datetime.now(timezone.utc)
_DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
_fecha_larga = f"{_DIAS[_TODAY.weekday()].capitalize()} {_TODAY.day} de {_MESES[_TODAY.month]} de {_TODAY.year}"

masthead(
    title="Argentina Mining Intelligence — Daily Brief",
    eyebrow="Panel ejecutivo · Sector minero argentino",
    meta_html=f"{_fecha_larga}<br><strong>Actualizado</strong> {_TODAY.strftime('%H:%M UTC')}",
)

announcements = get_announcements_df()
projects = get_projects_df()
provinces_summary = get_province_summary_df()
tenders = get_tenders_df()
briefing = get_daily_briefing(limit=3)

total_usd = announcements["investment_usd"].sum() if not announcements.empty else 0
n_provinces = provinces_summary["province"].nunique() if not provinces_summary.empty else 0

PROYECTOS_PAGE = "pages/2_Proyectos_y_Licitaciones.py"
PROVINCIAS_PAGE = "pages/3_Provincias.py"
MAPA_PAGE = "pages/1_Mapa.py"
NOVEDADES_PAGE = "pages/5_Novedades.py"
FUENTES_PAGE = "pages/6_Fuentes.py"

kpi_action_row(
    [
        {
            "label": "Inversión anunciada",
            "value": f"USD {total_usd:,.0f}",
            "help": "Acumulado histórico de anuncios registrados",
            "accent": GOLD,
            "key": "kpi_investment",
            "target_page": PROYECTOS_PAGE,
            "query_params": {"view": "proyectos"},
        },
        {
            "label": "Proyectos mineros",
            "value": f"{len(projects):,}",
            "help": f"{len(announcements):,} anuncios históricos, sin deduplicar",
            "accent": NAVY,
            "key": "kpi_projects",
            "target_page": PROYECTOS_PAGE,
            "query_params": {"view": "proyectos"},
        },
        {
            "label": "Provincias con proyectos",
            "value": f"{n_provinces}",
            "help": "Provincias reales con actividad minera",
            "accent": CHART_PRIMARY,
            "key": "kpi_provinces",
            "target_page": PROVINCIAS_PAGE,
        },
        {
            "label": "Licitaciones registradas",
            "value": f"{len(tenders):,}",
            "help": "Compras y contrataciones mineras",
            "accent": CHART_SECONDARY,
            "key": "kpi_tenders",
            "target_page": PROYECTOS_PAGE,
            "query_params": {"view": "licitaciones"},
        },
    ]
)


def _format_event_date(publication_date, detected_at_dt) -> str:
    if publication_date:
        parsed = pd.to_datetime(publication_date, errors="coerce", utc=True)
        if pd.notna(parsed):
            return parsed.strftime("%d/%m/%Y")
        return str(publication_date)
    return detected_at_dt.strftime("%d/%m/%Y") if pd.notna(detected_at_dt) else "Fecha no disponible"


def _short_summary(text: str, limit: int = 170) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


section_header(
    "Lo más importante hoy",
    "Selección automática de las noticias con mayor impacto sobre el sector minero argentino, no simplemente las últimas publicadas.",
)

if briefing.empty:
    st.markdown(
        '<div class="ami-empty-note">No se detectaron novedades de alto impacto en las últimas 24 horas.</div>',
        unsafe_allow_html=True,
    )
else:
    for _, event in briefing.iterrows():
        with st.container(border=True):
            news_brief_card(
                title=event["title"],
                url=event["source_url"],
                source=event["source_display_name"] or event["source_internal_name"],
                date_text=_format_event_date(event["publication_date"], event["detected_at_dt"]),
                summary=_short_summary(event["summary"]),
                relevance=event["relevance"],
                category=event["category"],
            )

if not announcements.empty:
    section_header("Inversión anunciada", "Acumulado histórico en USD, de mayor a menor.")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.caption("Por provincia")
        by_province = provinces_summary.set_index("province")["investment_usd"].sort_values(ascending=False)
        st.bar_chart(by_province, color=CHART_PRIMARY, height=320)
    with chart_col2:
        st.caption("Por mineral")
        by_mineral = announcements.groupby("mineral")["investment_usd"].sum().sort_values(ascending=False)
        st.bar_chart(by_mineral, color=CHART_SECONDARY, height=320)
else:
    st.info("Todavía no hay datos cargados. Corré `python scripts/run_update.py` para poblar la base.")

section_header("Explorar")
nav_grid(
    [
        {
            "icon": "🗺️",
            "title": "Mapa",
            "desc": "Proyectos y licitaciones en el territorio.",
            "target_page": MAPA_PAGE,
            "key": "nav_mapa",
        },
        {
            "icon": "📋",
            "title": "Proyectos y licitaciones",
            "desc": "Detalle filtrable de inversiones y compras.",
            "target_page": PROYECTOS_PAGE,
            "key": "nav_proyectos",
        },
        {
            "icon": "📍",
            "title": "Provincias",
            "desc": "Actividad minera por jurisdicción.",
            "target_page": PROVINCIAS_PAGE,
            "key": "nav_provincias",
        },
        {
            "icon": "🆕",
            "title": "Novedades",
            "desc": "Feed completo del monitoreo diario.",
            "target_page": NOVEDADES_PAGE,
            "key": "nav_novedades",
        },
        {
            "icon": "🛰️",
            "title": "Fuentes",
            "desc": "Estado y calidad de cada fuente de datos.",
            "target_page": FUENTES_PAGE,
            "key": "nav_fuentes",
        },
    ]
)
