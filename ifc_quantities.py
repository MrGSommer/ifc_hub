import streamlit as st
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape as ifc_shape
import ifcopenshell.util.element as IfcElement
import pandas as pd
import tempfile
import io

def calculate_quantities(ifc_file):
    """
    Berechnet Mengen (Volumen, Fläche, Abmessungen) für alle IfcBuildingElemente.
    Dabei werden exakte Funktionen zur Flächen- und Volumenberechnung verwendet,
    und die Bounding Box wird aus den extrahierten Vertices ermittelt.
    """
    settings = ifcopenshell.geom.settings()
    # Filter: Wir betrachten hier IfcBuildingElemente (anpassbar)
    elements = ifc_file.by_type("IfcBuildingElement")
    data = []

    for element in elements:
        try:
            # Geometrie generieren
            shape = ifcopenshell.geom.create_shape(settings, element)
            geometry = shape.geometry

            # Mengenauswertung mithilfe der ifc_shape-Funktionen
            volume = ifc_shape.get_volume(geometry)
            area = ifc_shape.get_area(geometry)
            # Erst Vertices extrahieren, dann Bounding Box berechnen
            vertices = ifc_shape.get_vertices(geometry)
            bbox_min, bbox_max = ifc_shape.get_bbox(vertices)
            length = bbox_max[0] - bbox_min[0]
            width  = bbox_max[1] - bbox_min[1]
            height = bbox_max[2] - bbox_min[2]

            # PropertySets auslesen
            psets = IfcElement.get_psets(element)
            ebkp = psets.get("eBKP-H", "(n/a)")
            is_external = psets.get("IsExternal", False)
            load_bearing = psets.get("LoadBearing", False)

            # Geschoss und Gebäude ermitteln (Container-Beziehungen)
            storey = IfcElement.get_container(element, "IfcBuildingStorey")
            building = IfcElement.get_container(element, "IfcBuilding")

            data.append({
                "GUID": element.GlobalId,
                "IfcEntität": element.is_a(),
                "Name": element.Name,
                "eBKP-H": ebkp,
                "Volumen [m³]": volume,
                "Fläche [m²]": area,
                "Länge [m]": length,
                "Breite [m]": width,
                "Höhe [m]": height,
                "ExterneBauteil": is_external,
                "Tragend": load_bearing,
                "Geschoss": storey.Name if storey else "(n/a)",
                "Gebäude": building.Name if building else "(n/a)"
            })
        except Exception as e:
            st.warning(f"Fehler bei Element {element.GlobalId}: {e}")

    return pd.DataFrame(data)

def app(uploaded_files):
    st.header("IFC Mengenauswertung 🏗️")
    if not uploaded_files:
        st.warning("Bitte IFC-Datei(en) in der Sidebar hochladen.")
        return

    selected_file_name = st.selectbox(
        "IFC-Datei auswählen",
        [file.name for file in uploaded_files],
        key="quantities_select"
    )
    selected_file = [f for f in uploaded_files if f.name == selected_file_name][0]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(selected_file.getbuffer())
        ifc_path = tmp.name

    if st.button("Mengenauswertung starten"):
        ifc_file = ifcopenshell.open(ifc_path)
        df = calculate_quantities(ifc_file)
        st.dataframe(df, use_container_width=True)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label="Mengenauswertung herunterladen (Excel)",
            data=buffer,
            file_name="mengenauswertung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
