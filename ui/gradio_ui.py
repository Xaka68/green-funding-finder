import gradio as gr
from services.funding_service import find_funding_programs
from utils.text_formatting import format_response
from config import APP_TITLE

def ui_handler(
    stadt, begruenung, gebaeude, eigentum, status, prioritaet
):
    response = find_funding_programs(
        stadt, begruenung, gebaeude, eigentum, status, prioritaet
    )
    return format_response(response)

def launch_app():
    with gr.Blocks(title=APP_TITLE) as app:
        gr.Markdown("## 🌱 Intelligenter Begrünungs-Förderfinder")

        stadt = gr.Textbox(label="📍 Stadt oder Gemeinde")
        begruenung = gr.Dropdown(
            ["Dachbegrünung", "Fassadenbegrünung", "Entsiegelung", "Nicht sicher"],
            label="🌿 Art der Begrünung"
        )
        gebaeude = gr.Dropdown(
            ["Einfamilienhaus", "Mehrfamilienhaus", "Gewerbe", "Öffentlich"],
            label="🏠 Gebäudetyp"
        )
        eigentum = gr.Dropdown(
            ["Eigentümer", "Mieter mit Zustimmung", "WEG / Hausverwaltung"],
            label="🔑 Eigentumsverhältnis"
        )
        status = gr.Dropdown(
            ["Planung", "Vor Umsetzung", "Bereits umgesetzt"],
            label="🛠️ Projektstatus"
        )
        prioritaet = gr.Radio(
            ["Maximale Förderung", "Einfache Antragstellung", "Beratung"],
            label="⭐ Priorität"
        )

        btn = gr.Button("🔍 Förderprogramme finden")
        output = gr.Markdown()

        btn.click(
            ui_handler,
            inputs=[stadt, begruenung, gebaeude, eigentum, status, prioritaet],
            outputs=output
        )

    app.launch()
