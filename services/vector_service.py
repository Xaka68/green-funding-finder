from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from llm.output_schema import FoerderProgrammDB
from langchain_pinecone import PineconeVectorStore

# Pfad wo die DB gespeichert wird
PERSIST_DIRECTORY = "./data/chroma_db"

INDEX_NAME = "green-funding"  # Exakt der Name aus deinem Screenshot

def get_vector_store():
    # Wir verbinden uns mit der Cloud-DB statt lokalem Ordner
    return PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=OpenAIEmbeddings()
    )

def add_program_to_index(program: FoerderProgrammDB):
    vector_db = get_vector_store()
    
    # 1. Erstelle den durchsuchbaren Text (Content)
    # Wir packen alle Keywords rein, nach denen man suchen könnte
    page_content = (
        f"Programm: {program.name}\n"
        f"Link: {program.quelle_url}\n"
        f"Beschreibung: {program.beschreibung}\n"
        f"Voraussetzungen: {', '.join(program.voraussetzungen)}\n"
        f"Förderhöhe: {program.foerderhoehe}"
    )
    
    # 2. Erstelle Metadaten (für Filterung: "Gib mir nur Programme in München")
    metadata = {
        "name": program.name,
        "regionen": ", ".join(program.region), # Chroma mag einfache Strings lieber als Listen in Metadaten
        "kategorien": ", ".join(program.kategorie),
        "url": program.quelle_url,
        "json_dump": program.json() # Wir speichern das ganze JSON als String, um es später schnell wiederherzustellen
    }
    
    # 3. ID erstellen (um Duplikate zu vermeiden)
    doc_id = program.name.replace(" ", "_").lower()
    
    # 4. Speichern
    vector_db.add_documents(
        documents=[Document(page_content=page_content, metadata=metadata)],
        ids=[doc_id]
    )
    print(f"✅ Gespeichert: {program.name}")

    # services/vector_service.py
# ... existing imports ...

def get_all_stored_programs():
    """
    Workaround für Pinecone: Da es kein .get() gibt, suchen wir nach 
    einem generischen Begriff und holen bis zu 100 Einträge.
    """
    db = get_vector_store()
    results = []
    
    try:
        # Trick: Wir suchen nach "Förderung", was in jedem deiner Dokumente vorkommt.
        # k=100 reicht für deinen Anwendungsfall locker aus.
        docs = db.similarity_search("Förderung", k=100)
        
        # Wir formatieren die Ergebnisse so, wie dein Frontend sie erwartet (wie bei Chroma)
        for doc in docs:
            results.append({
                "id": doc.metadata.get("name", "Unknown ID"), 
                "metadata": doc.metadata,
                "content": doc.page_content
            })
            
    except Exception as e:
        print(f"⚠️ Warnung: Konnte Admin-Liste nicht laden: {e}")
        # Leere Liste zurückgeben, damit die App nicht crasht
        return []
        
    return results

def delete_collection():
    """Clears the database (useful for resetting during development)."""
    db = get_vector_store()
    db.delete_collection()
    print("Database cleared.")