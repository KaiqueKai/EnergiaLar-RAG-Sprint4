"""
Constrói a chain conversacional em LCEL: ChatPromptTemplate | ChatOllama,
com saída estruturada aplicada após a memória.

Baseado no arquivo público src/chain/builder.py do repositório EnergiaLar.
A validação da chave é feita no momento de criar o modelo, e não durante o
import, para permitir executar testes unitários locais sem credenciais.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from src.schemas.consulta_recarga import ConsultaRecarga

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=False)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com").strip().rstrip("/")
MODEL_PRIMARY = os.getenv("MODEL_PRIMARY", "gpt-oss:20b").strip()
MODELOS_GRATUITOS = {
    "gemma4:31b", "gpt-oss:120b", "gpt-oss:20b",
    "nemotron-3-nano:30b", "nemotron-3-super", "nemotron-3-ultra",
}


def carregar_system_prompt(versao: str = "v3") -> str:
    caminho = BASE_DIR / "prompts" / f"system_prompt_{versao}.md"
    texto = caminho.read_text(encoding="utf-8").strip()
    if not texto:
        raise ValueError(f"Prompt vazio: {caminho}")
    return texto


def criar_modelo(modelo: str | None = None) -> ChatOllama:
    modelo = (modelo or MODEL_PRIMARY).strip()
    api_key = os.getenv("OLLAMA_API_KEY", "").strip()
    if not api_key or api_key in {"sua_chave_aqui", "COLE_SUA_CHAVE_AQUI"}:
        raise ValueError("OLLAMA_API_KEY não encontrada/configurada no .env")
    if modelo not in MODELOS_GRATUITOS:
        print(f"[AVISO] '{modelo}' não está na lista de modelos com uso gratuito conhecido.")
    return ChatOllama(
        model=modelo,
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
        top_p=0.9,
        num_predict=800,
        client_kwargs={"headers": {"Authorization": f"Bearer {api_key}"}},
    )


def criar_chain(modelo: str | None = None, versao_prompt: str = "v3"):
    parser = PydanticOutputParser(pydantic_object=ConsultaRecarga)
    system_prompt = carregar_system_prompt(versao_prompt)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="historico"),
        ("human", "{pergunta}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | criar_modelo(modelo), parser
