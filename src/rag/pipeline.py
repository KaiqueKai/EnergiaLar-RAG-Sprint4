"""Pipeline RAG: pergunta -> Chroma -> prompt versionado -> chat Cloud -> Pydantic -> fontes. Embeddings são configuráveis separadamente."""
from __future__ import annotations
import json
import re
from langchain_ollama import ChatOllama
from .settings import OLLAMA_HOST, OLLAMA_API_KEY, TEMPERATURE, TOP_P, MAX_TOKENS, CHAT_MODEL, validate_config
from .vector_store import build_or_load_vector_store
from .retriever import retrieve_context
from .prompt_rag import load_prompt
from .security import contains_possible_secret, is_out_of_scope_question, sanitize_user_question
from .citations import format_context_and_sources, ensure_source_citations
from src.schemas.consulta_recarga import ConsultaRecarga

OUT_OF_SCOPE = (
    "Não encontrei informação suficiente na base consultada para afirmar isso. "
    "O assistente cobre eficiência energética e recarga de veículos elétricos, "
    "GoodWe HCA G2, procedimentos orientativos de condomínio e os documentos tarifários presentes na base."
)


def _message_content(value) -> str:
    content = getattr(value, "content", value)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()
    return str(content).strip()


def _extract_json(text: str) -> str:
    """Aceita JSON puro ou cercado por bloco de código; não interpreta texto arbitrário."""
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("A resposta do modelo não contém um objeto JSON válido.")
    return cleaned[start:end + 1]


def _format_context(matches):
    """Mantém a API anterior do pacote RAG, com IDs consistentes por fonte/página."""
    return format_context_and_sources(matches)


def _chat_model(model_name: str | None = None) -> ChatOllama:
    validate_config(require_api_key=True)
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else {}
    kwargs = {"headers": headers} if headers else {}
    return ChatOllama(
        model=(model_name or CHAT_MODEL),
        base_url=OLLAMA_HOST,
        client_kwargs=kwargs,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        num_predict=MAX_TOKENS,
    )


def answer_question(
    question: str,
    model_name: str | None = None,
    prompt_version: str = "v2",
    vector_store=None,
    top_k: int | None = None,
    min_score: float | None = None,
) -> dict:
    """Responde com grounding e contrato Pydantic v2; fontes são expostas separadamente."""
    question = (question or "").strip()
    if not question:
        raise ValueError("Digite uma pergunta antes de consultar o RAG.")

    # Valida a versão antes de consultar o índice, inclusive no caminho de recusa.
    prompt = load_prompt(prompt_version)
    used_model = model_name or CHAT_MODEL
    question, injection_removed = sanitize_user_question(question)
    security_events = ["prompt_injection_clause_removed"] if injection_removed else []

    if not question:
        schema = ConsultaRecarga(
            estado_carregador="desconhecido", potencia_kw=None, faturamento_reais=None,
            resposta="A pergunta foi bloqueada porque continha apenas instruções maliciosas ou tentativa de revelar segredos.",
        )
        return {
            "answer": schema.resposta,
            "structured_answer": schema.model_dump(),
            "structure_valid": True,
            "sources": [],
            "prompt_version": prompt_version,
            "model": used_model,
            "relevance": "blocked_injection",
            "context": "",
            "security_events": security_events or ["prompt_injection_blocked"],
            "question_used": "",
        }

    # Recusa determinística para perguntas claramente alheias ao domínio, sem
    # consultar o modelo nem consumir créditos. A busca semântica continua sendo
    # responsável por perguntas relacionadas ao domínio.
    if is_out_of_scope_question(question):
        schema = ConsultaRecarga(
            estado_carregador="desconhecido",
            potencia_kw=None,
            faturamento_reais=None,
            resposta=OUT_OF_SCOPE,
        )
        return {
            "answer": schema.resposta,
            "structured_answer": schema.model_dump(),
            "structure_valid": True,
            "sources": [],
            "prompt_version": prompt_version,
            "model": used_model,
            "relevance": "out_of_scope",
            "context": "",
            "security_events": security_events,
            "question_used": question,
        }

    store = vector_store or build_or_load_vector_store()
    matches = retrieve_context(question, store, top_k=top_k, min_score=min_score)

    if not matches:
        schema = ConsultaRecarga(
            estado_carregador="desconhecido",
            potencia_kw=None,
            faturamento_reais=None,
            resposta=OUT_OF_SCOPE,
        )
        return {
            "answer": schema.resposta,
            "structured_answer": schema.model_dump(),
            "structure_valid": True,
            "sources": [],
            "prompt_version": prompt_version,
            "model": used_model,
            "relevance": "below_threshold",
            "context": "",
            "security_events": security_events,
            "question_used": question,
        }

    context, sources = format_context_and_sources(matches)
    raw_result = (prompt | _chat_model(model_name)).invoke({"question": question, "context": context})
    raw_text = _message_content(raw_result)

    if contains_possible_secret(raw_text) or (OLLAMA_API_KEY and OLLAMA_API_KEY in raw_text):
        blocked = "Resposta bloqueada pelo controle de saída porque continha um padrão semelhante a credencial. Nenhuma credencial foi exibida."
        safe_schema = ConsultaRecarga(
            estado_carregador="desconhecido", potencia_kw=None, faturamento_reais=None, resposta=blocked
        )
        return {
            "answer": blocked,
            "structured_answer": safe_schema.model_dump(),
            "structure_valid": True,
            "sources": sources,
            "prompt_version": prompt_version,
            "model": used_model,
            "relevance": max(score for _, score in matches),
            "context": context,
            "security_events": security_events + ["model_output_secret_blocked"],
            "question_used": question,
        }

    structure_valid = True
    try:
        data = json.loads(_extract_json(raw_text))
        schema = ConsultaRecarga.model_validate(data)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        structure_valid = False
        safe_schema = ConsultaRecarga(
            estado_carregador="desconhecido",
            potencia_kw=None,
            faturamento_reais=None,
            resposta=("Não foi possível validar a resposta estruturada do modelo. "
                      "A saída não foi publicada para evitar apresentar dados sem validação."),
        )
        answer = safe_schema.resposta
        parse_error = f"{type(exc).__name__}: {exc}"
    else:
        answer = ensure_source_citations(schema.resposta, sources)
        schema.resposta = answer
        safe_schema = schema
        parse_error = ""

    return {
        "answer": answer,
        "structured_answer": safe_schema.model_dump(),
        "structure_valid": structure_valid,
        "parse_error": parse_error,
        "sources": sources,
        "prompt_version": prompt_version,
        "model": used_model,
        "relevance": max(score for _, score in matches),
        "context": context,
        "security_events": security_events,
        "question_used": question,
    }
