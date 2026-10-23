from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
EVALS_DIR = BASE_DIR / "evals"

SYSTEM_PROMPT_FILE = PROMPTS_DIR / "system_prompt.txt"
BASELINE_PROMPT_FILE = PROMPTS_DIR / "baseline_prompt.txt"
CASES_FILE = EVALS_DIR / "casos_teste.json"
BASELINE_RESULTS_FILE = EVALS_DIR / "sprint2_baseline.json"
COMPARISON_RESULTS_FILE = EVALS_DIR / "model_comparison_results.json"

BASELINE_MODEL = "gemma4:31b-cloud"
COMPARISON_MODELS = (
    "gemma4:31b-cloud",
    "gpt-oss:120b-cloud",
)

TEMPERATURE = 0


def read_prompt(path: Path) -> str:
    """Lê um prompt de texto e garante que não fique vazio."""
    prompt = path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise ValueError(f"Prompt vazio: {path}")
    return prompt
