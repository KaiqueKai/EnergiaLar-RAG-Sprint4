"""Executa a avaliação conversacional da Sprint 3; salva resultados recém-medidos."""
import json, time
from pathlib import Path
import tiktoken
from src.chatbot import criar_chatbot, responder
from src.schemas.consulta_recarga import ConsultaRecarga
ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
FILES = {"happy_path": EVALS/"casos_teste.json", "edge_case": EVALS/"edge_cases.json", "jailbreak": EVALS/"jailbreak.json", "out_of_scope": EVALS/"out_of_scope.json"}
def carregar_casos():
    casos=[]
    for category,path in FILES.items():
        if path.exists():
            data=json.loads(path.read_text(encoding="utf-8"))
            for case in data.get("casos",[]):
                item=dict(case); item["categoria"]=category; casos.append(item)
    return casos
def main():
    cases=carregar_casos()
    if not cases: raise RuntimeError("Nenhum caso de teste Sprint 3 encontrado.")
    bot=criar_chatbot(); enc=tiktoken.get_encoding("cl100k_base"); results=[]
    for case in cases:
        start=time.perf_counter(); answer=responder(bot,case.get("pergunta",""),session_id=f"eval_{case['id']}"); elapsed=time.perf_counter()-start
        results.append({"id":case["id"],"categoria":case["categoria"],"tipo":case.get("tipo",case["categoria"]),"pergunta":case.get("pergunta",""),"resposta_esperada":case.get("resposta_esperada",""),"criterios":case.get("criterios",[]),"resposta_obtida":answer.resposta,"tokens_resposta":len(enc.encode(answer.resposta)),"latencia_segundos":round(elapsed,2),"estrutura_valida":isinstance(answer,ConsultaRecarga),"avaliacao":"PREENCHER_MANUALMENTE","justificativa":"PREENCHER_MANUALMENTE"})
        print(f"[{case['categoria']}] {case['id']} | {elapsed:.2f}s | estrutura={'OK' if isinstance(answer,ConsultaRecarga) else 'FALHA'}")
    path=EVALS/"sprint3_results.json"
    path.write_text(json.dumps({"data_execucao":time.strftime("%Y-%m-%dT%H:%M:%S"),"total_casos":len(results),"resultados":results},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Resultados recém-gerados: {path}")
    print("As avaliações qualitativas continuam pendentes até serem pontuadas por pessoa.")
if __name__ == "__main__": main()
