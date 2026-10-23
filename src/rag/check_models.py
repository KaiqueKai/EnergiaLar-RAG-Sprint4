"""Verifica modelos de chat da avaliação antes de gastar uma bateria completa."""
from __future__ import annotations

from .settings import CHAT_MODEL, COMPARISON_MODELS, OLLAMA_API_KEY
from .pipeline import _chat_model, _message_content
from .security import redact_sensitive_text


def main() -> None:
    models = list(dict.fromkeys([CHAT_MODEL, *COMPARISON_MODELS]))
    print("Este teste faz uma chamada curta por modelo listado e pode consumir cota.")
    print(f"Modelo principal mantido: {CHAT_MODEL}")
    failures = []
    for model in models:
        print(f"\nTestando modelo: {model}")
        try:
            result = _chat_model(model).invoke("Responda somente com: EnergiaLar modelo OK")
            content = _message_content(result)
            if not content:
                raise RuntimeError("o endpoint não retornou texto")
            safe_content = redact_sensitive_text(content, OLLAMA_API_KEY)
            print("OK:", safe_content[:100])
        except Exception as exc:
            detail = redact_sensitive_text(f"{type(exc).__name__}: {exc}", OLLAMA_API_KEY)
            failures.append((model, detail))
            print("FALHA:", detail)
    if len(models) < 2:
        failures.append(("COMPARISON_MODELS", "São necessários ao menos dois modelos diferentes para a rubrica."))
    if failures:
        print("\nModelos não validados:")
        for model, detail in failures:
            print(f"- {model}: {detail}")
        raise SystemExit("Não rode a comparação completa até escolher/testar um segundo modelo disponível.")
    print("\nTodos os modelos configurados responderam à chamada curta. Isto verifica conectividade, não qualidade comparativa.")


if __name__ == "__main__":
    main()
