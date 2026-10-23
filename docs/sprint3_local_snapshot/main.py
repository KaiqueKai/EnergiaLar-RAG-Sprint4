from src.chatbot import criar_chatbot, responder
from src.config import COMPARISON_MODELS


def main() -> None:
    modelo = COMPARISON_MODELS[0]
    chatbot = criar_chatbot(modelo)
    session_id = "demo"

    print("=" * 70)
    print("ASSISTENTE DE EFICIÊNCIA ENERGÉTICA")
    print(f"Modelo: {modelo}")
    print("Digite 'sair' para encerrar.")
    print("=" * 70)

    while True:
        pergunta = input("\nVocê: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if not pergunta:
            continue

        try:
            resultado = responder(chatbot, pergunta, session_id=session_id)
            print(f"Assistente: {resultado.resposta}")
        except Exception as erro:
            print(f"Erro: {erro}")


if __name__ == "__main__":
    main()
