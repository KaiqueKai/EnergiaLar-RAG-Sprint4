from types import SimpleNamespace
from src.rag.retriever import retrieve_context


class FakeVectorStore:
    def __init__(self, results):
        self.results = results
        self.last_question = None
        self.last_k = None

    def similarity_search_with_relevance_scores(self, question, k=4):
        self.last_question = question
        self.last_k = k
        return self.results[:k]


def test_retriever_filters_results_below_threshold():
    good = SimpleNamespace(page_content="fonte relevante", metadata={})
    weak = SimpleNamespace(page_content="fonte fraca", metadata={})
    store = FakeVectorStore([(good, 0.8), (weak, 0.1)])
    result = retrieve_context("Pergunta", store, top_k=2, min_score=0.5)
    assert len(result) == 1
    assert result[0][0].page_content == "fonte relevante"
    assert store.last_question == "Pergunta"
    assert store.last_k == 2


def test_retriever_empty_question_does_not_call_store():
    store = FakeVectorStore([])
    assert retrieve_context("  ", store) == []
    assert store.last_question is None
