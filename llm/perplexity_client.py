from langchain_openai import ChatOpenAI
from config import PERPLEXITY_API_KEY, TEMPERATURE

def get_perplexity_llm():
    return ChatOpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai",
        model="sonar-pro",
        temperature=TEMPERATURE
    )
