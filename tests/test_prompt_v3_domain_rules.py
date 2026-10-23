import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v3_explicitly_covers_state_municipal_laws_and_enel_effective_date():
    prompt = (ROOT / "prompts" / "rag_v3.md").read_text(encoding="utf-8")
    assert "18.403/2026" in prompt
    assert "17.336/2020" in prompt
    assert "04/07/2026" in prompt


def test_q04_expected_points_include_state_law_article_2():
    dataset = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    q04 = next(item for item in dataset if item["id"] == "Q04")
    assert any("art. 2º" in point and "capacidade mínima" in point for point in q04["expected_points"])
    assert "2º" in q04["question"] and "capacidade mínima" in q04["question"]
