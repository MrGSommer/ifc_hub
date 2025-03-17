import streamlit as st
import ifcopenshell
import ifcopenshell.util.element as IfcElement
import pandas as pd
import tempfile

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
        ifc = ifcopenshell.open(ifc_path)
        spaces = ifc.by_type("IfcSpace")

        data = []
        for space in spaces:
            props = IfcElement.get_psets(space)
            name = space.LongName or space.Name or "(n/a)"
            raumcode = props.get("SIA416", "(n/a)")

            geom = IfcElement.get_representation(space)
            bodenfläche = IfcElement.get_footprint_area(geom) or 0
            wandfläche = IfcElement.get_side_area(geom) or 0

            storey = IfcElement.get_container(space, "IfcBuildingStorey")
            building = IfcElement.get_container(space, "IfcBuilding")

            data.append({
                "Raumname": name,
                "SIA416 Raumcode": raumcode,
                "Bodenfläche [m²]": bodenfläche,
                "Wandfläche [m²]": wandfläche,
                "Geschoss": storey.Name if storey else "(n/a)",
                "Gebäude": building.Name if building else "(n/a)",
                "GUID": space.GlobalId
            })

        df_spaces = pd.DataFrame(data)
        st.dataframe(df_spaces, use_container_width=True)

        st.download_button(
            label="Raumauswertung herunterladen (Excel)",
            data=df_spaces.to_excel(index=False),
            file_name="raumauswertung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
