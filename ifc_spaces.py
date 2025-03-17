import streamlit as st
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as IfcElement
import ifcopenshell.util.shape as ifc_shape
import pandas as pd
import tempfile
import io

def calculate_spaces(ifc_file):
    """
    Liest IfcSpace-Elemente aus und ermittelt:
      - Raumname (LongName oder Name)
      - Raumkategorie (SIA416, falls vorhanden)
      - Bodenfläche (über get_area auf der Geometrie)
      - Approximierte Wandfläche (Perimeter * durchschnittliche Raumhöhe)
      - Geschoss und Gebäude (über Container-Beziehungen)
    """
    spaces = ifc_file.by_type("IfcSpace")
    data = []

    for space in spaces:
        try:
            name = space.LongName or space.Name or "(n/a)"
            psets = IfcElement.get_psets(space)
            room_category = psets.get("SIA416", "(n/a)")

            try:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, space)
                geometry = shape.geometry
                floor_area = ifc_shape.get_area(geometry)
                vertices = ifc_shape.get_vertices(geometry)
                bbox_min, bbox_max = ifc_shape.get_bbox(vertices)
                # Annahme: rechteckige Projektion, Perimeter berechnet aus X- und Y-Differenz
                perimeter = 2 * ((bbox_max[0] - bbox_min[0]) + (bbox_max[1] - bbox_min[1]))
                avg_height = bbox_max[2] - bbox_min[2]
                wall_area = perimeter * avg_height
            except Exception as e:
                floor_area = 0
                wall_area = 0

            storey = IfcElement.get_container(space, "IfcBuildingStorey")
            building = IfcElement.get_container(space, "IfcBuilding")
            data.append({
                "Raumname": name,
                "SIA416 Raumcode": room_category,
                "Bodenfläche [m²]": floor_area,
                "Wandfläche [m²]": wall_area,
                "Geschoss": storey.Name if storey else "(n/a)",
                "Gebäude": building.Name if building else "(n/a)",
                "GUID": space.GlobalId
            })
        except Exception as e:
            st.warning(f"Fehler bei Raum {space.GlobalId}: {e}")

    return pd.DataFrame(data)

def app(uploaded_files):
    st.header("IfcSpace Raumauswertung 📐")
    if not uploaded_files:
        st.warning("Bitte IFC-Datei(en) in der Sidebar hochladen.")
        return

    selected_file_name = st.selectbox(
        "IFC-Datei wählen für Raumauswertung",
        [f.name for f in uploaded_files],
        key="space_select"
    )
    selected_file = [f for f in uploaded_files if f.name == selected_file_name][0]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(selected_file.getbuffer())
        ifc_path = tmp.name

    if st.button("IfcSpace auswerten"):
        ifc_file = ifcopenshell.open(ifc_path)
        df_spaces = calculate_spaces(ifc_file)
        st.dataframe(df_spaces, use_container_width=True)
        buffer = io.BytesIO()
        df_spaces.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label="Raumauswertung herunterladen (Excel)",
            data=buffer,
            file_name="raumauswertung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
