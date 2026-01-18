import os
import re
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from utils.output_schema import FoerderProgrammDB

load_dotenv()

INDEX_NAME = "green-funding"

def get_vector_store():
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
    text = text.lower()
    
    # 1. Deutsche Umlaute ersetzen
    mapping = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in mapping.items():
        text = text.replace(k, v)
        
    # 2. Alles entfernen, was kein Buchstabe, Zahl oder Unterstrich ist
    # (Entfernt auch Leerzeichen und ersetzt sie durch Nichts, wir machen das vorher)
    text = text.replace(" ", "_")
    text = re.sub(r'[^a-z0-9_]', '', text)
    
    return text

def add_program_to_index(program: FoerderProgrammDB):
    vector_db = get_vector_store()
    
    # 1. Content bauen (Link direkt im Text!)
    page_content = (
        f"Programm: {program.name}\n"
        f"Link: {program.quelle_url}\n"
        f"Beschreibung: {program.beschreibung}\n"
        f"Voraussetzungen: {', '.join(program.voraussetzungen)}\n"
        f"Förderhöhe: {program.foerderhoehe}"
    )
    
    # 2. Metadaten
    metadata = {
        "name": program.name,
        "regionen": ", ".join(program.region),
        "kategorien": ", ".join(program.kategorie),
        "url": program.quelle_url,
        "json_dump": program.json()
    }
    
    # 3. ID sicher machen (FIX FÜR ERROR 400)
    doc_id = sanitize_id(program.name)
    
    # 4. In die Cloud hochladen
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
    Workaround für Pinecone Admin-View (Dummy Search)
    """
    db = get_vector_store()
    results = []
    
    try:
        # Suche nach "Förderung", um "alle" (max 100) Einträge zu finden
        docs = db.similarity_search("Förderung", k=100)
        
        for doc in docs:
            results.append({
                "id": sanitize_id(doc.metadata.get("name", "unknown")), 
                "metadata": doc.metadata,
                "content": doc.page_content
            })
            
    except Exception as e:
        print(f"⚠️ Warnung: Konnte Admin-Liste nicht laden: {e}")
        return []
        
    return results

def delete_collection():
    vector_db = get_vector_store()
    vector_db.delete(delete_all=True)
    print("🗑️ Pinecone Index geleert.")