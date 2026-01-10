import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests

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


import streamlit as st
from services.funding_service import find_funding_programs
from services.resource_service import extract_resources
from utils.streamlit_helpers import get_category_color

st.set_page_config(page_title="🌱 Förderfinder", layout="wide")
st.title("🌿 Intelligenter Begrünungs-Förderfinder")

# -------------------------------
# Formular
# -------------------------------
with st.form("foerder_form"):
    stadt = st.text_input("📍 Stadt oder Gemeinde")
    art = st.selectbox("🌱 Art der Begrünung", [
        "Dachbegrünung", "Fassadenbegrünung", "Entsiegelung", "Nicht sicher"
    ])
    gebaeude = st.selectbox("🏠 Gebäudetyp", [
        "Einfamilienhaus", "Mehrfamilienhaus", "Gewerbe", "Öffentlich"
    ])
    eigentum = st.selectbox("🔑 Eigentumsverhältnis", [
        "Eigentümer", "Mieter mit Zustimmung", "WEG / Hausverwaltung"
    ])
    status = st.selectbox("🛠️ Projektstatus", [
        "Planung", "Vor Umsetzung", "Bereits umgesetzt"
    ])
    prior = st.selectbox("⭐ Priorität", [
        "Maximale Förderung", "Einfache Antragstellung", "Beratung"
    ])
    submitted = st.form_submit_button("🔍 Programme finden")

# -------------------------------
# Ergebnisse
# -------------------------------
if submitted:
    with st.spinner("⏳ Förderprogramme werden ermittelt..."):
        result = find_funding_programs(stadt, art, gebaeude, eigentum, status, prior)

    if not result.programme:
        st.warning("Keine Programme gefunden.")
    else:
        st.header("📊 Ergebnisse")
        valid_programs = []

        for p in result.programme:
            valid_links = [link for link in p.links if verify_link(link)]

            if valid_links:
                p.links = valid_links  # 🔥 nur funktionierende Links behalten
                valid_programs.append(p)
            else:
                print(f"Programm verworfen (keine gültigen Links): {p.name}")
                print(f"Links waren: {p.links}")


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
