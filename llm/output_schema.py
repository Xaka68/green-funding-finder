from pydantic import BaseModel, Field, validator
from typing import List, Optional


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
            "Informationen oder Antragsformulare zu finden sind. "
            "Programme ohne Links werden verworfen."
        )
    )

    pdfs: List[str] = Field(
        default_factory=list,
        description=(
            "Liste direkter Links zu offiziellen PDF-Dokumenten "
            "wie Förderrichtlinien oder Antragsunterlagen. Optional."
        )
    )

    @validator("links", pre=True, always=True)
    def filter_no_links(cls, v, values, **kwargs):
        """
        Wenn das Programm keine offiziellen Links hat, 
        dann soll es als None zurückgegeben werden,
        sodass wir dieses Programm im UI nicht anzeigen.
        """
        if not v or len(v) == 0:
            # Markieren, dass das Programm ungültig ist
            raise ValueError("Programm ohne offizielle Links – wird ignoriert")
        return v


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
            "Nur reale Programme mit offiziellen Links aufführen."
        )
    )

    hinweise: List[str] = Field(
        description=(
            "Zusätzliche Hinweise, Tipps oder Warnungen, z. B. "
            "'Förderbedingungen regelmäßig prüfen' oder "
            "'Antrag muss vor Projektbeginn gestellt werden'."
        )
    )
