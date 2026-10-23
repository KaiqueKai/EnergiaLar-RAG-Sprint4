"""Seleção reproduzível de casos para avaliações RAG."""
from __future__ import annotations


def select_eval_cases(dataset: list[dict], requested_ids: list[str] | None = None) -> list[dict]:
    """Por padrão usa o eval set inteiro em todos os modos; IDs permitem pilotos explícitos."""
    if not requested_ids:
        return list(dataset)
    known = {item["id"] for item in dataset}
    requested = set(requested_ids)
    unknown = requested - known
    if unknown:
        raise ValueError(f"IDs desconhecidos: {', '.join(sorted(unknown))}. IDs válidos: {', '.join(sorted(known))}")
    selected = [item for item in dataset if item["id"] in requested]
    if not selected:
        raise ValueError("O conjunto de avaliação ficou vazio.")
    return selected


def build_model_prompt_combinations(models: list[str], prompts: list[str]) -> list[tuple[str, str]]:
    """Gera a matriz modelo × prompt sem chamadas duplicadas."""
    unique_models = list(dict.fromkeys(model.strip() for model in models if model.strip()))
    unique_prompts = list(dict.fromkeys(prompt.strip().lower() for prompt in prompts if prompt.strip()))
    if len(unique_models) < 2:
        raise ValueError("A comparação exige pelo menos dois modelos distintos.")
    if not unique_prompts:
        raise ValueError("Informe pelo menos uma versão de prompt.")
    invalid = [prompt for prompt in unique_prompts if prompt not in {"v1", "v2", "v3"}]
    if invalid:
        raise ValueError(f"Versões de prompt inválidas: {invalid}")
    return [(prompt, model) for model in unique_models for prompt in unique_prompts]
