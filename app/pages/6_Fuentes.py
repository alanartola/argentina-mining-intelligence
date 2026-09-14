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
        "Todavía no hay fuentes registradas. Corré `python -m mining_intel.pipeline.run_daily` "
        "para poblar esta vista."
    )
    st.stop()

_STATE_KIND = {"ACTIVE": "green", "FAILED": "red", "MANUAL": "amber", "UNSUPPORTED": "slate"}
_METHOD_KIND = {
    "API": "navy", "RSS": "navy", "DATASET": "navy",
    "HTML": "copper", "SEARCH": "copper", "MANUAL": "slate",
}

section_header(f"{len(sources)} fuentes evaluadas")

display = sources.copy()
display["Estado"] = display["state"].map(lambda s: badge(s, _STATE_KIND.get(s, "slate")))
display["Método"] = display["automation_method"].map(
    lambda m: badge(m, _METHOD_KIND.get(m, "slate")) if pd.notna(m) else ""
)
display = display.rename(
    columns={
        "display_name": "Fuente",
        "source_type": "Tipo",
        "last_run_at": "Última ejecución",
        "last_success_at": "Última ejecución exitosa",
        "last_document_count": "Documentos encontrados",
        "last_error": "Último error / motivo",
        "last_new_event_title": "Última novedad detectada",
        "last_new_event_at": "Fecha última novedad",
    }
)

for _, row in display.iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{row['Fuente']}**" + (f" · {row['Tipo']}" if pd.notna(row["Tipo"]) else ""))
            badges_html = row["Estado"] + " " + row["Método"]
            st.markdown(badges_html, unsafe_allow_html=True)
        with col2:
            st.caption(f"Docs: {row['Documentos encontrados'] if pd.notna(row['Documentos encontrados']) else '—'}")

        detail_cols = st.columns(2)
        detail_cols[0].caption(f"Última ejecución: {row['Última ejecución'] or '—'}")
        detail_cols[1].caption(f"Última exitosa: {row['Última ejecución exitosa'] or '—'}")

        if pd.notna(row["Última novedad detectada"]):
            st.caption(f"🆕 Última novedad: {row['Última novedad detectada']} ({row['Fecha última novedad']})")

        if row["Último error / motivo"]:
            st.caption(f"⚠️ {row['Último error / motivo']}")
