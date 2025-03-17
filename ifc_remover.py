import streamlit as st
import ifcopenshell
import tempfile

def remove_ifc_elements(file_path, global_ids, output_path):
    try:
        ifc_file = ifcopenshell.open(file_path)
        removed_elements = []
        not_found_elements = []
        for global_id in global_ids:
            element = ifc_file.by_guid(global_id)
            if element:
                ifc_file.remove(element)
                removed_elements.append(global_id)
            else:
                not_found_elements.append(global_id)
        ifc_file.write(output_path)
        return True, removed_elements, not_found_elements
    except Exception as e:
        return False, [], [str(e)]

def parse_global_ids(ids_str):
    global_ids = ids_str.replace(" ", "").split(",")
    return [gid for gid in global_ids if gid]

def app():
    st.header("IFC Element Remover")
    st.markdown("Entfernen Sie IFC-Elemente anhand ihrer GlobalIds.")

    uploaded_file = st.file_uploader("Wählen Sie eine IFC-Datei", type=["ifc"])
    ids_input = st.text_input("GlobalIds (getrennt mit Komma)", placeholder="z.B. 3K5hj2,1Q8dF7,...")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_ifc:
            temp_ifc.write(uploaded_file.getbuffer())
            temp_ifc_path = temp_ifc.name
        st.success(f"Datei {uploaded_file.name} hochgeladen.")

        if st.button("GlobalIds prüfen"):
            global_ids = parse_global_ids(ids_input)
            if not global_ids:
                st.error("Bitte mindestens eine GlobalId eingeben.")
            else:
                try:
                    ifc_file = ifcopenshell.open(temp_ifc_path)
                    found = [gid for gid in global_ids if ifc_file.by_guid(gid)]
                    not_found = [gid for gid in global_ids if not ifc_file.by_guid(gid)]
                    st.info(f"Gefunden: {found}\nNicht gefunden: {not_found}")
                except Exception as e:
                    st.error(f"Fehler: {str(e)}")

        if st.button("Elemente entfernen"):
            global_ids = parse_global_ids(ids_input)
            if not global_ids:
                st.error("Bitte mindestens eine GlobalId eingeben.")
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_output:
                    output_path = temp_output.name
                success, removed, not_found = remove_ifc_elements(temp_ifc_path, global_ids, output_path)
                if success:
                    st.success(f"Entfernt: {removed}\nNicht gefunden: {not_found}")
                    with open(output_path, "rb") as f:
                        output_bytes = f.read()
                    st.download_button(
                        label="Modifizierte IFC-Datei herunterladen",
                        data=output_bytes,
                        file_name="modified.ifc",
                        mime="application/octet-stream"
                    )
                else:
                    st.error("Fehler: " + " ".join(not_found))
    else:
        st.warning("Bitte laden Sie eine IFC-Datei hoch.")
