from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from datetime import datetime
from src.rag.settings import ROOT_DIR

RESULTS_DIR = ROOT_DIR / "evals" / "results"


def numeric(values, low=0, high=1):
    out = []
    for value in values:
        try:
            number = float(value)
            if low <= number <= high:
                out.append(number)
        except (TypeError, ValueError):
            pass
    return out


def discover_csvs(mode: str, explicit: str | None = None) -> list[Path]:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = ROOT_DIR / path
        if not path.is_file():
            raise SystemExit(f"CSV não encontrado: {path}")
        return [path]
    paths = sorted(RESULTS_DIR.glob(f"avaliacao_{mode}_*.csv"))
    legacy = RESULTS_DIR / f"avaliacao_{mode}.csv"
    if legacy.is_file():
        paths.insert(0, legacy)
    if not paths:
        raise SystemExit(f"Nenhum CSV de avaliação encontrado para '{mode}'. Execute primeiro evals.run_eval --mode {mode}.")
    return paths


def read_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                row.setdefault("run_id", path.stem)
                row["_file"] = str(path)
                rows.append(row)
    return rows


def build_summary(rows: list[dict], paths: list[Path], mode: str) -> dict:
    groups: dict[tuple[str, str, str], list[dict]] = {}
    for row in rows:
        key = (row.get("run_id") or row.get("_file", "execução_legacy"), row.get("prompt_version", ""), row.get("model", ""))
        groups.setdefault(key, []).append(row)

    summary = {
        "mode": mode,
        "input_files": [str(path.relative_to(ROOT_DIR) if path.is_relative_to(ROOT_DIR) else path) for path in paths],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "groups": [],
    }
    print("Execução | Prompt | Modelo | Contexto | Faithfulness | Answer relevancy | Citação % | Latência média (s) | erros")
    for (run_id, prompt, model), grouped in sorted(groups.items()):
        faith = numeric(row.get("faithfulness_score", "") for row in grouped)
        rel = numeric(row.get("answer_relevancy_score", "") for row in grouped)
        context = numeric(row.get("context_relevance_score", "") for row in grouped)
        latency = numeric((row.get("latency_seconds", "") for row in grouped), low=0, high=10**9)
        citation_rows = [row for row in grouped if str(row.get("citation_present", "")).lower() in {"true", "false"}]
        citation_coverage = (sum(1 for row in citation_rows if str(row.get("citation_present", "")).lower() == "true") / len(citation_rows)) if citation_rows else None
        failed = sum(1 for row in grouped if row.get("error"))
        item = {
            "run_id": run_id,
            "prompt_version": prompt,
            "model": model,
            "faithfulness_mean": round(mean(faith), 4) if faith else None,
            "answer_relevancy_mean": round(mean(rel), 4) if rel else None,
            "faithfulness_count": len(faith),
            "answer_relevancy_count": len(rel),
            "context_relevance_mean": round(mean(context), 4) if context else None,
            "context_relevance_count": len(context),
            "citation_coverage": round(citation_coverage, 4) if citation_coverage is not None else None,
            "citation_evaluated_count": len(citation_rows),
            "mean_latency_seconds": round(mean(latency), 3) if latency else None,
            "rows": len(grouped),
            "errors": failed,
            "structure_valid_count": sum(1 for row in grouped if str(row.get("structure_valid", "")).lower() in {"true", "1"}),
            "structure_valid_total": len(grouped),
            "structure_failures": sum(1 for row in grouped if str(row.get("structure_valid", "")).lower() not in {"true", "1"}),
        }
        summary["groups"].append(item)
        fs = f"{item['faithfulness_mean']:.3f}" if item["faithfulness_mean"] is not None else "PENDENTE"
        rs = f"{item['answer_relevancy_mean']:.3f}" if item["answer_relevancy_mean"] is not None else "PENDENTE"
        ls = f"{item['mean_latency_seconds']:.3f}" if item["mean_latency_seconds"] is not None else "N/D"
        cs = f"{item['context_relevance_mean']:.3f}" if item["context_relevance_mean"] is not None else "PENDENTE/N/A"
        citation = f"{item['citation_coverage'] * 100:.1f}% (n={item['citation_evaluated_count']})" if item["citation_coverage"] is not None else "N/D"
        print(f"{run_id} | {prompt} | {model} | {cs} | {fs} | {rs} | {citation} | {ls} | {failed}")

    by_run_model: dict[tuple[str, str], dict[str, dict]] = {}
    for item in summary["groups"]:
        by_run_model.setdefault((item["run_id"], item["model"]), {})[item["prompt_version"]] = item
    deltas = []
    for (run_id, model), versions in sorted(by_run_model.items()):
        # Compare only adjacent prompt versions measured in the same run and on the same dataset.
        for older, newer in (("v1", "v2"), ("v2", "v3")):
            left, right = versions.get(older), versions.get(newer)
            if left and right:
                deltas.append({
                    "run_id": run_id,
                    "model": model,
                    "comparison": f"{newer}-{older}",
                    "faithfulness_delta": round(right["faithfulness_mean"] - left["faithfulness_mean"], 4) if left["faithfulness_mean"] is not None and right["faithfulness_mean"] is not None else None,
                    "answer_relevancy_delta": round(right["answer_relevancy_mean"] - left["answer_relevancy_mean"], 4) if left["answer_relevancy_mean"] is not None and right["answer_relevancy_mean"] is not None else None,
                    "context_relevance_delta": round(right["context_relevance_mean"] - left["context_relevance_mean"], 4) if left["context_relevance_mean"] is not None and right["context_relevance_mean"] is not None else None,
                })
    summary["iteration_deltas"] = deltas
    return summary


def main():
    parser = argparse.ArgumentParser(description="Resume avaliações RAG sem misturar silenciosamente diferentes execuções.")
    parser.add_argument("csv_path", nargs="?", help="caminho de um CSV opcional; por padrão agrega arquivos históricos do modo")
    parser.add_argument("--mode", choices=["iterations", "models"], default="iterations")
    args = parser.parse_args()
    paths = discover_csvs(args.mode, args.csv_path)
    rows = read_rows(paths)
    summary = build_summary(rows, paths, args.mode)
    out_path = RESULTS_DIR / f"resumo_{args.mode}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resumo salvo: {out_path}")
    if not summary["iteration_deltas"]:
        print("Ainda não há um par de versões com scores na mesma execução. Não declare ganho até pontuar o mesmo eval set nas duas versões.")
    else:
        print("Deltas entre versões adjacentes (somente na mesma execução):")
        for item in summary["iteration_deltas"]:
            print(item)


if __name__ == "__main__":
    main()
