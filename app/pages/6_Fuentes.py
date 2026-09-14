import pandas as pd
import streamlit as st

from mining_intel.db.queries import get_news_sources_df
from style import badge, hero, inject_base_styles, section_header, sidebar_brand

st.set_page_config(page_title="Fuentes - Argentina Mining Intelligence", page_icon="🛰️", layout="wide")

inject_base_styles()
sidebar_brand()

hero(
    title="Fuentes",
    subtitle="Estado y calidad de datos de cada fuente del monitor de minería.",
    icon="🛰️",
    eyebrow="Data quality",
)

sources = get_news_sources_df()

if sources.empty:
    st.info(
        "Todavía no hay fuentes registradas. Corré `python scripts/run_daily_news.py` "
        "para poblar esta vista."
    )
    st.stop()

_STATE_KIND = {"ACTIVE": "green", "FAILED": "red", "MANUAL": "amber", "UNSUPPORTED": "slate"}

section_header(f"{len(sources)} fuentes evaluadas")

display = sources.copy()
display["Estado"] = display["state"].map(lambda s: badge(s, _STATE_KIND.get(s, "slate")))
display = display.rename(
    columns={
        "display_name": "Fuente",
        "last_run_at": "Última ejecución",
        "last_success_at": "Última ejecución exitosa",
        "last_document_count": "Documentos encontrados",
        "last_error": "Último error / motivo",
    }
)

for _, row in display.iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{row['Fuente']}**", unsafe_allow_html=True)
            st.markdown(row["Estado"], unsafe_allow_html=True)
        with col2:
            st.caption(f"Docs: {row['Documentos encontrados'] if pd.notna(row['Documentos encontrados']) else '—'}")
        detail_cols = st.columns(3)
        detail_cols[0].caption(f"Última ejecución: {row['Última ejecución'] or '—'}")
        detail_cols[1].caption(f"Última exitosa: {row['Última ejecución exitosa'] or '—'}")
        if row["Último error / motivo"]:
            detail_cols[2].caption(f"⚠️ {row['Último error / motivo']}")
