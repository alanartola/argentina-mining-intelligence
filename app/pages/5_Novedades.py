from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from mining_intel.db.queries import get_news_events_df
from style import (
    badge,
    badge_row,
    category_label,
    hero,
    inject_base_styles,
    relevance_kind,
    relevance_label,
    section_header,
    sidebar_brand,
)

st.set_page_config(page_title="Novedades - Argentina Mining Intelligence", page_icon="🆕", layout="wide")

inject_base_styles()
sidebar_brand()

hero(
    title="Novedades",
    subtitle="Monitor diario de publicaciones nuevas sobre minería argentina.",
    icon="🆕",
    eyebrow="Monitoreo diario",
)

events = get_news_events_df()

if events.empty:
    st.info(
        "Todavía no hay novedades detectadas. Corré `python -m mining_intel.pipeline.run_daily` "
        "para ejecutar el motor de monitoreo."
    )
    st.stop()

events["detected_at_dt"] = pd.to_datetime(events["detected_at"], errors="coerce", utc=True)
cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
last_24h = events[events["detected_at_dt"] >= cutoff]

section_header("Últimas 24 horas")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Críticas", int((last_24h["relevance"] == "CRITICAL").sum()))
col2.metric("Importantes", int((last_24h["relevance"] == "HIGH").sum()))
col3.metric("Publicaciones oficiales", int((last_24h["official"] == 1).sum()))
col4.metric("Noticias", int((last_24h["category"] == "NEWS").sum()))
col5.metric("Licitaciones", int((last_24h["category"] == "TENDER").sum()))
col6.metric("Proyectos actualizados", int(last_24h["project_id"].dropna().nunique()))

section_header("Feed cronológico", "Ordenado por fecha de detección, de más reciente a más antiguo.")

with st.container(border=True):
    fcol1, fcol2, fcol3, fcol4, fcol5 = st.columns(5)
    relevance_filter = fcol1.multiselect(
        "Relevancia", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], format_func=relevance_label, key="news_relevance"
    )
    source_filter = fcol2.multiselect(
        "Fuente", sorted(events["source_display_name"].dropna().unique()), key="news_source"
    )
    province_filter = fcol3.multiselect("Provincia", sorted(events["province"].dropna().unique()), key="news_province")
    project_filter = fcol4.multiselect("Proyecto", sorted(events["project_name"].dropna().unique()), key="news_project")
    category_filter = fcol5.multiselect(
        "Categoría", sorted(events["category"].dropna().unique()), format_func=category_label, key="news_category"
    )

    date_options = sorted(events["detected_at_dt"].dt.date.dropna().unique(), reverse=True)
    date_filter = st.multiselect("Fecha de detección", date_options, key="news_date")

filtered = events
if relevance_filter:
    filtered = filtered[filtered["relevance"].isin(relevance_filter)]
if source_filter:
    filtered = filtered[filtered["source_display_name"].isin(source_filter)]
if province_filter:
    filtered = filtered[filtered["province"].isin(province_filter)]
if project_filter:
    filtered = filtered[filtered["project_name"].isin(project_filter)]
if category_filter:
    filtered = filtered[filtered["category"].isin(category_filter)]
if date_filter:
    filtered = filtered[filtered["detected_at_dt"].dt.date.isin(date_filter)]

st.caption(f"{len(filtered)} de {len(events)} novedades")

for _, event in filtered.iterrows():
    with st.container(border=True):
        badge_row(
            [
                badge(relevance_label(event["relevance"]), relevance_kind(event["relevance"])),
                badge(category_label(event["category"]), "slate"),
            ]
        )
        st.markdown(f"**{event['title']}**")
        meta_bits = [
            event["detected_at_dt"].strftime("%Y-%m-%d %H:%M UTC") if pd.notna(event["detected_at_dt"]) else "—",
            event["source_display_name"] or event["source_internal_name"],
        ]
        if event["province"]:
            meta_bits.append(event["province"])
        if pd.notna(event["project_name"]):
            meta_bits.append(f"Proyecto: {event['project_name']}")
        st.caption(" · ".join(str(b) for b in meta_bits))
        if event["summary"]:
            st.write(event["summary"])
        st.caption(f"Por qué esta relevancia: {event['relevance_reason']}")
        st.markdown(f"[Ver fuente original]({event['source_url']})")
