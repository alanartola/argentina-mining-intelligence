import streamlit as st

from mining_intel.db.queries import get_announcements_df, get_projects_df, get_province_summary_df, get_tenders_df
from style import CHART_PRIMARY, CHART_SECONDARY, GOLD, NAVY, hero, inject_base_styles, kpi_action_row, section_header, sidebar_brand

st.set_page_config(page_title="Argentina Mining Intelligence", page_icon="⛏️", layout="wide")

inject_base_styles()
sidebar_brand()

hero(
    title="Argentina Mining Intelligence",
    subtitle="Proyectos, inversiones y licitaciones del sector minero argentino en un solo lugar.",
    icon="⛏️",
    eyebrow="Panel ejecutivo",
)

announcements = get_announcements_df()
projects = get_projects_df()
provinces_summary = get_province_summary_df()
tenders = get_tenders_df()

total_usd = announcements["investment_usd"].sum() if not announcements.empty else 0
n_provinces = provinces_summary["province"].nunique() if not provinces_summary.empty else 0

PROYECTOS_PAGE = "pages/2_Proyectos_y_Licitaciones.py"
PROVINCIAS_PAGE = "pages/3_Provincias.py"

kpi_action_row(
    [
        {
            "label": "Anuncios de inversión",
            "value": f"{len(announcements):,}",
            "help": "Registros SIACAM (histórico, sin deduplicar)",
            "accent": NAVY,
            "key": "kpi_announcements",
            "target_page": PROYECTOS_PAGE,
            "query_params": {"view": "proyectos"},
        },
        {
            "label": "Proyectos mineros",
            "value": f"{len(projects):,}",
            "help": "Proyectos únicos, tras deduplicar los anuncios",
            "accent": CHART_PRIMARY,
            "key": "kpi_projects",
            "target_page": PROYECTOS_PAGE,
            "query_params": {"view": "proyectos"},
        },
        {
            "label": "Inversión anunciada",
            "value": f"USD {total_usd:,.0f}",
            "help": "Acumulado de anuncios registrados",
            "accent": GOLD,
            "key": "kpi_investment",
            "target_page": PROYECTOS_PAGE,
            "query_params": {"view": "proyectos"},
        },
    ]
)

kpi_action_row(
    [
        {
            "label": "Provincias con proyectos",
            "value": f"{n_provinces}",
            "help": "Provincias argentinas reales (un proyecto multi-provincial cuenta en cada una)",
            "accent": NAVY,
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

if not announcements.empty:
    section_header(
        "Inversión anunciada por provincia",
        "Suma de montos anunciados (USD), de mayor a menor. Un proyecto multi-provincial suma en cada provincia real que lo compone.",
    )
    by_province = provinces_summary.set_index("province")["investment_usd"].sort_values(ascending=False)
    st.bar_chart(by_province, color=CHART_PRIMARY)

    section_header(
        "Inversión anunciada por mineral",
        "Suma de montos anunciados (USD), de mayor a menor.",
    )
    by_mineral = announcements.groupby("mineral")["investment_usd"].sum().sort_values(ascending=False)
    st.bar_chart(by_mineral, color=CHART_SECONDARY)
else:
    st.info("Todavía no hay datos cargados. Corré `python scripts/run_update.py` para poblar la base.")

section_header(
    "Cómo seguir",
    "Hacé clic en \"Ver detalle\" en cualquier KPI, o usá el menú lateral para el mapa y las tablas.",
)
