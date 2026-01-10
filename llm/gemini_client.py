from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, TEMPERATURE

def get_gemini_llm():
    """
    Gemini LLM mit explizit aktivierter Google-Suche (Grounding)
    """

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=TEMPERATURE,
        convert_system_message_to_human=True,

        # 🔥 DAS IST DER ENTSCHEIDENDE TEIL
        tools=["google_search"],

        # Optional, aber empfohlen
        model_kwargs={
            "response_mime_type": "application/json"
        }
    )
