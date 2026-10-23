"""Cliente de embeddings Ollama com host e credenciais configuráveis."""
from langchain_ollama import OllamaEmbeddings
from .settings import EMBEDDING_HOST, EMBEDDING_MODEL, OLLAMA_API_KEY


def create_embeddings():
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if EMBEDDING_HOST.startswith("https://") and OLLAMA_API_KEY else {}
    kwargs = {"headers": headers} if headers else {}
    # client_kwargs é suportado pela integração langchain-ollama atual.
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=EMBEDDING_HOST,
        client_kwargs=kwargs,
        validate_model_on_init=False,
    )
