from langchain_core.output_parsers import PydanticOutputParser

from llm.prompts import FUNDING_PROMPT
from llm.output_schema import FoerderAntwort
from llm.mistral_client import get_mistral_llm


def build_funding_chain():
    parser = PydanticOutputParser(pydantic_object=FoerderAntwort)
    llm = get_mistral_llm()

    chain = FUNDING_PROMPT | llm | parser

    return chain
