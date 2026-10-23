from pathlib import Path
from scripts.configurar_embeddings_locais import configure_env_file

def test_configurator_preserves_secret_and_primary_model_and_fixes_known_secondary(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(
        "OLLAMA_API_KEY=never-print-this-secret\n"
        "CHAT_MODEL=gemma4:31b\n"
        "COMPARISON_MODELS=gemma4:31b,nemotron-3-nano:30b-cloud\n"
        "EMBEDDING_HOST=https://ollama.com\n",
        encoding="utf-8",
    )
    configure_env_file(env)
    result = env.read_text(encoding="utf-8")
    assert "OLLAMA_API_KEY=never-print-this-secret" in result
    assert "CHAT_MODEL=gemma4:31b" in result
    assert "COMPARISON_MODELS=gemma4:31b,nemotron-3-nano:30b\n" in result
    assert "EMBEDDING_HOST=http://localhost:11434" in result
    assert "EMBEDDING_MODEL=nomic-embed-text" in result



def test_configurator_normalizes_gpt_oss_cli_cloud_alias_for_direct_api(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(
        "OLLAMA_API_KEY=keep-this-value\n"
        "CHAT_MODEL=gemma4:31b\n"
        "COMPARISON_MODELS=gemma4:31b,gpt-oss:20b-cloud\n",
        encoding="utf-8",
    )
    configure_env_file(env)
    result = env.read_text(encoding="utf-8")
    assert "OLLAMA_API_KEY=keep-this-value" in result
    assert "CHAT_MODEL=gemma4:31b" in result
    assert "COMPARISON_MODELS=gemma4:31b,gpt-oss:20b\n" in result
