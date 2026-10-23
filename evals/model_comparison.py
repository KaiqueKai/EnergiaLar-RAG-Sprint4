"""Compara os dois modelos conversacionais históricos da Sprint 3."""
import json
import time
from pathlib import Path
import tiktoken
from src.chatbot import criar_chatbot, responder
from src.schemas.consulta_recarga import ConsultaRecarga

MODELOS = ["gpt-oss:20b", "gemma4:31b"]
CASOS = [
    {"id": 1, "pergunta": "Como reduzir o consumo energético de uma estação de carregamento?"},
    {"id": 2, "pergunta": "Quais indicadores devo monitorar diariamente?"},
    {"id": 3, "pergunta": "Como prever falhas em carregadores elétricos?"},
    {"id": 4, "pergunta": "Como melhorar a eficiência operacional da estação?"},
    {"id": 5, "pergunta": "Qual a importância da manutenção preventiva?"},
]
def contar_tokens(texto):
    return len(tiktoken.get_encoding("cl100k_base").encode(texto))
def extrair_resposta(resultado):
    if isinstance(resultado, ConsultaRecarga): return resultado.resposta
    if isinstance(resultado, dict): return resultado["resposta"]
    raise TypeError(f"Tipo de resposta inesperado: {type(resultado).__name__}")
def validar_estrutura(resultado):
    if isinstance(resultado, ConsultaRecarga): return True
    if isinstance(resultado, dict): return {"estado_carregador","potencia_kw","faturamento_reais","resposta"}.issubset(resultado)
    return False
def avaliar_modelo(modelo):
    print(f"\n{'='*60}\nMODELO: {modelo}\n{'='*60}")
    bot=criar_chatbot(modelo); results=[]
    for case in CASOS:
        start=time.perf_counter()
        result=responder(bot,case["pergunta"],session_id=f"comparacao_{modelo}_{case['id']}")
        elapsed=time.perf_counter()-start; answer=extrair_resposta(result)
        item={"modelo":modelo,"id":case["id"],"pergunta":case["pergunta"],"resposta":answer,"tokens_resposta":contar_tokens(answer),"latencia_segundos":round(elapsed,2),"estrutura_valida":validar_estrutura(result)}
        results.append(item); print(f"CASO {item['id']} | tokens={item['tokens_resposta']} | latência={elapsed:.2f}s | estrutura={'OK' if item['estrutura_valida'] else 'FALHA'}")
    return results
def main():
    all_results=[]
    for model in MODELOS:
        try: all_results.extend(avaliar_modelo(model))
        except Exception as exc: print(f"Falha ao executar modelo {model}: {type(exc).__name__}: {exc}")
    output=Path(__file__).resolve().parent/"model_comparison_results.json"
    output.write_text(json.dumps(all_results,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Resultados salvos em: {output}")
    for model in MODELOS:
        rows=[row for row in all_results if row["modelo"]==model]
        if not rows: continue
        print(f"{model}: {len(rows)} casos; média tokens={sum(x['tokens_resposta'] for x in rows)/len(rows):.2f}; latência média={sum(x['latencia_segundos'] for x in rows)/len(rows):.2f}s; estrutura válida={sum(x['estrutura_valida'] for x in rows)}/{len(rows)}")
if __name__ == "__main__": main()
