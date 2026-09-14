import folium
import streamlit as st
from streamlit_folium import st_folium

from mining_intel.db.queries import get_projects_df, get_tenders_df
from mining_intel.processing.normalize import get_province_centroid, normalize_province
from style import COPPER, hero, inject_base_styles, section_header, sidebar_brand

st.set_page_config(page_title="Mapa - Argentina Mining Intelligence", page_icon="🗺️", layout="wide")

inject_base_styles()
sidebar_brand()

hero(
    title="Mapa de proyectos y licitaciones",
    subtitle="Ubicación geográfica de proyectos mineros únicos y procesos de compra del sector minero.",
    icon="🗺️",
    eyebrow="Vista geoespacial",
)

projects = get_projects_df()
tenders = get_tenders_df()

with st.container(border=True):
    mineral_options = sorted(projects["mineral"].dropna().unique()) if not projects.empty else []
    selected_minerals = st.multiselect(
        "Filtrar proyectos por mineral", mineral_options, default=mineral_options
    )

filtered_projects = projects[projects["mineral"].isin(selected_minerals)] if mineral_options else projects
plotted_projects = filtered_projects.dropna(subset=["lat", "lon"])
plotted_investment = plotted_projects["total_investment_usd"].sum() if not plotted_projects.empty else 0

section_header(
    f"{len(plotted_projects)} proyectos únicos · USD {plotted_investment:,.0f} representados en el mapa",
    "🟠 Proyectos mineros (marcador = centroide provincial, no la ubicación exacta) — 🔵 Licitaciones",
)

m = folium.Map(location=[-38.4, -63.6], zoom_start=4, tiles="OpenStreetMap")

for _, row in plotted_projects.iterrows():
    amount = f"USD {row['total_investment_usd']:,.0f}" if row["total_investment_usd"] else "Monto no informado"
    popup = (
        f"<b>{row['name']}</b><br>{row['mineral']} · {row['provinces']}<br>"
        f"{amount} en {int(row['announcement_count'])} anuncio(s)<br>"
        f"<i>Abrí la ficha completa desde la lista debajo del mapa</i>"
    )
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=7,
        color=COPPER,
        fill=True,
        fill_color="#D98C3D",
        fill_opacity=0.85,
        popup=folium.Popup(popup, max_width=260),
        tooltip=row["name"],
    ).add_to(m)

for _, row in tenders.iterrows():
    centroid = get_province_centroid(normalize_province(row.get("province")))
    if not centroid:
        continue
    popup = f"<b>{row['title']}</b><br>{row['entity']}<br>Estado: {row['status']}"
    folium.Marker(
        location=centroid,
        icon=folium.Icon(color="blue", icon="file-alt", prefix="fa"),
        popup=folium.Popup(popup, max_width=260),
        tooltip=(row["title"] or "")[:60],
    ).add_to(m)

with st.container(border=True):
    st_folium(m, use_container_width=True, height=650)

# Folium popups can't call back into Streamlit navigation, so opening a
# ficha from the map goes through a plain Streamlit control right below it.
section_header("Abrir ficha de un proyecto del mapa")
if plotted_projects.empty:
    st.caption("No hay proyectos para mostrar con los filtros actuales.")
else:
    options = plotted_projects.sort_values("name")
    choice = st.selectbox(
        "Proyecto",
        options["id"],
        format_func=lambda pid: options.loc[options["id"] == pid, "name"].iloc[0],
        key="map_project_choice",
    )
    if st.button("Ver ficha completa →", key="map_open_ficha"):
        st.switch_page("pages/4_Proyecto.py", query_params={"project_id": int(choice)})
