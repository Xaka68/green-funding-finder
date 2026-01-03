import re

PDF_REGEX = r"http[s]?://\S+\.pdf"
LINK_REGEX = r"http[s]?://\S+"

def extract_resources(text: str) -> dict:
    pdfs = re.findall(PDF_REGEX, text)
    links = re.findall(LINK_REGEX, text)

    return {
        "pdfs": list(set(pdfs)),
        "links": list(set(links) - set(pdfs))
    }
