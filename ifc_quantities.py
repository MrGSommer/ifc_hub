import streamlit as st
import ifcopenshell
import ifcopenshell.util.element as IfcElement
import pandas as pd
import tempfile

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
        ifc = ifcopenshell.open(ifc_path)
        elements = ifc.by_type("IfcBuildingElement")
        data = []

        for element in elements:
            quantities = IfcElement.get_psets(element)
            data.append({
                "GUID": element.GlobalId,
                "IfcEntität": element.is_a(),
                "eBKP-H": quantities.get('eBKP-H', "(n/a)"),
                "Material": IfcElement.get_material(element),
                "Anzahl": 1,
                "Volumen [m³]": IfcElement.get_volume(element) or 0,
                "Fläche [m²]": IfcElement.get_area(element) or 0,
                "Länge [m]": IfcElement.get_length(element) or 0,
                "Dicke [m]": IfcElement.get_thickness(element) or 0,
                "Höhe [m]": IfcElement.get_height(element) or 0,
                "ExterneBauteil": quantities.get("IsExternal", False),
                "Tragend": quantities.get("LoadBearing", False),
                "Geschoss": IfcElement.get_container(element, "IfcBuildingStorey").Name if IfcElement.get_container(element, "IfcBuildingStorey") else "(n/a)",
                "Gebäude": IfcElement.get_container(element, "IfcBuilding").Name if IfcElement.get_container(element, "IfcBuilding") else "(n/a)",
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="Mengenauswertung herunterladen (Excel)",
            data=df.to_excel(index=False),
            file_name="mengenauswertung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
