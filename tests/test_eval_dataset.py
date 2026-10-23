import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_eval_dataset_has_unique_ids_and_required_categories():
    data = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    ids = [item["id"] for item in data]
    categories = {item["category"] for item in data}
    assert len(data) >= 8
    assert len(ids) == len(set(ids))
    assert {"in_scope", "out_of_scope", "safety", "injection"}.issubset(categories)
    for item in data:
        assert item["question"].strip()
        assert item["expected_points"]
        assert item["expected_source"]


def test_full_set_is_used_by_default_for_every_evaluation_mode():
    from evals.evaluation_plan import select_eval_cases
    data = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    selected = select_eval_cases(data)
    assert [item["id"] for item in selected] == [item["id"] for item in data]
    assert len(selected) == 8


def test_pilot_can_select_only_requested_case():
    from evals.evaluation_plan import select_eval_cases
    data = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    selected = select_eval_cases(data, ["Q01"])
    assert [item["id"] for item in selected] == ["Q01"]
