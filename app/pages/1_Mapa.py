import folium
import streamlit as st
from streamlit_folium import st_folium

from mining_intel.db.queries import get_projects_df, get_tenders_df
from mining_intel.processing.normalize import get_province_centroid, normalize_province

st.set_page_config(page_title="Mapa - Argentina Mining Intelligence", page_icon="🗺️", layout="wide")
st.title("🗺️ Mapa de proyectos y licitaciones")

projects = get_projects_df()
tenders = get_tenders_df()

mineral_options = sorted(projects["mineral"].dropna().unique()) if not projects.empty else []
selected_minerals = st.multiselect("Filtrar proyectos por mineral", mineral_options, default=mineral_options)

filtered_projects = projects[projects["mineral"].isin(selected_minerals)] if mineral_options else projects

m = folium.Map(location=[-38.4, -63.6], zoom_start=4, tiles="OpenStreetMap")

for _, row in filtered_projects.dropna(subset=["lat", "lon"]).iterrows():
    amount = f"USD {row['investment_usd']:,.0f}" if row["investment_usd"] else "Monto no informado"
    popup = f"<b>{row['name']}</b><br>{row['company']}<br>{row['mineral']} · {row['province']}<br>{amount}"
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=7,
        color="#b5651d",
        fill=True,
        fill_color="#d98c3d",
        fill_opacity=0.85,
        popup=folium.Popup(popup, max_width=260),
        tooltip=row["name"] or row["company"],
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

st.caption("🟠 Proyectos / anuncios de inversión — 🔵 Licitaciones")
st_folium(m, use_container_width=True, height=600)
