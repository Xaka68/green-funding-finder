import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from llm.output_schema import FoerderProgrammDB

load_dotenv()

# Konfiguration: GPT-5 mini (oder gpt-4o-mini je nach API Verfügbarkeit)
# Stelle sicher, dass der Modellname exakt dem entspricht, was dein API-Provider erwartet.
llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
structured_llm = llm.with_structured_output(FoerderProgrammDB)

def find_canonical_url(soup: BeautifulSoup) -> str:
    """
    Versucht, die echte URL aus den HTML-Metadaten zu retten, 
    bevor der Text bereinigt wird.
    """
    # 1. <link rel="canonical"> (Der Goldstandard)
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        return canonical["href"]
    
    # 2. OpenGraph <meta property="og:url">
    og_url = soup.find("meta", property="og:url")
    if og_url and og_url.get("content"):
        return og_url["content"]
        
    # 3. Twitter Card <meta name="twitter:url">
    tw_url = soup.find("meta", name="twitter:url")
    if tw_url and tw_url.get("content"):
        return tw_url["content"]

    return None

def clean_html(soup: BeautifulSoup) -> str:
    """
    Entfernt Navigation, Footer und Skripte, um Tokens zu sparen.
    """
    try:
        # Entferne störende Elemente
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "svg", "noscript", "aside"]):
            tag.extract()
            
        # Text extrahieren mit Zeilenumbrüchen
        text = soup.get_text(separator="\n", strip=True)
        # Limit auf 30k Zeichen (ca. 7k Tokens), sicher für Mini-Modelle
        return text[:30000] 
    except Exception as e:
        print(f"Fehler beim Bereinigen: {e}")
        return ""

def extract_program_from_html(html_content: str, source_filename: str) -> FoerderProgrammDB:
    # 1. HTML Parsen
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 2. URL retten (Wichtig für den Link!)
    found_url = find_canonical_url(soup)
    url_hint = found_url if found_url else "Nicht im HTML gefunden"
    
    # 3. Text bereinigen
    clean_text = clean_html(soup)
    
    if not clean_text:
        return None

    # 4. Der Hybride Prompt (Dein Text + URL Logik)
    prompt = (
        f"Du bist ein Experte für Förderprogramme. Analysiere den folgenden Text einer Webseite "
        f"und extrahiere die Details des Förderprogramms strikt nach dem vorgegebenen Schema.\n\n"
        
        f"--- METADATEN ---\n"
        f"Dateiname: {source_filename}\n"
        f"Gefundene URL (aus HTML-Head): {url_hint}\n\n"
        
        f"--- ANWEISUNGEN ---\n"
        f"1. Suche nach dem Haupt-Förderprogramm auf dieser Seite.\n"
        f"2. Ignoriere Navigationselemente, Menüs, Footer oder Werbung.\n"
        f"3. WICHTIG ZUR URL: \n"
        f"   - Wir haben im HTML-Code die URL '{url_hint}' gefunden.\n"
        f"   - Wenn im Text keine *bessere* URL (z.B. direkt zum PDF) steht, NUTZE '{url_hint}' für die Felder 'links' und 'quelle_url'.\n"
        f"   - Schreibe NIEMALS 'siehe Webseite' oder 'Link nicht gefunden', wenn oben eine URL steht!\n\n"
        
        f"--- WEBSEITEN TEXT ---\n"
        f"{clean_text}"
    )

    try:
        # LLM Aufruf
        result = structured_llm.invoke(prompt)
        
        # 5. Sicherheitsnetz (Python-seitig)
        # Falls das LLM trotz Anweisung die URL vergisst, fügen wir sie hart ein.
        if found_url:
            # Check 'quelle_url'
            if not result.quelle_url or "siehe" in result.quelle_url.lower() or not result.quelle_url.startswith("http"):
                result.quelle_url = found_url
            
            # Check 'links' Liste
            if not result.links or (len(result.links) > 0 and "siehe" in result.links[0].lower()):
                result.links = [found_url]
            elif len(result.links) == 0:
                result.links = [found_url]
        
        return result

    except Exception as e:
        print(f"❌ Fehler bei der LLM Extraktion für {source_filename}: {e}")
        return None