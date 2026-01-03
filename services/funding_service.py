from llm.chains import build_funding_chain

chain = build_funding_chain()

def find_funding_programs(
    stadt: str,
    begruenung: str,
    gebaeude: str,
    eigentum: str,
    status: str,
    prioritaet: str
):
    return chain.invoke({
        "stadt": stadt,
        "begruenung": begruenung,
        "gebaeude": gebaeude,
        "eigentum": eigentum,
        "status": status,
        "prioritaet": prioritaet,
    })
