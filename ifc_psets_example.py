import streamlit as st
import ifcopenshell
import ifcopenshell.util.element as IfcElement
import pandas as pd
import tempfile

def calculate_reference_quantities(ifc_file):
    """
    Berechnet für jedes IfcBuildingElement (alle netto) eine Referenzmenge,
    abhängig vom IFC-Typ:
      - IfcWall: NetSideArea
      - IfcSlab: NetFootprintArea
      - IfcColumn: NominalHeight
      - IfcBeam: NominalLength
      - Default: NetVolume
    Zusätzlich werden weitere Mengen (NetVolume, NominalLength, NominalWidth, NominalHeight)
    aus den BaseQuantities extrahiert.
    """
    # Wir verarbeiten hier alle IfcBuildingElemente – Anpassung je nach Modell möglich.
    elements = ifc_file.by_type("IfcBuildingElement")
    rows = []
    
    for element in elements:
        try:
            # Hole QTO-Daten (nur Mengen, "qtos_only") aus den PropertySets
            qto = IfcElement.get_psets(element, qtos_only=True)
            # Versuche, aus der Gruppe "BaseQuantities" die Standardwerte zu erhalten
            base_qto = qto.get("BaseQuantities", {})
            
            if element.is_a("IfcWall"):
                ref = qto.get("Qto_WallBaseQuantities", {}).get("NetSideArea", None)
            elif element.is_a("IfcSlab"):
                ref = base_qto.get("NetFootprintArea", None)
            elif element.is_a("IfcColumn"):
                ref = base_qto.get("NominalHeight", None)
            elif element.is_a("IfcBeam"):
                ref = base_qto.get("NominalLength", None)
            else:
                ref = base_qto.get("NetVolume", None)
            
            row = {
                "GUID": element.GlobalId,
                "IFC_Type": element.is_a(),
                "Reference_Quantity": ref,
                "NetVolume": base_qto.get("NetVolume", None),
                "NominalLength": base_qto.get("NominalLength", None),
                "NominalWidth": base_qto.get("NominalWidth", None),
                "NominalHeight": base_qto.get("NominalHeight", None)
            }
            rows.append(row)
        except Exception as e:
            st.warning(f"Fehler bei Element {element.GlobalId}: {e}")
    return pd.DataFrame(rows)

def app(uploaded_files):
    st.header("Referenzmengen je IFC-Typ (Netto)")
    if not uploaded_files:
        st.warning("Bitte IFC-Datei(en) in der Sidebar hochladen.")
        return
        
    selected_file_name = st.selectbox(
        "IFC-Datei auswählen",
        [f.name for f in uploaded_files],
        key="refq_select"
    )
    selected_file = [f for f in uploaded_files if f.name == selected_file_name][0]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(selected_file.getbuffer())
        ifc_path = tmp.name
    
    if st.button("Referenzmengen berechnen"):
        ifc_file = ifcopenshell.open(ifc_path)
        df = calculate_reference_quantities(ifc_file)
        st.dataframe(df.head(10), use_container_width=True)
