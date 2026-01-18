import os
import re
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from llm.output_schema import FoerderProgrammDB

load_dotenv()

# Konfiguration
INDEX_NAME = "green-funding"

def get_vector_store():
    # Wir verbinden uns mit der Cloud-DB (Pinecone)
    return PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=OpenAIEmbeddings()
    )

def sanitize_id(text: str) -> str:
    """
    Pinecone erlaubt nur ASCII-Zeichen in IDs.
    Wir wandeln deutsche Umlaute um und entfernen Sonderzeichen.
    Beispiel: "Münchener Gründach" -> "muenchener_gruendach"
    """
    if not text:
        return "unknown_id"
        
    text = text.lower()
    
    # 1. Deutsche Umlaute ersetzen
    mapping = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in mapping.items():
        text = text.replace(k, v)
        
    # 2. Alles entfernen, was kein Buchstabe, Zahl oder Unterstrich ist
    text = text.replace(" ", "_")
    text = re.sub(r'[^a-z0-9_]', '', text)
    
    return text

def add_program_to_index(program: FoerderProgrammDB):
    vector_db = get_vector_store()
    
    # 1. Erstelle den durchsuchbaren Text (Content)
    # Link wird direkt in den Text geschrieben, damit das LLM ihn sieht
    page_content = (
        f"Programm: {program.name}\n"
        f"Link: {program.quelle_url}\n"
        f"Beschreibung: {program.beschreibung}\n"
        f"Voraussetzungen: {', '.join(program.voraussetzungen)}\n"
        f"Förderhöhe: {program.foerderhoehe}"
    )
    
    # 2. Erstelle Metadaten
    metadata = {
        "name": program.name,
        "regionen": ", ".join(program.region),
        "kategorien": ", ".join(program.kategorie),
        "url": program.quelle_url,
        "json_dump": program.json()
    }
    
    # 3. ID erstellen & bereinigen (WICHTIG für Pinecone!)
    doc_id = sanitize_id(program.name)
    
    # 4. Speichern
    try:
        vector_db.add_documents(
            documents=[Document(page_content=page_content, metadata=metadata)],
            ids=[doc_id]
        )
        print(f"✅ Gespeichert in Pinecone: {doc_id}")
    except Exception as e:
        print(f"❌ Fehler beim Speichern von {program.name}: {e}")

def get_all_stored_programs():
    """
    Workaround für Pinecone: Da es kein .get() gibt, suchen wir nach 
    einem generischen Begriff und holen bis zu 100 Einträge.
    """
    db = get_vector_store()
    results = []
    
    try:
        # Trick: Wir suchen nach "Förderung", was in fast jedem Dokument vorkommt.
        docs = db.similarity_search("Förderung", k=100)
        
        for doc in docs:
            # Wir nutzen sanitize_id auch hier für Konsistenz
            safe_id = sanitize_id(doc.metadata.get("name", "unknown"))
            
            results.append({
                "id": safe_id, 
                "metadata": doc.metadata,
                "content": doc.page_content
            })
            
    except Exception as e:
        print(f"⚠️ Warnung: Konnte Admin-Liste nicht laden: {e}")
        return []
        
    return results

def delete_collection():
    """Löscht alle Vektoren im Pinecone Index."""
    try:
        db = get_vector_store()
        # Pinecone spezifischer Befehl zum Löschen aller Daten
        db.delete(delete_all=True)
        print("🗑️ Pinecone Index geleert.")
    except Exception as e:
        print(f"❌ Fehler beim Löschen der DB: {e}")