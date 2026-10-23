import os
import subprocess
import sys
from pathlib import Path


def test_rag_defaults_do_not_change_when_legacy_sprint3_models_are_set():
    env = os.environ.copy()
    for key in (
        "CHAT_MODEL", "COMPARISON_MODELS", "RAG_MODEL_SECONDARY", "OLLAMA_HOST",
        "OLLAMA_BASE_URL", "EMBEDDING_HOST", "MODEL_PRIMARY", "MODEL_SECONDARY",
    ):
        env.pop(key, None)
    env["PYTHON_DOTENV_DISABLED"] = "1"
    env["MODEL_PRIMARY"] = "gpt-oss:20b"
    env["MODEL_SECONDARY"] = "gemma4:31b"
    code = (
        "from src.rag.settings import CHAT_MODEL, COMPARISON_MODELS, EMBEDDING_HOST, TOP_K; "
        "print(CHAT_MODEL); print(','.join(COMPARISON_MODELS)); print(EMBEDDING_HOST); print(TOP_K)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "gemma4:31b"
    assert lines[1] == "gemma4:31b,gpt-oss:20b"
    assert lines[2] == "http://localhost:11434"
    assert lines[3] == "8"
