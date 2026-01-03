import streamlit as st
from ui.streamlit_ui import render_program
from services.funding_service import find_funding_programs
from services.resource_service import extract_resources

st.set_page_config(page_title="🌱 Förderfinder", layout="wide")

st.title("🌿 Intelligenter Begrünungs-Förderfinder")

# -------------------------------
# DETAILSEITE
# -------------------------------
if "selected_program" in st.session_state:
    p = st.session_state["selected_program"]

    st.header(f"📄 {p.name}")
    st.markdown(f"**Ebene:** {p.ebene}")
    st.markdown(f"**Förderhöhe:** {p.foerderhoehe}")

    st.markdown("### Warum dieses Programm passt")
    st.write(p.begruendung)

    st.markdown("### Voraussetzungen")
    for v in p.voraussetzungen:
        st.write(f"- {v}")

    if p.links or p.pdfs:
        st.markdown("### 🔗 Offizielle Quellen")

        for link in p.links:
            st.markdown(f"[🌐 Webseite öffnen]({link})")

        for pdf in p.pdfs:
            st.markdown(f"[📄 PDF öffnen]({pdf})")

    if st.button("⬅️ Zurück zur Übersicht"):
        del st.session_state["selected_program"]

# -------------------------------
# ÜBERSICHT / FORMULAR
# -------------------------------
else:
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

    if submitted:
        with st.spinner("⏳ Förderprogramme werden ermittelt..."):
            result = find_funding_programs(
                stadt, art, gebaeude, eigentum, status, prior
            )

        st.header("📊 Ergebnisse")

        if not result.programme:
            st.warning("Keine Programme gefunden.")
        else:
            for p in result.programme:
                all_text = " ".join([p.begruendung] + p.voraussetzungen)
                res = extract_resources(all_text)
                p.links = res["links"]
                p.pdfs = res["pdfs"]

                render_program(p)
