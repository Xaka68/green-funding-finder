import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from llm.chains import build_funding_chain

# 1. Environment laden (Wichtig für API Key)
load_dotenv()

# 2. Datenbank initialisieren (Mit OpenAI Embeddings)
embeddings = OpenAIEmbeddings()

vector_db = Chroma(
    collection_name="green_funding_programs",
    embedding_function=embeddings,
    persist_directory="./data/chroma_db"
)

# 3. Chain bauen
chain = build_funding_chain()

def retrieve_relevant_programs(stadt: str, begruenung: str, k: int = 4):
    """
    Sucht in der Vektor-DB nach passenden Programmen.
    Gibt Text (für LLM) UND Dokumente (für UI-Anzeige) zurück.
    """
    query = f"Förderprogramm für {begruenung} in {stadt} oder bundesweit"
    print(f"🔎 Suche Kontext für: {query}")
    
    # Suche in der Datenbank
    source_docs = vector_db.similarity_search(query, k=k)
    
    # Kontext-String bauen
    if source_docs:
        context_text = "\n\n".join([
            f"--- QUELLE {i+1} ({doc.metadata.get('name', 'Unbekannt')}) ---\n{doc.page_content}" 
            for i, doc in enumerate(source_docs)
        ])
    else:
        context_text = "Keine spezifischen lokalen Programme in der Datenbank gefunden."
    
    return context_text, source_docs

def find_funding_programs(
    stadt: str,
    begruenung: str,
    gebaeude: str,
    eigentum: str,
    status: str,
    prioritaet: str
):
    print(f"🔎 Searching RAG for: {begruenung} in {stadt}...")
    
    # 1. RETRIEVE: Hole Daten & Quellen
    context, sources = retrieve_relevant_programs(stadt, begruenung)
    
    # Fallback, falls DB leer ist
    if not sources:
        print("⚠️ Warning: No relevant documents found in Vector DB.")
        context = "Keine spezifischen lokalen Programme in der Datenbank gefunden. Antworte basierend auf allgemeinem Wissen, aber weise darauf hin."

    # 2. AUGMENT & GENERATE: Generiere Antwort mit LLM
    ai_response = chain.invoke({
        "context": context,
        "stadt": stadt,
        "begruenung": begruenung,
        "gebaeude": gebaeude,
        "eigentum": eigentum,
        "status": status,
        "prioritaet": prioritaet,
    })
    
    # 3. RETURN: Beides zurückgeben (Antwort + Beweise)
    return {
        "response": ai_response,
        "sources": sources
    }