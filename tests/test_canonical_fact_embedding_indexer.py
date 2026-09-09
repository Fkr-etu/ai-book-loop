from book_loop.application.services.canonical_fact_embedding_indexer import CanonicalFactEmbeddingIndexer
from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact


class StubEmbeddingProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def embed(self, *, text: str) -> tuple[float, ...]:
        self.calls.append(text)
        return (0.1, 0.2, 0.3)


class InMemoryEmbeddingStore:
    def __init__(self) -> None:
        self.items: dict[str, CanonicalFactEmbedding] = {}

    def get_canonical_fact_embedding(self, *, fact_id: str):
        return self.items.get(fact_id)

    def save_canonical_fact_embedding(self, embedding: CanonicalFactEmbedding) -> None:
        self.items[embedding.fact_id] = embedding


def make_fact(statement: str = "Alice lives in Lyon") -> CanonicalFact:
    return CanonicalFact(
        id="fact-1",
        book_id="book-1",
        assertion_id="assertion-1",
        statement=statement,
        subject="Alice",
        predicate="lives_in",
        object="Lyon",
        decision_id="decision-1",
        version=1,
        active=True,
        previous_fact_id=None,
    )


def test_index_persists_embedding_and_uses_fact_statement() -> None:
    provider = StubEmbeddingProvider()
    store = InMemoryEmbeddingStore()
    indexer = CanonicalFactEmbeddingIndexer(provider=provider, repository=store, model="test-model")

    embedding = indexer.index(make_fact("  Alice lives in Lyon  "))

    assert embedding == CanonicalFactEmbedding(
        fact_id="fact-1", embedding=(0.1, 0.2, 0.3), model="test-model"
    )
    assert store.items["fact-1"] == embedding
    assert provider.calls == ["Alice lives in Lyon"]


def test_index_reuses_existing_embedding_for_same_model() -> None:
    provider = StubEmbeddingProvider()
    store = InMemoryEmbeddingStore()
    existing = CanonicalFactEmbedding(
        fact_id="fact-1", embedding=(0.4, 0.5), model="test-model"
    )
    store.items["fact-1"] = existing
    indexer = CanonicalFactEmbeddingIndexer(provider=provider, repository=store, model="test-model")

    result = indexer.index(make_fact())

    assert result == existing
    assert provider.calls == []


def test_index_rebuilds_when_model_changes() -> None:
    provider = StubEmbeddingProvider()
    store = InMemoryEmbeddingStore()
    store.items["fact-1"] = CanonicalFactEmbedding(
        fact_id="fact-1", embedding=(0.4, 0.5), model="old-model"
    )
    indexer = CanonicalFactEmbeddingIndexer(provider=provider, repository=store, model="new-model")

    result = indexer.index(make_fact())

    assert result.model == "new-model"
    assert provider.calls == ["Alice lives in Lyon"]
    assert store.items["fact-1"] == result


def test_index_rejects_empty_fact_statement() -> None:
    provider = StubEmbeddingProvider()
    store = InMemoryEmbeddingStore()
    indexer = CanonicalFactEmbeddingIndexer(provider=provider, repository=store, model="test-model")

    try:
        indexer.index(make_fact("   "))
    except ValueError as exc:
        assert str(exc) == "Canonical fact statement must not be empty"
    else:
        raise AssertionError("Expected ValueError")
