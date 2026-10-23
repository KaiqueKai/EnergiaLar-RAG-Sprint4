from __future__ import annotations
import argparse
import json
import os
import re
import time
from pathlib import Path
from src.rag.settings import ROOT_DIR, COMPARISON_MODELS, CHAT_MODEL, TOP_K, MIN_RELEVANCE_SCORE, TEMPERATURE, TOP_P, MAX_TOKENS
from src.rag.pipeline import answer_question
from src.rag.security import redact_sensitive_text
from evals.results_io import FIELDS, create_run_id, result_path, save_csv
from evals.evaluation_plan import select_eval_cases, build_model_prompt_combinations

EVAL_FILE = ROOT_DIR / "evals" / "dataset.json"
RESULTS_DIR = ROOT_DIR / "evals" / "results"


def load_dataset():
    return json.loads(EVAL_FILE.read_text(encoding="utf-8"))


def ask_score(label: str):
    while True:
        raw = input(f"{label} (0, 0.25, 0.5, 0.75, 1 ou Enter para deixar pendente): ").strip().replace(",", ".")
        if not raw:
            return ""
        try:
            value = float(raw)
        except ValueError:
            print("Digite um número entre 0 e 1.")
            continue
        if value in (0.0, 0.25, 0.5, 0.75, 1.0):
            return value
        print("Use um dos valores 0, 0.25, 0.5, 0.75 ou 1.")



def main():
    parser = argparse.ArgumentParser(description="Gera respostas reais para avaliar o RAG por rubrica manual.")
    parser.add_argument("--mode", choices=["iterations", "models"], required=True)
    parser.add_argument("--model", default=CHAT_MODEL, help="modelo usado para comparar v1 x v2")
    parser.add_argument("--models", nargs="+", default=None, help="dois ou mais modelos para comparação com v2")
    parser.add_argument("--interactive", action="store_true", help="pontua manualmente cada resposta gerada")
    parser.add_argument("--prompts", nargs="+", choices=["v1", "v2", "v3"], default=None, help="no modo iterations compara versões; no modo models permite matriz modelo × prompt")
    parser.add_argument("--prompt", choices=["v1", "v2", "v3"], default="v2", help="prompt usado no modo models")
    parser.add_argument("--ids", nargs="*", default=None, help="IDs de perguntas opcionais, por exemplo Q01 Q02 Q03")
    args = parser.parse_args()

    try:
        dataset = select_eval_cases(load_dataset(), args.ids)
    except ValueError as exc:
        parser.error(str(exc))

    if args.mode == "iterations":
        versions = list(dict.fromkeys(args.prompts or ["v1", "v2"]))
        combinations = [(prompt_version, args.model) for prompt_version in versions]
    else:
        models = args.models or COMPARISON_MODELS
        models = list(dict.fromkeys(models))
        versions = list(dict.fromkeys(args.prompts or [args.prompt]))
        try:
            combinations = build_model_prompt_combinations(models, versions)
        except ValueError as exc:
            parser.error(str(exc))
        if len(versions) > 1:
            print(f"Matriz de comparação: {len(models)} modelos × {len(versions)} prompts = {len(combinations)} combinações; cada caso será executado em cada combinação.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = create_run_id()
    output_path = result_path(RESULTS_DIR, args.mode, run_id)
    records: list[dict] = []

    for prompt_version, model in combinations:
        for item in dataset:
            print(f"\n[{item['id']}] {prompt_version} | {model} | {item['question']}")
            result = {}
            error = ""
            started = time.perf_counter()
            try:
                result = answer_question(
                    question=item["question"],
                    model_name=model,
                    prompt_version=prompt_version,
                    top_k=TOP_K,
                    min_score=MIN_RELEVANCE_SCORE,
                )
                print("Resposta:", result["answer"])
                print("Contrato Pydantic:", "OK" if result.get("structure_valid") else "FALHA")
                if result.get("parse_error"):
                    print("Falha de estrutura:", result["parse_error"])
                print("Fontes:", "; ".join(source["citation"] for source in result["sources"]) or "nenhuma")
            except Exception as exc:
                error = redact_sensitive_text(f"{type(exc).__name__}: {exc}", os.getenv("OLLAMA_API_KEY", ""))
                print("FALHA REAL:", error)
            latency_seconds = round(time.perf_counter() - started, 3)
            context_relevance = ""
            faithfulness = ""
            relevancy = ""
            notes = ""
            if args.interactive and not error:
                context_relevance = ask_score("Qualidade do contexto recuperado")
                faithfulness = ask_score("Faithfulness")
                relevancy = ask_score("Answer relevancy")
                notes = input("Justificativa curta (opcional): ").strip()
            answer_text = result.get("answer", "")
            retrieved_sources = result.get("sources", [])
            if retrieved_sources:
                citation_present = str(bool(re.search(r"\[\d+\]", answer_text) and any(
                    source.get("citation", "") in answer_text for source in retrieved_sources
                ))).lower()
            else:
                citation_present = "n/a"
            records.append({
                "run_id": run_id,
                "case_id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "question_used_after_security_filter": result.get("question_used", item["question"]),
                "security_events": " | ".join(result.get("security_events", [])),
                "expected_points": " | ".join(item["expected_points"]),
                "expected_source": item["expected_source"],
                "prompt_version": prompt_version,
                "model": model,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "max_tokens": MAX_TOKENS,
                "top_k": TOP_K,
                "min_relevance_score": MIN_RELEVANCE_SCORE,
                "latency_seconds": latency_seconds,
                "source_count": len(result.get("sources", [])),
                "structure_valid": result.get("structure_valid", False),
                "answer": result.get("answer", ""),
                "sources": " | ".join(source["citation"] for source in result.get("sources", [])),
                "retrieved_context": result.get("context", ""),
                "context_relevance_score": context_relevance,
                "faithfulness_score": faithfulness,
                "answer_relevancy_score": relevancy,
                "citation_present": citation_present,
                "evaluator_notes": notes,
                "error": error,
            })
            save_csv(output_path, records)
    print(f"\nCSV salvo: {output_path}")
    print("Este arquivo é exclusivo desta execução; rodadas anteriores foram preservadas.")
    print("Pontue contexto, faithfulness e answer relevancy conforme evals/manual_rubric.md. Citação é registrada automaticamente quando há fontes.")


if __name__ == "__main__":
    main()
