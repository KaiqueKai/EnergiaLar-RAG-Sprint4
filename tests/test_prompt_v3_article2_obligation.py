from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v3_requires_article_2_when_the_retrieved_context_contains_it():
    prompt = (ROOT / "prompts" / "rag_v3.md").read_text(encoding="utf-8")
    assert "REQUISITOS DE COBERTURA PARA Q04 E Q05" in prompt
    assert "Lei Estadual SP nº 18.403/2026, art. 2º" in prompt
    assert "capacidade mínima" in prompt
    assert "Não invente percentuais, kW" in prompt
    assert "Não generalize a lei municipal para todo o Estado" in prompt


def test_v3_keeps_document_only_grounding_and_json_contract():
    prompt = (ROOT / "prompts" / "rag_v3.md").read_text(encoding="utf-8")
    assert "contexto documental é a ÚNICA evidência factual" in prompt
    assert "Retorne SOMENTE JSON válido" in prompt
    assert "{question}" in prompt
    assert "{context}" in prompt
