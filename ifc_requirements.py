import streamlit as st

def app(ifc_files=None):
    st.header("IFC Hub Anforderungen & Übersicht")
    st.markdown("Dieser Hub bietet diverse Operationen mit IFC-Daten. Im Folgenden die Übersicht:")

    if ifc_files:
        st.markdown("**Hochgeladene IFC-Dateien:**")
        for file in ifc_files:
            st.markdown(f"- {file.name}")
    else:
        st.info("Keine IFC-Dateien hochgeladen. Nutzen Sie die Sidebar zum Hochladen.")

    with st.expander("Tool-Erklärungen"):
        st.markdown(
            """
            **1. IFC Element Remover:**  
            Entfernt IFC-Elemente anhand ihrer GlobalIds.  
            *Beispiel:* Entfernen fehlerhafter Bauelemente aus einem Modell.
            
            **Weitere Tools (in Planung):**  
            - IFC Daten laden: Import und Validierung von IFC-Dateien.  
            - IFC Visualisierung: Interaktive 3D-Ansichten der Modelle.  
            - IFC Bearbeitung: Anpassungen und Optimierungen an den IFC-Daten.
            """
        )
