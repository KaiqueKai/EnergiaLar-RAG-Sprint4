"""Compara o baseline Sprint 2 documentado com resultados medidos Sprint 3."""
import json
from pathlib import Path
CASOS_SPRINT2 = [
 {"id":"EV-01","pergunta":"Como reduzir o consumo energético de uma estação de carregamento?","avaliacao":"Adequada"},
 {"id":"EV-02","pergunta":"Quais indicadores devo monitorar diariamente?","avaliacao":"Adequada"},
 {"id":"EV-03","pergunta":"Como prever falhas em carregadores elétricos?","avaliacao":"Adequada"},
 {"id":"EV-04","pergunta":"Como melhorar a eficiência operacional da estação?","avaliacao":"Adequada"},
 {"id":"EV-05","pergunta":"Qual a importância da manutenção preventiva?","avaliacao":"Adequada"},
]
def carregar_resultados_sprint3():
    path=Path(__file__).resolve().parent/"sprint3_results.json"
    if not path.exists(): raise FileNotFoundError("Rode primeiro: python -m evals.sprint3_eval")
    data=json.loads(path.read_text(encoding="utf-8")); rows=data["resultados"] if isinstance(data,dict) else data
    return [r for r in rows if r.get("categoria")=="happy_path"]
def main():
    rows=carregar_resultados_sprint3()
    if not rows: raise RuntimeError("Nenhum resultado happy_path Sprint 3 foi gerado.")
    by_id={r["id"]:r for r in rows}
    comparable=[c for c in CASOS_SPRINT2 if c["id"] in by_id]
    print("COMPARAÇÃO SPRINT 2 x SPRINT 3")
    for case in comparable:
        row=by_id[case["id"]]
        print(f"{case['id']} | Sprint 2={case['avaliacao']} | tokens S3={row.get('tokens_resposta')} | latência S3={row.get('latencia_segundos')}s | estrutura={row.get('estrutura_valida')}")
    count=len(comparable)
    print(f"Média tokens S3: {sum(by_id[c['id']]['tokens_resposta'] for c in comparable)/count:.2f}")
    print(f"Latência média S3: {sum(by_id[c['id']]['latencia_segundos'] for c in comparable)/count:.2f}s")
    print(f"Saídas estruturadas válidas: {sum(bool(by_id[c['id']]['estrutura_valida']) for c in comparable)}/{count}")
    print("Sprint 2: o arquivo de comparação registra ‘Adequada’ para esses cinco casos; tokens/latência do baseline Sprint 2 não foram registrados e não serão inventados.")
if __name__ == "__main__": main()
