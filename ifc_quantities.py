import streamlit as st
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape as ifc_shape
import pandas as pd
import tempfile

def calculate_quantities(ifc_file):
    """
    Berechnet Mengen (Volumen, Fläche, Abmessungen) für alle IfcBuildingElemente.
    """
    settings = ifcopenshell.geom.settings()
    # Wir nutzen IfcBuildingElement als Filter; je nach Modell kann ggf. eine Erweiterung sinnvoll sein.
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
            bbox = ifc_shape.get_bbox(geometry)  # Liefert (min_xyz, max_xyz)
            length = bbox[1][0] - bbox[0][0]
            width  = bbox[1][1] - bbox[0][1]
            height = bbox[1][2] - bbox[0][2]

            # PropertySets auslesen (hier beispielhaft eBKP-H und typische Booleans)
            psets = ifcopenshell.util.element.get_psets(element)
            ebkp = psets.get("eBKP-H", "(n/a)")
            is_external = psets.get("IsExternal", False)
            load_bearing = psets.get("LoadBearing", False)

            # Ermitteln des Geschosses und Gebäudes über Containerbeziehungen
            storey = ifcopenshell.util.element.get_container(element, "IfcBuildingStorey")
            building = ifcopenshell.util.element.get_container(element, "IfcBuilding")

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
        towrite = df.to_excel(index=False)
        st.download_button(
            label="Mengenauswertung herunterladen (Excel)",
            data=towrite,
            file_name="mengenauswertung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
