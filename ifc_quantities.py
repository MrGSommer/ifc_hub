import streamlit as st
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.element as IfcElement
import pandas as pd
import tempfile
import ace_tools as tools

def app(uploaded_files):
    st.header("IFC Mengenauswertung 🏗️")
    if not uploaded_files:
        st.warning("Bitte IFC-Datei(en) in der Sidebar hochladen.")
        return

    file_dict = {f.name: f for f in uploaded_files}
    selected_file_name = st.selectbox("IFC-Datei auswählen", file_options := list(file.name for file in uploaded_files), key="quantities_select")
    selected_file = file_dict[selected_file_name]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(selected_file.getbuffer())
        ifc_path = tmp.name

    if st.button("Mengenauswertung starten"):
        ifc = ifcopenshell.open(ifc_path)
        elements = ifc.by_type("IfcBuildingElement")
        data = []

        for el in elements:
            shape = IfcElement.get_shape(ifc, el=element, settings=IfcElement.geom_settings())
            quantities = IfcElement.get_psets(element)
            props = IfcElement.get_property_sets(element)

            data.append({
                "GUID": element.GlobalId,
                "IfcEntität": element.is_a(),
                "eBKP-H": IfcElement.get_psets(element).get('eBKP-H', "(n/a)"),
                "Material": IfcElement.get_material(element),
                "Anzahl": 1,
                "Volumen [m³]": IfcElement.get_volume(element) or 0,
                "Fläche [m²]": IfcElement.get_area(element),
                "Länge [m]": IfcElement.get_length(element),
                "Dicke [m]": IfcElement.get_thickness(element),
                "Höhe [m]": IfcElement.get_height(element),
                "ExterneBauteil": IfcElement.get_psets(element).get("IsExternal", False),
                "Tragend": IfcElement.get_psets(element).get("LoadBearing", False),
                "Geschoss": IfcElement.get_container(element, "IfcBuildingStorey"),
                "Gebäude": IfcElement.get_psets(element).get("Building", "(n/a)"),
            }

        df = pd.DataFrame(elements_data)
        tools.display_dataframe_to_user(name="IFC Mengenauswertung", dataframe=df)
