def format_response(response):
    text = f"## {response.ueberschrift}\n\n"

    if not response.programme:
        text += "❗ Leider konnte kein konkretes Förderprogramm identifiziert werden.\n\n"

    for p in response.programme:
        text += f"### 🌿 {p.name}\n"
        text += f"- **Ebene:** {p.ebene}\n"
        text += f"- **Warum passend:** {p.begruendung}\n"
        text += f"- **Förderhöhe:** {p.foerderhoehe}\n"
        text += f"- **Voraussetzungen:** {p.voraussetzungen}\n\n"

    text += f"---\n💡 **Hinweise:** {response.hinweise}"
    return text
