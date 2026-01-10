from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from llm.output_schema import FoerderAntwort

# Parser für strukturierte Ausgabe
parser = PydanticOutputParser(pydantic_object=FoerderAntwort)

FUNDING_PROMPT = PromptTemplate(
    input_variables=["stadt","begruenung","gebaeude","eigentum","status","prioritaet"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
Du bist ein professioneller Recherche-Agent für Förderprogramme in Deutschland mit Zugriff auf Websuche.

Deine Aufgabe ist es, systematisch möglichst VIELE reale Förderprogramme zu finden.

Suche aktiv in diesen Ebenen (alle prüfen!):
1. Kommune ({stadt})
2. Landkreis / Region
3. Bundesland
4. Bund
5. Stiftungen / öffentliche Fonds
6. Versorger & kommunale Betriebe
7. EU-Programme (wenn relevant)

Nutzerangaben:
- Standort: {stadt}
- Art der Begrünung: {begruenung}
- Gebäudetyp: {gebaeude}
- Eigentum: {eigentum}
- Projektstatus: {status}
- Priorität: {prioritaet}

PFLICHTREGELN:
- Antworte AUSSCHLIESSLICH im JSON-Format.
- Gib NUR valides JSON zurück.
- KEIN Fließtext vor oder nach dem JSON.
- KEINE Kommentare.
- KEINE Quellenmarker wie [1], [2], etc.
- KEINE doppelten geschweiften Klammern.
- Strings dürfen keine Zeilen mit ``` enthalten.

HARTE REGELN:
- Nenne nur reale Programme.
- JEDES Programm MUSS mindestens eine funktionierende offizielle Quelle haben:
  - Stadt / Landes / Bundes-Webseite oder offizielles PDF
- Wenn du keinen funktionierenden Link findest → NICHT ausgeben.
- Führe so viele passende Programme wie möglich auf.
- Prüfe mehrere Suchanfragen (z. B. „{stadt} Förderprogramm Dachbegrünung“, „Begrünung Zuschuss {stadt}“, „Klimaanpassung Förderung Bayern Dach“).

ZIEL:
Maximale Vollständigkeit + nur verifizierbare Programme.

{format_instructions}
"""
)

