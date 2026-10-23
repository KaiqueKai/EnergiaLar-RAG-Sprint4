"""Busca semântica com expansão direcionada para evidências legais críticas."""
from __future__ import annotations

import re
import unicodedata

from .settings import TOP_K, MIN_RELEVANCE_SCORE


_ARTICLE_2_QUERY = (
    "Lei Estadual de São Paulo 18.403/2026, artigo 2: "
    "empreendimentos imobiliários com projetos aprovados após "
    "a entrada em vigor, capacidade mínima para instalação futura "
    "de estações de recarga e regulamentação técnica."
)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("º", "o").replace("ª", "a")
    return re.sub(r"\s+", " ", text).strip()


def _is_legal_condominium_question(question: str) -> bool:
    q = _normalize(question)
    legal_signals = (
        "18.403", "17.336", "lei estadual", "lei municipal",
        "referencias legais", "legislacao", "ambito legal",
    )
    domain_signals = ("condominio", "recarga", "estacao", "edificio", "edificacao")
    return any(term in q for term in legal_signals) and any(term in q for term in domain_signals)


def _is_article_2_capacity_chunk(doc) -> bool:
    text = _normalize(getattr(doc, "page_content", ""))
    has_article_2 = "artigo 2" in text or "art. 2" in text
    has_capacity = "capacidade minima" in text
    has_future_installation = "futura" in text or "instalacao futura" in text
    negates_capacity = any(phrase in text for phrase in (
        "sem capacidade minima", "nao ha capacidade minima",
        "nao preve capacidade minima", "nao prevê capacidade minima",
    ))
    return has_article_2 and has_capacity and has_future_installation and not negates_capacity


def _score_and_filter(matches, threshold: float):
    selected = []
    for doc, raw_score in matches:
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            continue
        if score >= threshold:
            selected.append((doc, score))
    return selected


def _dedup_key(doc):
    metadata = getattr(doc, "metadata", {}) or {}
    source = str(metadata.get("source") or metadata.get("source_name") or "")
    content = _normalize(getattr(doc, "page_content", ""))
    return source, content


def retrieve_context(question: str, vector_store, top_k: int | None = None, min_score: float | None = None):
    """Recupera top-k e acrescenta evidência crítica quando a pergunta é jurídica.

    A expansão garante que o trecho sobre o art. 2º da Lei Estadual 18.403/2026
    não seja eliminado por competir com trechos de art. 1º, lei municipal e protocolo.
    A expansão só acrescenta um trecho que aparece na busca dirigida e contém evidências textuais específicas; não inventa conteúdo. O limiar da busca suplementar é no máximo 0.70, mantendo o limiar global intacto para os resultados normais.
    """
    question = (question or "").strip()
    if not question:
        return []

    k = TOP_K if top_k is None else max(1, int(top_k))
    threshold = MIN_RELEVANCE_SCORE if min_score is None else float(min_score)
    primary = _score_and_filter(
        vector_store.similarity_search_with_relevance_scores(question, k=k),
        threshold,
    )

    # Para perguntas legais sobre condomínio/recarga, faz uma busca suplementar
    # focada no art. 2º estadual. A busca suplementar é local e não chama o chat.
    if _is_legal_condominium_question(question):
        try:
            supplemental_raw = vector_store.similarity_search_with_relevance_scores(
                _ARTICLE_2_QUERY,
                k=max(8, k),
            )
            # A evidência legal específica pode ficar ligeiramente abaixo do limiar global;
            # aceitamos até 0.70 apenas nesta busca dirigida, após validar artigo/capacidade/instalação futura.
            supplemental = _score_and_filter(supplemental_raw, min(threshold, 0.70))
            critical = [item for item in supplemental if _is_article_2_capacity_chunk(item[0])]
            if critical:
                best = max(critical, key=lambda item: item[1])
                existing = {_dedup_key(doc) for doc, _ in primary}
                if _dedup_key(best[0]) not in existing:
                    primary.append(best)
        except Exception as exc:
            # Não esconde erro: informa o diagnóstico, mas mantém os resultados
            # primários úteis para não derrubar perguntas que não dependem desse artigo.
            import warnings
            warnings.warn(
                f"Busca suplementar do art. 2º estadual falhou: {type(exc).__name__}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )

    # Dedupe pelo conteúdo real, não apenas por arquivo/página: arquivos Markdown
    # inteiros podem compartilhar metadata de página e conter chunks distintos.
    deduped = {}
    for doc, score in primary:
        key = _dedup_key(doc)
        if key not in deduped or score > deduped[key][1]:
            deduped[key] = (doc, score)

    return sorted(deduped.values(), key=lambda item: item[1], reverse=True)
