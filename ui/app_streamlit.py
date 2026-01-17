import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import streamlit as st
from services.funding_service import find_funding_programs
from services.resource_service import extract_resources
from utils.streamlit_helpers import get_category_color

# --- NEW IMPORTS FOR RAG INGESTION ---
from services.ingestion_service import extract_program_from_html
from services.vector_service import add_program_to_index, get_all_stored_programs, delete_collection
import json
import pandas as pd

# -------------------------------
# Helper Functions
# -------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (FundingFinder/1.0)"
}

def verify_link(url: str) -> bool:
    try:
        # Erst HEAD (schnell)
        r = requests.head(url, allow_redirects=True, timeout=6, headers=HEADERS)
        if r.status_code < 400:
            return True
        # Fallback: GET (viele Behörden blocken HEAD)
        r = requests.get(url, allow_redirects=True, timeout=8, headers=HEADERS, stream=True)
        return r.status_code < 400
    except requests.RequestException:
        return False

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="🌱 Förderfinder", layout="wide")
st.title("🌿 Intelligenter Begrünungs-Förderfinder")

# Create Tabs to separate User Search from Admin Import
tab_search, tab_admin = st.tabs(["🔍 Förder-Suche", "⚙️ Admin / Daten-Import"])

# =========================================================
# TAB 1: USER SEARCH (Your existing code)
# =========================================================
with tab_search:
    st.markdown("### Finde passende Förderungen für dein Projekt")
    
    # --- Formular ---
    with st.form("foerder_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            stadt = st.text_input("📍 Stadt oder Gemeinde")
            art = st.selectbox("🌱 Art der Begrünung", [
                "Dachbegrünung", "Fassadenbegrünung", "Entsiegelung", "Nicht sicher"
            ])
            gebaeude = st.selectbox("🏠 Gebäudetyp", [
                "Einfamilienhaus", "Mehrfamilienhaus", "Gewerbe", "Öffentlich"
            ])
        
        with col2:
            eigentum = st.selectbox("🔑 Eigentumsverhältnis", [
                "Eigentümer", "Mieter mit Zustimmung", "WEG / Hausverwaltung"
            ])
            status = st.selectbox("🛠️ Projektstatus", [
                "Planung", "Vor Umsetzung", "Bereits umgesetzt"
            ])
            prior = st.selectbox("⭐ Priorität", [
                "Maximale Förderung", "Einfache Antragstellung", "Beratung"
            ])
            
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🔍 Programme finden", use_container_width=True)

    # --- Ergebnisse ---
    if submitted:
        with st.spinner("⏳ Förderprogramme werden ermittelt... (Datenbank & KI)"):
            # 1. Service Aufruf: Gibt jetzt ein Dictionary zurück {"response": ..., "sources": ...}
            full_result = find_funding_programs(stadt, art, gebaeude, eigentum, status, prior)
            
            # 2. Entpacken der Daten
            result_data = full_result["response"]  # Das Pydantic-Objekt (die Antwort)
            source_docs = full_result["sources"]   # Die RAG-Beweise (die Dokumente)

        # --- NEU: RAG-Transparenz Box ---
        # Zeigt an, welche Datenbank-Einträge genutzt wurden (nur wenn vorhanden)
        if source_docs:
            with st.expander(f"📚 RAG-Kontext: {len(source_docs)} Quellen aus der Datenbank genutzt", expanded=False):
                for i, doc in enumerate(source_docs):
                    meta = doc.metadata
                    st.markdown(f"**{i+1}. {meta.get('name', 'Unbekanntes Programm')}**")
                    # Zeige Region und gefundene URL an
                    st.caption(f"📍 Region: {meta.get('regionen', 'N/A')} | 🔗 URL: {meta.get('url', 'N/A')}")
                    
                    # Optional: Button um den Text zu lesen, den die KI bekommen hat
                    with st.popover("📄 Gelesenen Text anzeigen"):
                        st.text(doc.page_content)
                    st.divider()
        elif result_data.programme:
            st.info("ℹ️ Keine lokalen Datenbank-Treffer. Antwort basiert auf allgemeinem LLM-Wissen.")

        # --- Bestehende Logik (angepasst auf 'result_data') ---
        if not result_data.programme:
            st.warning("Keine Programme gefunden.")
        else:
            st.divider()
            st.header("📊 Ergebnisse")
            valid_programs = []

            # Link Verification
            progress_text = "Prüfe Verfügbarkeit der Links..."
            my_bar = st.progress(0, text=progress_text)
            
            # WICHTIG: Hier nutzen wir jetzt 'result_data.programme'
            total_links = sum([len(p.links) for p in result_data.programme])
            checked_links = 0

            for p in result_data.programme:
                valid_links = []
                for link in p.links:
                    if verify_link(link):
                        valid_links.append(link)
                    
                    # Update progress bar
                    checked_links += 1
                    if total_links > 0:
                        my_bar.progress(checked_links / total_links, text=progress_text)

                if valid_links:
                    p.links = valid_links  # 🔥 nur funktionierende Links behalten
                    valid_programs.append(p)
                else:
                    print(f"Programm verworfen (keine gültigen Links): {p.name}")

            my_bar.empty() # Remove progress bar

            # Display Results
            for idx, p in enumerate(valid_programs):
                color = get_category_color(p.ebene)

                # Card-Layout
                with st.container():
                    st.markdown(f"""
                        <div style='border-left: 6px solid {color}; padding: 12px; margin-bottom:10px; border-radius:8px; background-color:#f9f9f9;'>
                        <h3>{p.name} ({p.ebene})</h3>
                        <p><b>Förderhöhe:</b> {p.foerderhoehe}</p>
                        <p><b>Warum geeignet:</b> {p.begruendung}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Expander für Details
                    with st.expander("🔍 Details anzeigen"):
                        st.markdown("### Voraussetzungen")
                        for v in p.voraussetzungen:
                            st.write(f"- {v}")

                        st.markdown("### 🔗 Offizielle Quellen")
                        if p.links:
                            for link in p.links:
                                st.markdown(f"[🌐 Webseite öffnen]({link})")
                        else:
                            st.warning("Mindestens eine Referenz muss vorhanden sein!")

# =========================================================
# TAB 2: ADMIN / DATA INGESTION (New RAG Code)
# =========================================================
with tab_admin:
    st.header("⚙️ Verwaltungs-Dashboard")
    
    # We create two sub-tabs here: one for feeding data, one for viewing data
    sub_upload, sub_view = st.tabs(["📤 Upload & Import", "💾 Datenbank Inspektor"])

    # --- SUB-TAB 1: UPLOAD (Your existing logic) ---
    with sub_upload:
        st.subheader("📂 HTML Import")
        st.info(
            "Hier kannst du HTML-Dateien von 'foerderdatenbank.de' (Detailansicht) hochladen. "
            "Die KI extrahiert die Daten automatisch und speichert sie in der Vektor-Datenbank."
        )

        uploaded_files = st.file_uploader(
            "HTML-Dateien hier ablegen (Mehrfachauswahl möglich)", 
            type=["html", "htm"], 
            accept_multiple_files=True
        )

        if uploaded_files and st.button(f"🚀 Start: {len(uploaded_files)} Dateien verarbeiten"):
            
            # UI Elements for Progress
            progress_bar = st.progress(0)
            status_box = st.empty()
            log_container = st.container(height=300, border=True)
            
            success_count = 0
            error_count = 0
            
            for i, file in enumerate(uploaded_files):
                # Update Status
                status_box.markdown(f"**Bearbeite:** `{file.name}`...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                try:
                    # 1. Read File
                    html_bytes = file.read()
                    html_string = html_bytes.decode("utf-8", errors="ignore")
                    
                    # 2. Extract Data using LLM
                    program_data = extract_program_from_html(html_string, file.name)
                    
                    if program_data:
                        # 3. Store in Vector DB
                        add_program_to_index(program_data)
                        
                        success_count += 1
                        log_container.success(f"✅ **Gespeichert:** {program_data.name}")
                    else:
                        error_count += 1
                        log_container.warning(f"⚠️ **Leer/Ignoriert:** {file.name}")
                        
                except Exception as e:
                    error_count += 1
                    log_container.error(f"❌ **Fehler bei {file.name}:** {str(e)}")

            # Final Report
            status_box.empty()
            st.success(f"🎉 Import abgeschlossen! {success_count} Programme hinzugefügt.")
            if error_count > 0:
                st.error(f"{error_count} Dateien konnten nicht verarbeitet werden.")

    # --- SUB-TAB 2: DATABASE INSPECTOR (New Visualization) ---
    with sub_view:
        st.subheader("🧐 Einblick in den Vektor-Speicher")
        
        # 1. Load Data from ChromaDB
        stored_items = get_all_stored_programs()
        
        col1, col2 = st.columns([1, 3])
        col1.metric("Gespeicherte Programme", len(stored_items))
        
        # Danger Zone Button
        if col2.button("🗑️ Datenbank komplett löschen (Reset)", type="primary"):
            delete_collection()
            st.rerun()

        if stored_items:
            # 2. Overview Table (DataFrame)
            # We flatten the metadata to make it displayable in a table
            table_data = []
            for item in stored_items:
                meta = item['metadata']
                table_data.append({
                    "Name": meta.get("name", "N/A"),
                    "Region": meta.get("regionen", "N/A"),
                    "Kategorie": meta.get("kategorien", "N/A"),
                    "ID": item['id']
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            
            # 3. Detailed View
            st.markdown("### 🔍 Detail-Ansicht & Validierung")
            
            selected_id_label = st.selectbox(
                "Wähle ein Programm zum Prüfen:", 
                options=df["ID"],
                format_func=lambda x: next((d['Name'] for d in table_data if d['ID'] == x), x)
            )
            
            # Retrieve the full object for the selected ID
            if selected_id_label:
                selected_item = next((item for item in stored_items if item['id'] == selected_id_label), None)
                
                if selected_item:
                    c_left, c_right = st.columns(2)
                    
                    with c_left:
                        st.markdown("**🤖 Extrahierte Daten (JSON)**")
                        st.caption("Strukturierte Daten, die das LLM erkannt hat.")
                        
                        # Parse JSON string from metadata if it exists
                        try:
                            json_data = json.loads(selected_item['metadata'].get('json_dump', '{}'))
                            st.json(json_data)
                        except:
                            st.warning("Kein Raw-JSON in Metadaten gefunden.")
                            st.write(selected_item['metadata'])

                    with c_right:
                        st.markdown("**🧠 Vektor-Kontext (Text)**")
                        st.caption("Der reine Text, der für die Suche verwendet wird.")
                        st.text_area("Content", selected_item['content'], height=400)
        else:
            st.info("Die Datenbank ist leer. Bitte lade Dateien im 'Upload'-Tab hoch.")