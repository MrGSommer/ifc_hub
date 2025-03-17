import streamlit as st
from ifc_requirements import app as ifc_requirements_app
from ifc_remover import app as ifc_remover_app
from ifc_quantities import app as ifc_quantities_app
from ifc_spaces import app as ifc_spaces_app
from ifc_psets_example import app as ifc_psets_example_app

st.set_page_config(page_title="IFC Operation Hub", layout="wide")
st.title("IFC Operation Hub 🚧")
st.markdown("Wähle einen Tab für verschiedene IFC-Operationen.")

uploaded_ifc_files = st.sidebar.file_uploader(
    "IFC-Dateien hochladen", type=["ifc"], accept_multiple_files=True
)

if uploaded_ifc_files:
    st.sidebar.markdown("### Hochgeladene Dateien:")
    for f in uploaded_ifc_files:
        st.sidebar.write(f"- {f.name}")
else:
    st.sidebar.info("Noch keine Dateien hochgeladen.")

tabs = st.tabs([
    "Übersicht & Anforderungen",
    "IFC Element Remover",
    "Mengenauswertung",
    "Raumauswertung (IfcSpace)",
    "Psets & QTO (low Files)"
])

with tabs[0]:
    ifc_requirements_app(uploaded_ifc_files)

with tabs[1]:
    ifc_remover_app(uploaded_ifc_files)

with tabs[2]:
    ifc_quantities_app(uploaded_ifc_files)

with tabs[3]:
    ifc_spaces_app(uploaded_ifc_files)

with tabs[4]:
    ifc_psets_example_app(uploaded_ifc_files)
