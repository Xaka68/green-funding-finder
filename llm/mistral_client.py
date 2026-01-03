from langchain_mistralai.chat_models import ChatMistralAI
from config import MISTRAL_API_KEY, MISTRAL_MODEL, TEMPERATURE

def get_mistral_llm():
    print("MISTRAL_API_KEY:", MISTRAL_API_KEY)
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=TEMPERATURE
    )
