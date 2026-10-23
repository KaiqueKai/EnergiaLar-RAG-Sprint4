from types import SimpleNamespace

from src.rag.retriever import retrieve_context


ARTICLE_2_QUERY_PART = "empreendimentos imobiliários com projetos aprovados após"


def make_doc(text, source="data/06_referencias_condominiais_sp.md"):
    return SimpleNamespace(
        page_content=text,
        metadata={"source": source, "source_name": "06_referencias_condominiais_sp.md", "page": -1},
    )


class QueryAwareStore:
    def __init__(self, primary, supplemental):
        self.primary = primary
        self.supplemental = supplemental
        self.calls = []

    def similarity_search_with_relevance_scores(self, question, k=4):
        self.calls.append(question)
        results = self.supplemental if ARTICLE_2_QUERY_PART in question else self.primary
        return results[:k]


def test_legal_condominium_question_adds_article_2_capacity_evidence():
    ordinary = [
        (make_doc("Lei estadual, artigo 1º: instalação individual em vaga privativa."), 0.80),
        (make_doc("Lei municipal: medição individualizada em edifícios do município."), 0.77),
        (make_doc("Protocolo orientativo para operação de recarga compartilhada." , "data/03_condominio_protocolo_orientativo.md"), 0.70),
    ]
    article_2_text = (
        "O artigo 2º aborda empreendimentos com projetos aprovados depois da entrada em vigor "
        "e prevê capacidade mínima para instalação futura, com regulamentação técnica a ser definida."
    )
    supplemental = [(make_doc(article_2_text), 0.7442)]
    store = QueryAwareStore(ordinary, supplemental)

    result = retrieve_context(
        "Quais cuidados para recarga compartilhada em condomínio e qual o alcance das referências legais de São Paulo?",
        store,
        top_k=3,
    )

    retrieved_text = "\n".join(doc.page_content for doc, _ in result).lower()
    assert "artigo 2º" in retrieved_text
    assert "capacidade mínima" in retrieved_text
    assert len(store.calls) == 2
    assert len(result) == 4  # top-k principal + o trecho crítico obrigatório


def test_non_legal_question_does_not_run_supplemental_search():
    store = QueryAwareStore([(make_doc("A sessão didática multiplica kW por horas."), 0.8)], [])
    result = retrieve_context("Como calcular energia consumida em uma sessão?", store)
    assert len(result) == 1
    assert len(store.calls) == 1


def test_supplemental_chunk_must_contain_article_and_capacity_evidence():
    ordinary = [(make_doc("Lei estadual, artigo 1º: instalação individual."), 0.8)]
    irrelevant = [(make_doc("O artigo 2º trata de prazos, sem capacidade mínima para instalação futura."), 0.9)]
    store = QueryAwareStore(ordinary, irrelevant)
    result = retrieve_context("Quais leis se aplicam a recarga em condomínio?", store)
    assert len(result) == 1
