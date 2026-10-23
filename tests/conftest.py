"""Testes unitários não devem exigir chave real nem chamar a API."""
import os
os.environ.setdefault("OLLAMA_API_KEY", "test-key-only-for-mocked-tests")
