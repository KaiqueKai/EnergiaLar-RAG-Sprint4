from src.chain.builder import criar_chain
from src.chain.memoria import criar_chain_com_memoria
from src.guardrails.moderation import detectar_injection, detectar_risco
from src.guardrails.scope_validator import validar_escopo
from src.schemas.consulta_recarga import ConsultaRecarga


def criar_chatbot(modelo=None):
    """Cria o chatbot completo com LCEL, memória por sessão e guardrails."""
    chain, parser = criar_chain(modelo)
    return criar_chain_com_memoria(chain, parser)


def responder(chatbot, pergunta, session_id="usuario_1") -> ConsultaRecarga:
    pergunta = pergunta or ""
    if detectar_injection(pergunta):
        return ConsultaRecarga(estado_carregador="desconhecido", potencia_kw=None,
            faturamento_reais=None, resposta="Não posso ignorar minhas instruções ou revelar instruções internas do sistema.")
    if detectar_risco(pergunta):
        return ConsultaRecarga(estado_carregador="desconhecido", potencia_kw=None,
            faturamento_reais=None, resposta="Não posso orientar procedimentos de instalação, reparo ou intervenção elétrica. Para esse tipo de atividade, procure um profissional qualificado.")
    if not validar_escopo(pergunta):
        return ConsultaRecarga(estado_carregador="desconhecido", potencia_kw=None,
            faturamento_reais=None, resposta="Essa pergunta está fora do escopo do EnergiaLar. Posso ajudar com energia residencial, carregamento de veículos elétricos e produtos GoodWe.")
    try:
        return chatbot.invoke({"pergunta": pergunta}, config={"configurable": {"session_id": session_id}})
    except Exception:
        return ConsultaRecarga(estado_carregador="desconhecido", potencia_kw=None,
            faturamento_reais=None, resposta="Não consegui estruturar uma resposta confiável para essa pergunta. Pode reformular de um jeito mais específico? Se envolver risco elétrico, procure um profissional habilitado.")


if __name__ == "__main__":
    print("EnergiaLar - Assistente de eficiência energética")
    print("Digite 'sair' para encerrar.\n")
    chatbot = criar_chatbot()
    while True:
        pergunta = input("Você: ")
        if pergunta.lower().strip() == "sair":
            print("Encerrando...")
            break
        resultado = responder(chatbot, pergunta)
        print("\nEnergiaLar:")
        print(resultado.resposta, "\n")
