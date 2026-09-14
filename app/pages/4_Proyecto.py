import pandas as pd
import streamlit as st

from mining_intel.db.queries import get_project_detail
from style import badge, badge_row, hero, inject_base_styles, section_header, sidebar_brand, source_label, source_link, stage_kind

st.set_page_config(page_title="Ficha de Proyecto - Argentina Mining Intelligence", page_icon="🗂️", layout="wide")

inject_base_styles()
sidebar_brand()

_NOT_AVAILABLE = "No disponible"
_NO_SUMMARY = "Información descriptiva pendiente de incorporar."

raw_id = st.query_params.get("project_id") or st.session_state.get("selected_project_id")

if not raw_id:
    hero(
        title="Ficha de Proyecto",
        subtitle="Ningún proyecto seleccionado todavía.",
        icon="🗂️",
        eyebrow="Detalle de proyecto",
    )
    st.info("Seleccioná un proyecto desde el Home, desde Provincias, desde la tabla de proyectos o desde el mapa.")
    st.page_link("Home.py", label="⛏️ Ir a Home", icon="↩️")
    st.page_link("pages/3_Provincias.py", label="🗺️ Ir a Provincias", icon="↩️")
    st.page_link("pages/2_Proyectos_y_Licitaciones.py", label="📋 Ir a Proyectos y Licitaciones", icon="↩️")
    st.stop()

project = get_project_detail(int(raw_id))

if project is None:
    hero(title="Ficha de Proyecto", subtitle="Proyecto no encontrado.", icon="🗂️", eyebrow="Detalle de proyecto")
    st.warning(
        "No se encontró ese proyecto — puede que la base se haya reconstruido. "
        "Volvé a seleccionarlo desde Provincias o la tabla de proyectos."
    )
    st.page_link("pages/2_Proyectos_y_Licitaciones.py", label="📋 Ir a Proyectos y Licitaciones", icon="↩️")
    st.stop()

st.session_state["selected_project_id"] = project["id"]

profile = project.get("profile")
announcements = project["announcements"]
provinces = project["provinces"]

hero(
    title=project["name"] or "Proyecto sin nombre",
    subtitle=f"{project['mineral'] or 'Mineral no informado'} · {', '.join(provinces) or 'Provincia no informada'}",
    icon="🗂️",
    eyebrow="Ficha de proyecto",
)

badge_row(
    [badge(project["stage"] or "Etapa no informada", stage_kind(project["stage"]))]
    + [badge(p, "navy") for p in provinces]
)

section_header("Resumen ejecutivo")
if profile and profile.get("summary"):
    st.markdown(profile["summary"])
else:
    st.info(_NO_SUMMARY)

section_header("Ubicación")
loc_col1, loc_col2, loc_col3 = st.columns(3)
loc_col1.markdown(f"**Provincia(s)**\n\n{', '.join(provinces) or _NOT_AVAILABLE}")
loc_col2.markdown(
    f"**Departamento / localidad**\n\n{(profile or {}).get('department_locality') or _NOT_AVAILABLE}"
)
if profile and profile.get("precise_coordinates"):
    coord_text = f"{profile['precise_coordinates'][0]}, {profile['precise_coordinates'][1]} (fuente verificada)"
elif project.get("lat") is not None and project.get("lon") is not None:
    coord_text = f"~{project['lat']:.4f}, {project['lon']:.4f} (aproximación por centroide provincial, no es la ubicación exacta)"
else:
    coord_text = _NOT_AVAILABLE
loc_col3.markdown(f"**Coordenadas**\n\n{coord_text}")

section_header("Empresas involucradas")
comp_col1, comp_col2 = st.columns(2)
with comp_col1:
    st.markdown(f"**Propietario:** {(profile or {}).get('owner') or _NOT_AVAILABLE}")
    st.markdown(f"**Operador:** {(profile or {}).get('operator') or _NOT_AVAILABLE}")
with comp_col2:
    partners = (profile or {}).get("partners") or []
    contractors = (profile or {}).get("contractors") or []
    st.markdown(f"**Socios:** {', '.join(partners) if partners else _NOT_AVAILABLE}")
    st.markdown(f"**Contratistas:** {', '.join(contractors) if contractors else _NOT_AVAILABLE}")

raw_companies = sorted({c for c in announcements["company"].dropna() if c.strip()})
if raw_companies:
    st.caption("Empresas mencionadas en los anuncios (rol no verificado, no asumido como propietario/operador):")
    badge_row([badge(c, "slate") for c in raw_companies])

section_header(
    "Inversión y cronología",
    f"USD {project['total_investment_usd']:,.0f} anunciados en {project['announcement_count']} anuncio(s), ordenados por fecha.",
)
history = announcements.copy()
history["Inversión (USD)"] = history["investment_usd"].map(lambda v: f"USD {v:,.0f}" if pd.notna(v) else "—")
history["Fuente"] = history["source"].map(source_label)
history = history.rename(
    columns={"announced_date": "Fecha", "company": "Empresa", "stage": "Etapa"}
)
st.dataframe(
    history,
    column_order=["Fecha", "Empresa", "Etapa", "Inversión (USD)", "Fuente"],
    hide_index=True,
    use_container_width=True,
)

section_header(
    "Objetivo / qué se busca",
    "Secuencia real de etapas declaradas en los anuncios (Secretaría de Minería / SIACAM).",
)
stage_sequence = [s for s in history["Etapa"] if s]
if stage_sequence:
    st.markdown(" → ".join(stage_sequence))
else:
    st.info(_NOT_AVAILABLE)

section_header("Fuentes")
cited_sources = sorted({s for s in announcements["source"].dropna()})
for source in cited_sources:
    st.markdown(f"- {source_link(source)} (datos estructurados: empresa, monto, fecha, etapa)", unsafe_allow_html=True)

if profile and profile.get("sources"):
    for src in profile["sources"]:
        st.markdown(
            f"- [{src['name']}]({src['url']}) — consultado el {src['retrieved_at']} (resumen ejecutivo)"
        )
elif not profile:
    st.caption("Sin fuentes adicionales para el resumen descriptivo — ver nota en \"Resumen ejecutivo\".")
