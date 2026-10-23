import pytest
from src.rag.prompt_format import split_prompt


def test_split_prompt_preserves_separate_system_and_user_templates():
    system, human = split_prompt(
        "Instruções invioláveis.\n\n--- HUMAN ---\nPergunta: {question}\nContexto: {context}"
    )
    assert "Instruções invioláveis" in system
    assert "{question}" in human
    assert "{context}" in human


def test_split_prompt_rejects_missing_or_empty_sections():
    with pytest.raises(ValueError):
        split_prompt("Sem delimitador")
    with pytest.raises(ValueError):
        split_prompt("--- HUMAN ---\nSó mensagem humana")
