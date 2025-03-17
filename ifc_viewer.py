import streamlit as st
import streamlit.components.v1 as components
import base64

def app(ifc_files):
    st.header("IFC 3D Viewer")
    st.markdown("Interaktive Darstellung von IFC-Modellen mit IFC.js.")

    # Falls Dateien hochgeladen wurden, Auswahl anbieten
    if ifc_files:
        file_options = {file.name: file for file in ifc_files}
        selected_file_name = st.selectbox("Wählen Sie eine IFC-Datei", list(file_options.keys()))
        selected_file = file_options[selected_file_name]
        # Datei als Base64 kodieren und Data-URL erstellen
        file_bytes = selected_file.read()
        encoded = base64.b64encode(file_bytes).decode("utf-8")
        ifc_file_url = f"data:application/octet-stream;base64,{encoded}"
    else:
        st.info("Keine IFC-Datei hochgeladen. Es wird ein Beispielmodell geladen.")
        ifc_file_url = "https://raw.githubusercontent.com/IFCjs/test-ifc-files/main/IFC/01.ifc"

    viewer_html = f"""
    <div id="viewer-container" style="width: 100%; height: 600px;"></div>
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/web-ifc-viewer@1.0.218/dist/IFC.js"></script>
    <script>
        // Viewer initialisieren
        const container = document.getElementById('viewer-container');
        const viewer = new IfcViewerAPI({{ container: container, backgroundColor: new THREE.Color(0xeeeeee) }});
        viewer.axes.setAxes();
        viewer.grid.setGrid();

        // IFC-Modell laden
        async function loadIfcModel(url) {{
            await viewer.IFC.setWasmPath("https://cdn.jsdelivr.net/npm/web-ifc@0.0.42/");
            await viewer.IFC.loadIfcUrl(url);
            viewer.camera.fitCameraToSelection();
        }}
        loadIfcModel("{ifc_file_url}");

        // Objektauswahl mit Anzeige der GlobalId per Doppelklick
        window.addEventListener('dblclick', async (event) => {{
            const result = await viewer.IFC.pickIfcItem(true);
            if (result) {{
                const props = await viewer.IFC.getProperties(result.modelID, result.id, true);
                const globalId = props.GlobalId ? props.GlobalId.value : "(n/a)";
                let infoDiv = document.getElementById('ifc-info');
                if (!infoDiv) {{
                    infoDiv = document.createElement('div');
                    infoDiv.id = 'ifc-info';
                    infoDiv.style.position = 'absolute';
                    infoDiv.style.top = '10px';
                    infoDiv.style.left = '10px';
                    infoDiv.style.padding = '5px 10px';
                    infoDiv.style.background = '#ffffffcc';
                    infoDiv.style.border = '1px solid #555';
                    document.body.appendChild(infoDiv);
                }}
                infoDiv.innerHTML = `<b>Ausgewählte GlobalId:</b> ${{{{globalId}}}}`;
            }}
        }});

        // Aktivierung der Schnittebene
        viewer.clipper.active = true;
        viewer.clipper.createPlane();
    </script>
    """

    components.html(viewer_html, height=650)
