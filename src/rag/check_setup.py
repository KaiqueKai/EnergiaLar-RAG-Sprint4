"""Verifica embeddings e chat separadamente, sem imprimir credenciais nem ocultar divergências."""
from .settings import EMBEDDING_HOST, EMBEDDING_MODEL, CHAT_MODEL, OLLAMA_HOST, validate_config
from .embeddings import create_embeddings
from .pipeline import _chat_model, _message_content
from .security import redact_sensitive_text
from .settings import OLLAMA_API_KEY


def main():
    validate_config(require_api_key=True)
    print(f"Ollama chat host: {OLLAMA_HOST}")
    print(f"Embedding host: {EMBEDDING_HOST}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    if EMBEDDING_HOST.startswith(("http://localhost", "http://127.0.0.1")):
        print("AVISO DE CONFORMIDADE: embeddings estão locais; isso NÃO atende literalmente ao trecho 'Ollama Cloud' do PDF.")
        print("Motivo documentado: Ollama Cloud não expõe endpoint público de embeddings; o chat continua na nuvem.")
    failures = []

    print("1/2 - Testando embeddings...")
    try:
        vector = create_embeddings().embed_query("Teste semântico do EnergiaLar Sprint 4")
        if not vector:
            raise RuntimeError("O endpoint não retornou vetor de embedding.")
        print(f"Embedding OK: dimensões={len(vector)}")
    except Exception as exc:
        detail = redact_sensitive_text(f"{type(exc).__name__}: {exc}", OLLAMA_API_KEY)
        failures.append("embeddings")
        print(f"Embedding FALHOU: {detail}")

    print(f"2/2 - Testando chat model={CHAT_MODEL}...")
    try:
        response = _chat_model(CHAT_MODEL).invoke("Responda somente: EnergiaLar OK")
        content = _message_content(response)
        if not content:
            raise RuntimeError("O endpoint não retornou texto de resposta.")
        safe_content = redact_sensitive_text(content, OLLAMA_API_KEY)
        print("Chat OK:", safe_content[:120])
    except Exception as exc:
        detail = redact_sensitive_text(f"{type(exc).__name__}: {exc}", OLLAMA_API_KEY)
        failures.append("chat")
        print(f"Chat FALHOU: {detail}")

    if failures:
        raise SystemExit(f"Configuração não validada. Falhas: {', '.join(failures)}. Não declare o pipeline pronto.")
    print("Configuração básica de embeddings e chat validada.")
    if EMBEDDING_HOST.startswith(("http://localhost", "http://127.0.0.1")):
        print("Requisito Cloud de embeddings: limitação técnica documentada; não marcar como cumprimento literal.")


if __name__ == "__main__":
    main()
