from evals.summarize_results import build_summary


def test_summary_tracks_context_scores_citation_coverage_and_same_run_deltas(tmp_path):
    rows = [
        {"run_id": "run1", "prompt_version": "v1", "model": "gemma4:31b", "context_relevance_score": "0.5", "faithfulness_score": "0.5", "answer_relevancy_score": "0.75", "citation_present": "true", "latency_seconds": "1.0", "error": ""},
        {"run_id": "run1", "prompt_version": "v1", "model": "gemma4:31b", "context_relevance_score": "0.75", "faithfulness_score": "0.5", "answer_relevancy_score": "0.5", "citation_present": "false", "latency_seconds": "1.5", "error": ""},
        {"run_id": "run1", "prompt_version": "v2", "model": "gemma4:31b", "context_relevance_score": "1", "faithfulness_score": "1", "answer_relevancy_score": "0.75", "citation_present": "true", "latency_seconds": "0.9", "error": ""},
        {"run_id": "run1", "prompt_version": "v2", "model": "gemma4:31b", "context_relevance_score": "", "faithfulness_score": "0.75", "answer_relevancy_score": "1", "citation_present": "n/a", "latency_seconds": "0.8", "error": ""},
    ]
    summary = build_summary(rows, [tmp_path / "fake.csv"], "iterations")
    groups = {item["prompt_version"]: item for item in summary["groups"]}
    assert groups["v1"]["context_relevance_mean"] == 0.625
    assert groups["v1"]["citation_coverage"] == 0.5
    assert groups["v1"]["citation_evaluated_count"] == 2
    assert groups["v2"]["citation_coverage"] == 1.0
    assert len(summary["iteration_deltas"]) == 1
    assert summary["iteration_deltas"][0]["comparison"] == "v2-v1"
    assert summary["iteration_deltas"][0]["context_relevance_delta"] == 0.375
