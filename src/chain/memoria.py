"""Memória conversacional por sessão com limite de tokens."""
from typing import Dict, List, Sequence
import tiktoken
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory

LIMITE_TOKENS = 2000
ENCODING = "cl100k_base"

def contar_tokens(texto: str) -> int:
    return len(tiktoken.get_encoding(ENCODING).encode(texto))

class HistoricoComLimiteDeTokens(BaseChatMessageHistory):
    def __init__(self, limite_tokens: int = LIMITE_TOKENS):
        self._mensagens: List[BaseMessage] = []
        self._limite_tokens = limite_tokens

    @property
    def messages(self) -> List[BaseMessage]:
        return self._mensagens

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        self._mensagens.extend(messages)
        self._podar_por_limite_de_tokens()

    def clear(self) -> None:
        self._mensagens = []

    def _tokens_totais(self) -> int:
        texto = "\n".join(m.content for m in self._mensagens if isinstance(m.content, str))
        return contar_tokens(texto)

    def _podar_por_limite_de_tokens(self) -> None:
        while self._mensagens and self._tokens_totais() > self._limite_tokens:
            self._mensagens.pop(0)

historicos: Dict[str, HistoricoComLimiteDeTokens] = {}

def obter_historico(session_id: str) -> HistoricoComLimiteDeTokens:
    if session_id not in historicos:
        historicos[session_id] = HistoricoComLimiteDeTokens()
    return historicos[session_id]

def criar_chain_com_memoria(chain: Runnable, parser):
    memoria = RunnableWithMessageHistory(
        chain, obter_historico,
        input_messages_key="pergunta",
        history_messages_key="historico",
    )
    return memoria | parser
