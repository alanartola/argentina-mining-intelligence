import streamlit as st

from mining_intel.db.queries import get_projects_df, get_tenders_df

st.set_page_config(page_title="Proyectos y Licitaciones", page_icon="⛏️", layout="wide")
st.title("⛏️ Proyectos, inversiones y licitaciones")

tab_projects, tab_tenders = st.tabs(["Proyectos / Inversiones", "Licitaciones"])

with tab_projects:
    projects = get_projects_df()
    if projects.empty:
        st.info("Sin datos todavía. Corré `python scripts/run_update.py`.")
    else:
        col1, col2 = st.columns(2)
        province_filter = col1.multiselect(
            "Provincia", sorted(projects["province"].dropna().unique()), key="province_projects"
        )
        mineral_filter = col2.multiselect(
            "Mineral", sorted(projects["mineral"].dropna().unique()), key="mineral_projects"
        )

        filtered = projects
        if province_filter:
            filtered = filtered[filtered["province"].isin(province_filter)]
        if mineral_filter:
            filtered = filtered[filtered["mineral"].isin(mineral_filter)]

        st.dataframe(
            filtered[
                ["name", "company", "province", "mineral", "stage", "investment_usd", "announced_date", "source"]
            ],
            use_container_width=True,
            hide_index=True,
        )

with tab_tenders:
    tenders = get_tenders_df()
    if tenders.empty:
        st.info("Sin datos todavía. Corré `python scripts/run_update.py`.")
    else:
        province_filter_t = st.multiselect(
            "Provincia", sorted(tenders["province"].dropna().unique()), key="province_tenders"
        )
        filtered_t = tenders[tenders["province"].isin(province_filter_t)] if province_filter_t else tenders

        st.dataframe(
            filtered_t[
                ["title", "entity", "province", "status", "publish_date", "closing_date", "budget_ars", "source"]
            ],
            use_container_width=True,
            hide_index=True,
        )
