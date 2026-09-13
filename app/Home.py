import streamlit as st

from mining_intel.db.queries import get_projects_df, get_tenders_df

st.set_page_config(page_title="Argentina Mining Intelligence", page_icon="⛏️", layout="wide")

st.title("⛏️ Argentina Mining Intelligence")
st.caption("Proyectos, inversiones y licitaciones del sector minero argentino.")

projects = get_projects_df()
tenders = get_tenders_df()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Anuncios de inversión", len(projects))
total_usd = projects["investment_usd"].sum() if not projects.empty else 0
col2.metric("Inversión anunciada (USD)", f"{total_usd:,.0f}")
col3.metric("Provincias con proyectos", projects["province"].nunique() if not projects.empty else 0)
col4.metric("Licitaciones registradas", len(tenders))

st.divider()

if not projects.empty:
    st.subheader("Inversión anunciada por provincia (USD)")
    by_province = projects.groupby("province")["investment_usd"].sum().sort_values(ascending=False)
    st.bar_chart(by_province)

    st.subheader("Inversión anunciada por mineral (USD)")
    by_mineral = projects.groupby("mineral")["investment_usd"].sum().sort_values(ascending=False)
    st.bar_chart(by_mineral)
else:
    st.info("Todavía no hay datos cargados. Corré `python scripts/run_update.py` para poblar la base.")

st.divider()
st.caption("Usá el menú lateral para ver el mapa interactivo y las tablas detalladas.")
