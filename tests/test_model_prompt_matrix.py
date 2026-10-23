import pytest
from evals.evaluation_plan import build_model_prompt_combinations

def test_matrix_compares_each_model_with_each_prompt():
    combos = build_model_prompt_combinations(["gemma4:31b", "gpt-oss:20b"], ["v1", "v2"])
    assert combos == [
        ("v1", "gemma4:31b"), ("v2", "gemma4:31b"),
        ("v1", "gpt-oss:20b"), ("v2", "gpt-oss:20b"),
    ]

def test_matrix_rejects_duplicate_models_and_no_prompts():
    with pytest.raises(ValueError, match="dois modelos"):
        build_model_prompt_combinations(["gemma4:31b", "gemma4:31b"], ["v1", "v2"])
    with pytest.raises(ValueError, match="versão de prompt"):
        build_model_prompt_combinations(["a", "b"], [])
