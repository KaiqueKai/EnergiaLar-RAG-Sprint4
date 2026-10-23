"""Utilitários para salvar avaliações sem sobrescrever execuções anteriores."""
from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path

FIELDS = [
    "run_id", "case_id", "category", "question", "question_used_after_security_filter", "security_events", "expected_points", "expected_source",
    "prompt_version", "model", "temperature", "top_p", "max_tokens", "top_k", "min_relevance_score",
    "latency_seconds", "source_count", "structure_valid", "answer", "sources", "retrieved_context",
    "context_relevance_score", "faithfulness_score", "answer_relevancy_score",
    "citation_present", "evaluator_notes", "error",
]


def create_run_id(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime("%Y%m%d_%H%M%S_%f")


def result_path(results_dir: Path, mode: str, run_id: str) -> Path:
    if mode not in {"iterations", "models"}:
        raise ValueError("mode deve ser 'iterations' ou 'models'.")
    return results_dir / f"avaliacao_{mode}_{run_id}.csv"


def save_csv(path: Path, records: list[dict]) -> None:
    """Persiste o estado da execução atual; cada execução tem um arquivo próprio."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
        stream.flush()
