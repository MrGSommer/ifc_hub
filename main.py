import streamlit as st
from ifc_requirements import app as ifc_requirements_app
from ifc_remover import app as ifc_remover_app
from ifc_viewer import app as ifc_viewer_app

st.set_page_config(page_title="IFC Operation Hub", layout="wide")
st.title("IFC Operation Hub")
st.markdown("Wählen Sie einen Tab für verschiedene IFC-Operationen.")

# Sidebar: Mehrere IFC-Dateien hochladen
uploaded_ifc_files = st.sidebar.file_uploader(
    "Laden Sie IFC-Dateien hoch", type=["ifc"], accept_multiple_files=True
)
st.sidebar.markdown("### Hochgeladene Dateien")
if uploaded_ifc_files:
    for file in uploaded_ifc_files:
        st.sidebar.write(file.name)
else:
    st.sidebar.info("Keine IFC-Dateien hochgeladen.")

tabs = st.tabs(["Übersicht & Tool-Erklärungen", "IFC Element Remover", "3D Viewer"])

with tabs[0]:
    ifc_requirements_app(uploaded_ifc_files)

with tabs[1]:
    ifc_remover_app(uploaded_ifc_files)

with tabs[2]:
    ifc_viewer_app(uploaded_ifc_files)
