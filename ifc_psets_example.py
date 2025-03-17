import streamlit as st
import ifcopenshell
import ifcopenshell.util.element as IfcElement
import tempfile

def app(uploaded_files):
    st.header("Eigenschaften & Mengen (Psets & QTO)")
    if not uploaded_files:
        st.warning("Bitte IFC-Dateien in der Sidebar hochladen.")
        return

    selected_file_name = st.selectbox(
        "Wähle eine IFC-Datei",
        [f.name for f in uploaded_files],
        key="psets_select"
    )
    selected_file = [f for f in uploaded_files if f.name == selected_file_name][0]

    # Temporäre Datei erstellen und IFC-Modell laden
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(selected_file.getbuffer())
        ifc_path = tmp.name

    model = ifcopenshell.open(ifc_path)
    walls = model.by_type("IfcWall")
    if not walls:
        st.error("Keine IfcWall-Elemente im Modell gefunden.")
        return
    wall = walls[0]

    # Ermittlung des Wall-Typs
    wall_type = IfcElement.get_type(wall)

    st.subheader("Psets für Wall Type")
    psets_type = IfcElement.get_psets(wall_type)
    st.json(psets_type)

    st.subheader("Psets für Wall Instanz")
    psets_wall = IfcElement.get_psets(wall)
    st.json(psets_wall)

    st.subheader("Nur Properties (psets_only=True)")
    psets_only = IfcElement.get_psets(wall, psets_only=True)
    st.json(psets_only)

    st.subheader("Nur Mengen (qtos_only=True)")
    qtos_only = IfcElement.get_psets(wall, qtos_only=True)
    st.json(qtos_only)
