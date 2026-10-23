"""Configura embeddings locais e normaliza o ID do modelo secundário para a API Cloud."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
VALUES = {
    "EMBEDDING_HOST": "http://localhost:11434",
    "EMBEDDING_MODEL": "nomic-embed-text",
}

def configure_env_file(env_file: Path) -> None:
    """Atualiza apenas hosts/modelos conhecidos; não imprime nem lê segredos para o output."""
    env_file = Path(env_file)
    if not env_file.exists():
        raise FileNotFoundError("Arquivo .env ausente.")
    text = env_file.read_text(encoding="utf-8-sig")
    for key, value in VALUES.items():
        pattern = rf"(?m)^\s*{re.escape(key)}\s*=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, text):
            text = re.sub(pattern, lambda _match, r=replacement: r, text, count=1)
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += replacement + "\n"

    # The public model registry uses the -cloud suffix for the CLI alias, but examples
    # for the direct API's `model` field use the name without that suffix. Normalize
    # known optional CLI aliases; preserve the primary/model choices.
    comparison_pattern = r"(?m)^\s*COMPARISON_MODELS\s*=([^\r\n]*)$"
    match = re.search(comparison_pattern, text)
    if match:
        models = [item.strip() for item in match.group(1).split(",") if item.strip()]
        models = [
            "gpt-oss:20b" if item == "gpt-oss:20b-cloud" else item
            for item in models
        ]
        models = [
            "nemotron-3-nano:30b" if item == "nemotron-3-nano:30b-cloud" else item
            for item in models
        ]
        replacement = "COMPARISON_MODELS=" + ",".join(models)
        text = re.sub(comparison_pattern, lambda _match, r=replacement: r, text, count=1)

    env_file.write_text(text, encoding="utf-8")

def main() -> None:
    if not ENV_FILE.exists():
        raise SystemExit("Arquivo .env ausente. Crie-o a partir de .env.example e configure OLLAMA_API_KEY antes de continuar.")
    try:
        configure_env_file(ENV_FILE)
    except OSError as exc:
        raise SystemExit(f"Não foi possível atualizar .env: {type(exc).__name__}") from exc
    print("Embeddings configurados: host local e nomic-embed-text.")
    print("Se o identificador de comparação padrão usava o sufixo -cloud do CLI, ele foi normalizado para o campo model da API.")
    print("A chave API e o modelo primário gemma4:31b foram preservados; nenhum segredo foi exibido.")

if __name__ == "__main__":
    main()
