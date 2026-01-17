from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from llm.output_schema import FoerderProgrammDB

# Pfad wo die DB gespeichert wird
PERSIST_DIRECTORY = "./data/chroma_db"

def get_vector_store():
    return Chroma(
        collection_name="green_funding_programs",
        embedding_function=OpenAIEmbeddings(),
        persist_directory=PERSIST_DIRECTORY
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
    """Fetches all documents and metadata from the vector database."""
    db = get_vector_store()
    
    # ChromaDB allows fetching all data (limit to a reasonable number if DB grows huge)
    data = db.get() 
    
    # 'data' is a dict with keys: 'ids', 'embeddings', 'metadatas', 'documents'
    results = []
    if data and data['ids']:
        for i, doc_id in enumerate(data['ids']):
            results.append({
                "id": doc_id,
                "metadata": data['metadatas'][i],
                "content": data['documents'][i]
            })
    return results

def delete_collection():
    """Clears the database (useful for resetting during development)."""
    db = get_vector_store()
    db.delete_collection()
    print("Database cleared.")