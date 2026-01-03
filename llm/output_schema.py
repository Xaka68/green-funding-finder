from pydantic import BaseModel, Field
from typing import List


class FoerderProgramm(BaseModel):
    name: str = Field(
        description="Offizieller Name des Förderprogramms, z. B. 'Förderprogramm Grüne Stadt München'"
    )

    ebene: str = Field(
        description=(
            "Förderebene des Programms. "
            "Erlaubte Werte sind z. B.: "
            "'Kommunal', 'Bundesland', 'Bund', 'EU', 'Stiftung', 'Sonstige'."
        )
    )

    begruendung: str = Field(
        description=(
            "Kurze, verständliche Erklärung, warum dieses Förderprogramm "
            "für das beschriebene Projekt geeignet ist."
        )
    )

    foerderhoehe: str = Field(
        description=(
            "Beschreibung der Förderhöhe oder Förderart, z. B. "
            "'Bis zu 50 % der förderfähigen Kosten, maximal 50.000 €'."
        )
    )

    voraussetzungen: List[str] = Field(
        description=(
            "Liste der wichtigsten Voraussetzungen für die Förderung. "
            "Jeder Eintrag soll ein klarer Stichpunkt sein, z. B. "
            "'Gebäude befindet sich im Stadtgebiet' oder "
            "'Antrag muss vor Maßnahmenbeginn gestellt werden'."
        )
    )

    links: List[str] = Field(
        default_factory=list,
        description=(
            "Liste von offiziellen Webseiten (URLs), auf denen weitere "
            "Informationen oder Antragsformulare zu finden sind."
        )
    )

    pdfs: List[str] = Field(
        default_factory=list,
        description=(
            "Liste direkter Links zu offiziellen PDF-Dokumenten "
            "wie Förderrichtlinien oder Antragsunterlagen."
        )
    )


class FoerderAntwort(BaseModel):
    ueberschrift: str = Field(
        description=(
            "Kurze, zusammenfassende Überschrift für das Ergebnis, "
            "z. B. 'Fördermöglichkeiten für Dachbegrünung in München'."
        )
    )

    programme: List[FoerderProgramm] = Field(
        description=(
            "Liste aller passenden Förderprogramme, die zur Nutzeranfrage passen. "
            "Nur reale Programme aufführen, keine erfundenen."
        )
    )

    hinweise: List[str] = Field(
        description=(
            "Zusätzliche Hinweise, Tipps oder Warnungen, z. B. "
            "'Förderbedingungen regelmäßig prüfen' oder "
            "'Antrag muss vor Projektbeginn gestellt werden'."
        )
    )
