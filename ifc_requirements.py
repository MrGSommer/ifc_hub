import streamlit as st

def app():
    st.header("IFC Hub Anforderungen & Übersicht")
    st.markdown("Dieser Hub bietet diverse Operationen mit IFC-Daten. Im Folgenden die Übersicht:")

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
