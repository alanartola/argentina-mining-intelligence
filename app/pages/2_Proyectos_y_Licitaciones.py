import pandas as pd
import streamlit as st

from mining_intel.db.queries import get_announcements_df, get_projects_df, get_tenders_df
from style import (
    badge,
    badge_row,
    hero,
    inject_base_styles,
    section_header,
    sidebar_brand,
    source_label,
    stage_kind,
    status_kind,
)

st.set_page_config(page_title="Proyectos y Licitaciones", page_icon="⛏️", layout="wide")

inject_base_styles()
sidebar_brand()

hero(
    title="Proyectos, inversiones y licitaciones",
    subtitle="Detalle filtrable de proyectos mineros únicos, sus anuncios de inversión y procesos de compra.",
    icon="📋",
    eyebrow="Detalle operativo",
)

_VIEWS = ["Proyectos / Inversiones", "Licitaciones"]

# Deep-link support: a KPI card on Home can navigate here with
# ?view=licitaciones. We only *force* the segmented control to that value
# the first time we see this particular query-param value (tracked via
# `_consumed_view_param`) - after that the user is free to toggle the
# control manually without it snapping back on every rerun.
_view_param = st.query_params.get("view")
if _view_param and st.session_state.get("_consumed_view_param") != _view_param:
    st.session_state["active_view"] = "Licitaciones" if _view_param == "licitaciones" else _VIEWS[0]
    st.session_state["_consumed_view_param"] = _view_param

active_view = st.segmented_control("Vista", _VIEWS, default=_VIEWS[0], key="active_view")

if active_view == "Proyectos / Inversiones":
    projects = get_projects_df()
    if projects.empty:
        st.info("Sin datos todavía. Corré `python scripts/run_update.py`.")
    else:
        all_provinces = sorted(
            {p for provinces in projects["provinces"].dropna() for p in provinces.split(", ") if p}
        )

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            province_filter = col1.multiselect("Provincia", all_provinces, key="province_projects")
            mineral_filter = col2.multiselect(
                "Mineral", sorted(projects["mineral"].dropna().unique()), key="mineral_projects"
            )
            stage_filter = col3.multiselect(
                "Etapa actual", sorted(projects["stage"].dropna().unique()), key="stage_projects"
            )

        filtered = projects
        if province_filter:
            filtered = filtered[
                filtered["provinces"].fillna("").apply(
                    lambda s: any(p in s.split(", ") for p in province_filter)
                )
            ]
        if mineral_filter:
            filtered = filtered[filtered["mineral"].isin(mineral_filter)]
        if stage_filter:
            filtered = filtered[filtered["stage"].isin(stage_filter)]

        stage_counts = filtered["stage"].value_counts()
        badge_row([badge(f"{stage} ({count})", stage_kind(stage)) for stage, count in stage_counts.items()])

        section_header(
            f"{len(filtered)} de {len(projects)} proyectos únicos",
            "Seleccioná una fila para abrir la ficha completa del proyecto.",
        )

        display = filtered.copy()
        display["Inversión total (USD)"] = display["total_investment_usd"].map(
            lambda v: f"USD {v:,.0f}" if pd.notna(v) else "—"
        )
        display = display.rename(
            columns={
                "name": "Proyecto",
                "provinces": "Provincia(s)",
                "mineral": "Mineral",
                "stage": "Etapa actual",
                "announcement_count": "Anuncios",
            }
        )

        with st.container(border=True):
            event = st.dataframe(
                display,
                column_order=["Proyecto", "Provincia(s)", "Mineral", "Etapa actual", "Inversión total (USD)", "Anuncios"],
                hide_index=True,
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row",
                key="projects_table",
            )

        selected_rows = (event or {}).get("selection", {}).get("rows", [])
        if selected_rows:
            selected_project_id = int(display.iloc[selected_rows[0]]["id"])
            st.switch_page("pages/4_Proyecto.py", query_params={"project_id": selected_project_id})

        announcements = get_announcements_df()
        with st.expander(f"Ver todos los anuncios de inversión (histórico) — {len(announcements)} registros"):
            display_a = announcements.copy()
            display_a["Inversión (USD)"] = display_a["investment_usd"].map(
                lambda v: f"USD {v:,.0f}" if pd.notna(v) else "—"
            )
            display_a["Fuente"] = display_a["source"].map(source_label)
            display_a = display_a.rename(
                columns={
                    "name": "Proyecto (según anuncio)",
                    "company": "Empresa",
                    "province": "Provincia (según anuncio)",
                    "mineral": "Mineral",
                    "stage": "Etapa",
                    "announced_date": "Fecha",
                }
            )
            st.dataframe(
                display_a,
                column_order=[
                    "Proyecto (según anuncio)", "Empresa", "Provincia (según anuncio)", "Mineral",
                    "Etapa", "Inversión (USD)", "Fecha", "Fuente",
                ],
                hide_index=True,
                use_container_width=True,
            )

else:
    tenders = get_tenders_df()
    if tenders.empty:
        st.info("Sin datos todavía. Corré `python scripts/run_update.py`.")
    else:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            province_filter_t = col1.multiselect(
                "Provincia", sorted(tenders["province"].dropna().unique()), key="province_tenders"
            )
            status_filter_t = col2.multiselect(
                "Estado", sorted(tenders["status"].dropna().unique()), key="status_tenders"
            )

        filtered_t = tenders
        if province_filter_t:
            filtered_t = filtered_t[filtered_t["province"].isin(province_filter_t)]
        if status_filter_t:
            filtered_t = filtered_t[filtered_t["status"].isin(status_filter_t)]

        status_counts = filtered_t["status"].value_counts()
        badge_row([badge(f"{status} ({count})", status_kind(status)) for status, count in status_counts.items()])

        section_header(f"{len(filtered_t)} de {len(tenders)} licitaciones")

        display_t = filtered_t.copy()
        display_t["budget_ars"] = display_t["budget_ars"].map(lambda v: f"$ {v:,.0f}" if pd.notna(v) else "—")
        display_t["Fuente"] = display_t["source"].map(source_label)
        display_t = display_t.rename(
            columns={
                "title": "Licitación / Compra",
                "entity": "Organismo",
                "province": "Provincia",
                "status": "Estado",
                "publish_date": "Publicación",
                "closing_date": "Apertura",
                "budget_ars": "Presupuesto (ARS)",
            }
        )

        with st.container(border=True):
            st.dataframe(
                display_t,
                column_order=[
                    "Licitación / Compra", "Organismo", "Provincia", "Estado",
                    "Publicación", "Apertura", "Presupuesto (ARS)", "Fuente",
                ],
                use_container_width=True,
                hide_index=True,
            )
