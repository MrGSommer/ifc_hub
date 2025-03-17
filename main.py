import streamlit as st
from ifc_requirements import app as ifc_requirements_app
from ifc_remover import app as ifc_remover_app
from ifc_quantities import app as ifc_quantities_app
from ifc_spaces import app as ifc_spaces_app

st.set_page_config(page_title="IFC Operation Hub", layout="wide")
st.title("IFC Operation Hub 🚧")
st.markdown("Wählen Sie einen Tab für verschiedene IFC-Operationen.")

uploaded_ifc_files = st.sidebar.file_uploader(
    "IFC-Dateien hochladen", type=["ifc"], accept_multiple_files=True
)

if uploaded_ifc_files := uploaded_ifc_files:
    st.sidebar.success("Dateien geladen:")
    for f in uploaded_ifc_files:
        st.sidebar.write(f"✅ {f.name}")
else:
    st.sidebar.info("Bitte IFC-Dateien hochladen.")

tabs = st.tabs(["Übersicht", "IFC Element Remover", "Mengenauswertung", "Raumauswertung"])


with tabs[0]:
    ifc_requirements_app(uploaded_files)

with tabs[1]:
    ifc_remover_app(uploaded_files)

with tabs[2]:
    ifc_quantities_app(uploaded_ifc_files)

with tabs[3]:
    ifc_spaces_app(uploaded_ifc_files)
