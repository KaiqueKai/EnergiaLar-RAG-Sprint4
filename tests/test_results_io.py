import csv
from datetime import datetime
from pathlib import Path
import pytest
from evals.results_io import create_run_id, result_path, save_csv


def test_result_path_is_unique_per_evaluation_run(tmp_path: Path):
    t1 = datetime(2026, 10, 21, 6, 0, 0, 100)
    t2 = datetime(2026, 10, 21, 6, 0, 0, 200)
    p1 = result_path(tmp_path, "iterations", create_run_id(t1))
    p2 = result_path(tmp_path, "iterations", create_run_id(t2))
    assert p1 != p2
    assert p1.name.startswith("avaliacao_iterations_")
    with pytest.raises(ValueError):
        result_path(tmp_path, "modo-invalido", create_run_id(t1))


def test_csv_contains_latency_sources_and_real_run_id(tmp_path: Path):
    path = result_path(tmp_path, "models", "20261021_060000_000100")
    save_csv(path, [{
        "run_id": "20261021_060000_000100", "case_id": "Q01",
        "prompt_version": "v2", "model": "gemma4:31b",
        "question_used_after_security_filter": "pergunta segura",
        "security_events": "prompt_injection_clause_removed",
        "latency_seconds": 1.234, "source_count": 2,
        "faithfulness_score": "", "answer_relevancy_score": "",
    }])
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["latency_seconds"] == "1.234"
    assert rows[0]["source_count"] == "2"
    assert rows[0]["run_id"] == "20261021_060000_000100"
    assert rows[0]["question_used_after_security_filter"] == "pergunta segura"
    assert rows[0]["security_events"] == "prompt_injection_clause_removed"
