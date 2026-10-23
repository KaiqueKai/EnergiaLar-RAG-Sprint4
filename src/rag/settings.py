"""Configuração central, sem qualquer credencial hard-coded."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env", override=False)

KNOWLEDGE_BASE_DIR = ROOT_DIR / "data" / "knowledge_base"
PROMPTS_DIR = ROOT_DIR / "prompts"
STORAGE_DIR = ROOT_DIR / "storage"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", os.getenv("OLLAMA_BASE_URL", "https://ollama.com")).strip().rstrip("/")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma4:31b").strip()
# As variáveis MODEL_PRIMARY/MODEL_SECONDARY pertencem ao chatbot Sprint 3 e não devem
# alterar a seleção padrão do RAG. O RAG usa nomes de configuração próprios.
_DEFAULT_COMPARISON_MODELS = f"{CHAT_MODEL},{os.getenv('RAG_MODEL_SECONDARY', 'gpt-oss:20b')}"
COMPARISON_MODELS = [m.strip() for m in os.getenv("COMPARISON_MODELS", _DEFAULT_COMPARISON_MODELS).split(",") if m.strip()]
EMBEDDING_HOST = os.getenv("EMBEDDING_HOST", "http://localhost:11434").strip().rstrip("/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text").strip()

CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", "storage/chroma"))
if not CHROMA_PERSIST_DIR.is_absolute():
    CHROMA_PERSIST_DIR = ROOT_DIR / CHROMA_PERSIST_DIR

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "8"))
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.15"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "600"))
COLLECTION_NAME = "energialar_knowledge_v1"


def validate_config(require_api_key: bool = True) -> None:
    """Valida configurações básicas sem revelar o valor do segredo."""
    if not OLLAMA_HOST.startswith(("https://", "http://")):
        raise ValueError("OLLAMA_HOST precisa começar com https:// ou http://.")
    if not EMBEDDING_HOST.startswith(("https://", "http://")):
        raise ValueError("EMBEDDING_HOST precisa começar com https:// ou http://.")
    if not EMBEDDING_MODEL:
        raise ValueError("EMBEDDING_MODEL está vazio.")
    if CHUNK_SIZE < 100 or CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError("Configuração de chunk inválida: verifique CHUNK_SIZE e CHUNK_OVERLAP.")
    if not 0 <= MIN_RELEVANCE_SCORE <= 1:
        raise ValueError("MIN_RELEVANCE_SCORE precisa estar entre 0 e 1.")
    if require_api_key and (OLLAMA_HOST.startswith("https://") or EMBEDDING_HOST.startswith("https://")) and (not OLLAMA_API_KEY or OLLAMA_API_KEY == "COLE_SUA_CHAVE_AQUI"):
        raise ValueError("Configure OLLAMA_API_KEY no arquivo .env. A chave não deve ser enviada ao GitHub.")
