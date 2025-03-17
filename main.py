import streamlit as st
from ifc_requirements import app as ifc_requirements_app
from ifc_remover import app as ifc_remover_app

st.set_page_config(page_title="IFC Operation Hub", layout="wide")
st.title("IFC Operation Hub")
st.markdown("Wählen Sie einen Tab für verschiedene IFC-Operationen.")

tabs = st.tabs(["Übersicht & Tool-Erklärungen", "IFC Element Remover"])

with tabs[0]:
    ifc_requirements_app()

with tabs[1]:
    ifc_remover_app()
