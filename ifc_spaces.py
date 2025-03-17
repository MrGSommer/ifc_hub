import streamlit as st
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as IfcElement
import ifcopenshell.util.shape as ifc_shape
import pandas as pd
import tempfile

def calculate_spaces(ifc_file):
    """
    Liest IfcSpace-Elemente aus, ermittelt Raumname, Raumkategorie (SIA416),
    Bodenfläche und Wandfläche (approximiert) sowie Geschoss und Gebäude.
    """
    spaces = ifc_file.by_type("IfcSpace")
    data = []

    for space in spaces:
        try:
            # Raumname (LongName bevorzugt, ansonsten Name)
            name = space.LongName or space.Name or "(n/a)"
            # Raumkategorie aus PropertySet "SIA416"
            psets = IfcElement.get_psets(space)
            room_category = psets.get("SIA416", "(n/a)")

            # Versuche, Geometrie zu erzeugen – nicht alle IfcSpace haben eine direkte Darstellung.
            try:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, space)
                geometry = shape.geometry
                floor_area = ifc_shape.get_area(geometry)
                bbox = ifc_shape.get_bbox(geometry)
                perimeter = 2 * ((bbox[1][0] - bbox[0][0]) + (bbox[1][1] - bbox[0][1]))
                avg_height = bbox[1][2] - bbox[0][2]
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
    st.header("Raumauswertung 📐")
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
        towrite = df_spaces.to_excel(index=False)
        st.download_button(
            label="Raumauswertung herunterladen (Excel)",
            data=towrite,
            file_name="raumauswertung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
