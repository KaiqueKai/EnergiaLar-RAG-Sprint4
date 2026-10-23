"""Formatação consistente de contexto e referências de fonte para respostas RAG."""
from __future__ import annotations
import re

_CITATION_PATTERN = re.compile(r"\[(\d+)\]")


def _page_number(value) -> int:
    try:
        number = int(value)
        return number if number >= 0 else -1
    except (TypeError, ValueError):
        return -1


def format_context_and_sources(matches):
    """Numera fontes únicas por documento/página; vários chunks podem apontar à mesma fonte."""
    blocks: list[str] = []
    sources: list[dict] = []
    ids_by_key: dict[tuple[str, int], int] = {}

    for doc, raw_score in matches:
        metadata = getattr(doc, "metadata", {}) or {}
        name = str(metadata.get("source_name") or "documento_sem_nome")
        source_path = str(metadata.get("source") or name)
        page = _page_number(metadata.get("page", -1))
        key = (source_path, page)
        score = float(raw_score)

        if key not in ids_by_key:
            source_id = len(sources) + 1
            ids_by_key[key] = source_id
            page_label = f"página {page + 1}" if page >= 0 else "sem paginação"
            citation = f"[{source_id}] {name} ({page_label})"
            sources.append({
                "id": source_id,
                "name": name,
                "page": page + 1 if page >= 0 else None,
                "score": round(score, 4),
                "url": str(metadata.get("source_url") or ""),
                "citation": citation,
                "excerpt": str(getattr(doc, "page_content", ""))[:360].strip(),
                "source": source_path,
            })
        else:
            source_id = ids_by_key[key]
            current = sources[source_id - 1]
            current["score"] = round(max(float(current["score"]), score), 4)
            # Preserva até dois excertos curtos sem repetir o mesmo trecho.
            excerpt = str(getattr(doc, "page_content", ""))[:180].strip()
            if excerpt and excerpt not in current["excerpt"] and len(current["excerpt"]) < 360:
                current["excerpt"] = (current["excerpt"] + " … " + excerpt)[:360]

        citation = sources[source_id - 1]["citation"]
        blocks.append(f"{citation}\n{getattr(doc, 'page_content', '')}")

    return "\n\n---\n\n".join(blocks), sources


def ensure_source_citations(answer: str, sources: list[dict]) -> str:
    """Remove referências inexistentes e garante uma referência documental visível."""
    answer = (answer or "").strip()
    if not sources:
        return answer

    valid_ids = {int(source["id"]) for source in sources}

    def keep_valid(match):
        return match.group(0) if int(match.group(1)) in valid_ids else ""

    answer = _CITATION_PATTERN.sub(keep_valid, answer)
    answer = re.sub(r"[ \t]{2,}", " ", answer)
    references = "; ".join(source["citation"] for source in sources)
    footer = f"Fontes consultadas: {references}"
    if footer not in answer:
        answer = f"{answer}\n\n{footer}".strip()
    return answer
