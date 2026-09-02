import pytest

from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.domain.models import CanonicalFact


def fact(fact_id: str, statement: str) -> CanonicalFact:
    return CanonicalFact(
        id=fact_id,
        book_id="book-1",
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject=fact_id,
        predicate="has fact",
        object=statement,
        decision_id=f"decision-{fact_id}",
        version=1,
    )


class FakeEmbeddingProvider:
    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self.vectors = vectors

    def embed(self, *, text: str) -> tuple[float, ...]:
        return self.vectors[text]


def test_embedding_retriever_ranks_by_cosine_similarity():
    facts = [fact("a", "Alice has a silver key"), fact("b", "The castle has a red gate")]
    query = "Alice key"
    provider = FakeEmbeddingProvider(
        {
            query: (1.0, 0.0),
            "Alice has a silver key Alice has fact Alice has a silver key": (0.99, 0.1),
            "The castle has a red gate The castle has fact The castle has a red gate": (0.0, 1.0),
        }
    )

    result = EmbeddingCanonicalRetriever(provider).retrieve(facts, query=query)

    assert [item.id for item in result] == ["a", "b"]


def test_embedding_retriever_is_deterministic_on_equal_scores():
    facts = [fact("b", "Bob fact"), fact("a", "Alice fact")]
    query = "query"
    provider = FakeEmbeddingProvider(
        {
            query: (1.0, 0.0),
            "Bob fact b has fact Bob fact": (1.0, 0.0),
            "Alice fact a has fact Alice fact": (1.0, 0.0),
        }
    )

    result = EmbeddingCanonicalRetriever(provider).retrieve(facts, query=query)

    assert [item.id for item in result] == ["a", "b"]


def test_embedding_retriever_respects_top_k_and_min_score():
    facts = [fact("a", "close"), fact("b", "far")]
    query = "query"
    provider = FakeEmbeddingProvider(
        {
            query: (1.0, 0.0),
            "close a has fact close": (1.0, 0.0),
            "far b has fact far": (0.0, 1.0),
        }
    )
    retriever = EmbeddingCanonicalRetriever(provider, top_k=1, min_score=0.5)

    assert [item.id for item in retriever.retrieve(facts, query=query)] == ["a"]


def test_embedding_retriever_rejects_invalid_dimensions():
    facts = [fact("a", "Alice fact")]
    query = "query"
    provider = FakeEmbeddingProvider(
        {query: (1.0, 0.0), "Alice fact a has fact Alice fact": (1.0,)}
    )

    with pytest.raises(ValueError, match="dimensions"):
        EmbeddingCanonicalRetriever(provider).retrieve(facts, query=query)
