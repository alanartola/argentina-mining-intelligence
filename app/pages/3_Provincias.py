import pandas as pd
import streamlit as st

from mining_intel.db.queries import get_province_summary_df, get_projects_df
from style import badge, badge_row, hero, inject_base_styles, section_header, sidebar_brand, stage_kind

st.set_page_config(page_title="Provincias - Argentina Mining Intelligence", page_icon="🗺️", layout="wide")

inject_base_styles()
sidebar_brand()

hero(
    title="Provincias",
    subtitle="Actividad minera real por provincia argentina — un proyecto multi-provincial cuenta en cada una.",
    icon="🗺️",
    eyebrow="Drill-down geográfico",
)

summary = get_province_summary_df()

if summary.empty:
    st.info("Todavía no hay datos cargados. Corré `python scripts/run_update.py`.")
else:
    display = summary.copy()
    display["Inversión anunciada (USD)"] = display["investment_usd"].map(lambda v: f"USD {v:,.0f}")
    display = display.rename(
        columns={
            "province": "Provincia",
            "unique_projects": "Proyectos únicos",
            "announcements": "Anuncios de inversión",
            "minerals": "Minerales presentes",
            "tenders": "Licitaciones",
        }
    )

    section_header(
        f"{len(display)} provincias con actividad minera",
        "Ordenadas por inversión anunciada acumulada. Seleccioná una fila para ver el detalle.",
    )

    with st.container(border=True):
        event = st.dataframe(
            display,
            column_order=[
                "Provincia", "Proyectos únicos", "Anuncios de inversión",
                "Inversión anunciada (USD)", "Minerales presentes", "Licitaciones",
            ],
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            key="provinces_table",
        )

    selected_rows = (event or {}).get("selection", {}).get("rows", [])
    if selected_rows:
        row = summary.iloc[selected_rows[0]]
        province = row["province"]

        section_header(f"📍 {province}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Proyectos únicos", int(row["unique_projects"]))
        col2.metric("Inversión anunciada", f"USD {row['investment_usd']:,.0f}")
        col3.metric("Licitaciones", int(row["tenders"]))

        minerals = [m for m in (row["minerals"] or "").split(", ") if m]
        badge_row([badge(m, "copper") for m in minerals])

        projects = get_projects_df()
        province_projects = projects[
            projects["provinces"].fillna("").apply(lambda s: province in s.split(", "))
        ].sort_values("total_investment_usd", ascending=False)

        st.markdown(f"**Proyectos en {province}**")
        for _, project in province_projects.iterrows():
            with st.container(border=True):
                pcol1, pcol2 = st.columns([4, 1])
                with pcol1:
                    st.markdown(f"**{project['name']}**")
                    stage_badge = badge(project["stage"] or "Etapa no informada", stage_kind(project["stage"]))
                    st.markdown(
                        f"{stage_badge} {project['mineral'] or ''} · USD {project['total_investment_usd']:,.0f} "
                        f"· {int(project['announcement_count'])} anuncio(s)",
                        unsafe_allow_html=True,
                    )
                with pcol2:
                    if st.button("Ver ficha →", key=f"prov_project_{project['id']}", use_container_width=True):
                        st.switch_page("pages/4_Proyecto.py", query_params={"project_id": int(project["id"])})
    else:
        st.caption("Seleccioná una provincia en la tabla para ver su detalle.")
