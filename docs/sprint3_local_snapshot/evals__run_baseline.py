import json
import time

import tiktoken
from langchain_ollama import ChatOllama

from src.config import (
    BASELINE_MODEL,
    BASELINE_PROMPT_FILE,
    BASELINE_RESULTS_FILE,
    CASES_FILE,
    TEMPERATURE,
    read_prompt,
)
from src.schemas.consulta_recarga import ConsultaRecarga


ENCODING = tiktoken.get_encoding("cl100k_base")
SYSTEM_PROMPT = read_prompt(BASELINE_PROMPT_FILE)


def _extrair_json(texto: str) -> str:
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio == -1 or fim == -1 or fim < inicio:
        raise ValueError("Resposta sem JSON válido.")
    return texto[inicio : fim + 1]


def avaliar_caso(llm: ChatOllama, caso: dict) -> dict:
    inicio = time.perf_counter()
    resposta = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", caso["pergunta"]),
        ]
    )
    latencia = time.perf_counter() - inicio

    texto = str(resposta.content)
    dados = json.loads(_extrair_json(texto))
    validado = ConsultaRecarga.model_validate(dados)

    return {
        "modelo": BASELINE_MODEL,
        "id": caso["id"],
        "pergunta": caso["pergunta"],
        "resposta": validado.resposta,
        "tokens_resposta": len(ENCODING.encode(validado.resposta)),
        "latencia_segundos": round(latencia, 2),
        "estrutura_valida": True,
        "status": "OK",
    }


def main() -> None:
    casos = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    llm = ChatOllama(model=BASELINE_MODEL, temperature=TEMPERATURE)
    resultados: list[dict] = []

    print("=" * 80)
    print("SPRINT 2 - BASELINE")
    print("=" * 80)

    for caso in casos:
        try:
            resultado = avaliar_caso(llm, caso)
            resultados.append(resultado)
            print(f"\nCASO {caso['id']}")
            print(f"Tokens: {resultado['tokens_resposta']}")
            print(f"Latência: {resultado['latencia_segundos']:.2f} segundos")
            print("Estrutura Pydantic: OK")
        except Exception as erro:
            resultados.append(
                {
                    "modelo": BASELINE_MODEL,
                    "id": caso["id"],
                    "pergunta": caso["pergunta"],
                    "resposta": None,
                    "tokens_resposta": None,
                    "latencia_segundos": None,
                    "estrutura_valida": False,
                    "status": "ERRO",
                    "erro": str(erro),
                }
            )
            print(f"\nCASO {caso['id']}")
            print(f"ERRO: {erro}")

    BASELINE_RESULTS_FILE.write_text(
        json.dumps(resultados, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    print(f"\nResultados salvos em: {BASELINE_RESULTS_FILE}")


if __name__ == "__main__":
    main()
