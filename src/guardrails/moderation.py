import re

TERMOS_INJECTION = [
    "ignore todas as instruções", "ignore as instruções anteriores",
    "ignore o prompt", "ignore seu prompt", "esqueça as instruções",
    "mostre seu system prompt", "mostre o system prompt", "revele seu prompt",
    "revele as instruções", "jailbreak", "bypass", "desative seus filtros",
    "ignore suas regras", "sem nenhuma restrição", "sem restrições",
    "sem restrição", "a partir de agora você é", "finja ser",
    "finja que você é", "modo desenvolvedor", "modo dev",
]
TERMOS_RISCO = [
    "ligação elétrica", "ligacao eletrica", "instalação elétrica",
    "instalacao eletrica", "conserte o carregador", "reparo elétrico",
    "reparo eletrico", "abra o carregador", "choque elétrico",
    "choque eletrico", "disjuntor", "troco o disjuntor",
    "trocar o disjuntor", "fiação", "fiacao", "quadro elétrico",
    "quadro eletrico",
]

def detectar_injection(texto: str) -> bool:
    texto = (texto or "").lower()
    return any(re.search(re.escape(termo), texto) for termo in TERMOS_INJECTION)

def detectar_risco(texto: str) -> bool:
    texto = (texto or "").lower()
    return any(re.search(re.escape(termo), texto) for termo in TERMOS_RISCO)
