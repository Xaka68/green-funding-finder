from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from llm.output_schema import FoerderAntwort

# Parser für strukturierte Ausgabe
parser = PydanticOutputParser(pydantic_object=FoerderAntwort)

FUNDING_PROMPT = PromptTemplate(
    input_variables=[
        "stadt","begruenung","gebaeude",
        "eigentum","status","prioritaet"
    ],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    },
    template="""
Du bist ein Experte für Umwelt- und Begrünungsförderprogramme in Deutschland.

Nutzerangaben:
- Standort: {stadt}
- Art der Begrünung: {begruenung}
- Gebäudetyp: {gebaeude}
- Eigentumsverhältnis: {eigentum}
- Projektstatus: {status}
- Priorität: {prioritaet}

REGELN:
- Nenne nur reale Förderprogramme
- Gib für jedes Programm möglichst URLs zu Richtlinien/Anträgen
- Nenne auch relevante PDFs, wenn öffentlich verlinkt
- Keine erfundenen Programme
- Wenn unsicher, sage es klar
- Bevorzuge kommunale Programme
- Erkläre verständlich und freundlich

{format_instructions}
"""
)

