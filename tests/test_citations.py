from types import SimpleNamespace
from src.rag.citations import format_context_and_sources, ensure_source_citations


def doc(name, source, page, text, url="https://example.com"):
    return SimpleNamespace(
        metadata={"source_name": name, "source": source, "page": page, "source_url": url},
        page_content=text,
    )


def test_chunks_on_same_document_page_share_one_citation_id():
    matches = [
        (doc("manual.pdf", "data/manual.pdf", 0, "Potência: 7 kW."), 0.71),
        (doc("manual.pdf", "data/manual.pdf", 0, "Tensão: 230 V."), 0.92),
        (doc("manual.pdf", "data/manual.pdf", 1, "Outras informações."), 0.63),
    ]
    context, sources = format_context_and_sources(matches)

    assert len(sources) == 2
    assert sources[0]["id"] == 1
    assert sources[0]["score"] == 0.92
    assert sources[0]["page"] == 1
    assert sources[1]["id"] == 2
    assert sources[1]["page"] == 2
    assert context.count("[1] manual.pdf (página 1)") == 2
    assert "[2] manual.pdf (página 2)" in context


def test_citation_footer_includes_named_source_even_when_model_omits_citation():
    _, sources = format_context_and_sources([
        (doc("faq.md", "data/faq.md", -1, "A sessão simulada multiplica kW por horas."), 0.8)
    ])
    answer = ensure_source_citations("A energia ideal é potência vezes duração.", sources)
    assert "Fontes consultadas:" in answer
    assert "[1] faq.md (sem paginação)" in answer


def test_invalid_model_citation_is_removed_but_real_source_is_attached():
    _, sources = format_context_and_sources([
        (doc("faq.md", "data/faq.md", -1, "Energia e potência."), 0.8)
    ])
    answer = ensure_source_citations("Resposta sem respaldo [77].", sources)
    assert "[77]" not in answer
    assert "[1] faq.md" in answer
