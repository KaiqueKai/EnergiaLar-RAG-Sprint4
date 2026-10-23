"""Carrega prompts versionados em mensagens SYSTEM e HUMAN separadas."""
from langchain_core.prompts import ChatPromptTemplate
from .settings import PROMPTS_DIR
from .prompt_format import split_prompt

VALID_VERSIONS = {"v1": "rag_v1.md", "v2": "rag_v2.md", "v3": "rag_v3.md"}


def load_prompt(version: str = "v2") -> ChatPromptTemplate:
    key = (version or "v2").lower().strip()
    if key not in VALID_VERSIONS:
        raise ValueError(f"Versão de prompt inválida: {version}. Use: {', '.join(VALID_VERSIONS)}")
    path = PROMPTS_DIR / VALID_VERSIONS[key]
    if not path.is_file():
        raise FileNotFoundError(f"Prompt não encontrado: {path}")
    system_text, human_text = split_prompt(path.read_text(encoding="utf-8"))
    return ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("human", human_text),
    ])
