import streamlit as st
from streamlit_3d_model import st_3d_model

def app(uploaded_files):
    st.header("3D Viewer (glTF)")
    st.markdown(
        "Dieser Viewer nutzt *streamlit-3d-model* zur Darstellung von glTF/GLB-Modellen. "
        "Hinweis: IFC-Dateien müssen zuvor in das glTF-Format konvertiert werden."
    )
    
    # Auswahl: Falls glTF/GLB-Dateien hochgeladen wurden, diese verwenden.
    gltf_files = [f for f in uploaded_files if f.name.lower().endswith(('.gltf', '.glb'))] if uploaded_files else []
    
    if gltf_files:
        file_options = {f.name: f for f in gltf_files}
        selected_file_name = st.selectbox("Wählen Sie ein glTF-Modell", list(file_options.keys()), key="gltf_viewer_selectbox")
        selected_file = file_options[selected_file_name]
        st_3d_model(selected_file, height=600)
    else:
        st.info("Keine glTF-Datei hochgeladen. Es wird ein Beispielmodell geladen.")
        example_url = "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/house/house.glb"
        st_3d_model(example_url, height=600)
