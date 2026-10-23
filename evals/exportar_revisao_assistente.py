from __future__ import annotations
import argparse
import csv
from pathlib import Path
from src.rag.settings import ROOT_DIR

RESULTS = ROOT_DIR / "evals" / "results"


def main():
    parser = argparse.ArgumentParser(description="Exporta respostas e contextos da última avaliação para revisão assistida.")
    parser.add_argument("csv_path", nargs="?", help="CSV específico; se omitido, escolhe a avaliação iterations mais recente.")
    args = parser.parse_args()
    if args.csv_path:
        path = Path(args.csv_path)
        if not path.is_absolute():
            path = ROOT_DIR / path
    else:
        candidates = sorted(RESULTS.glob("avaliacao_iterations_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            raise SystemExit("Nenhum CSV iterations encontrado. Execute primeiro evals.run_eval.")
        path = candidates[0]
    if not path.is_file():
        raise SystemExit(f"CSV não encontrado: {path}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("O CSV não tem registros para revisar.")
    run_ids = {row.get("run_id", "") for row in rows}
    versions = {row.get("prompt_version", "") for row in rows}
    output = RESULTS / f"revisao_assistente_{path.stem.replace('avaliacao_iterations_', '')}.md"
    lines = [
        "# Revisão assistida — avaliação RAG", "",
        f"- CSV de origem: `{path.name}`",
        f"- run_id(s): {', '.join(sorted(run_ids))}",
        f"- versões de prompt: {', '.join(sorted(versions))}",
        f"- linhas exportadas: {len(rows)}", "",
        "Scores manuais estão deliberadamente vazios; esta exportação contém evidência para a revisão. Não trate latência, estrutura Pydantic ou presença mecânica de citação como score de qualidade.", "",
    ]
    for row in rows:
        lines += [
            "---", "",
            f"## {row.get('prompt_version', '?')} / {row.get('case_id', '?')} / {row.get('model', '?')}", "",
            f"**Categoria:** {row.get('category', '')}", "",
            f"**Pergunta:** {row.get('question', '')}", "",
            f"**Pontos esperados:** {row.get('expected_points', '')}", "",
            f"**Fonte(s) esperada(s):** {row.get('expected_source', '')}", "",
            f"**Fontes recuperadas:** {row.get('sources', '') or '(nenhuma)'}", "",
            f"**Contrato Pydantic:** {row.get('structure_valid', '')} | **Citação presente:** {row.get('citation_present', '')} | **Latência (s):** {row.get('latency_seconds', '')}", "",
            "### Resposta", "", row.get('answer', '') or "(sem resposta)", "",
            "### Contexto recuperado", "", row.get('retrieved_context', '') or "(sem contexto recuperado)", "",
            "### Erro", "", row.get('error', '') or "(nenhum)", "",
        ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Arquivo para revisão criado: {output}")
    print(f"Linhas: {len(rows)} | versões: {', '.join(sorted(versions))}")


if __name__ == "__main__":
    main()
