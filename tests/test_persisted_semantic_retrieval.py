from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.domain.embedding import CanonicalFactEmbedding
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


class Provider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def embed(self, *, text: str) -> tuple[float, ...]:
        self.calls.append(text)
        return (1.0, 0.0)


class Store:
    def __init__(self, entries: dict[str, CanonicalFactEmbedding]) -> None:
        self.entries = entries
        self.fact_ids: list[str] = []

    def list_canonical_fact_embeddings(self, *, fact_ids: list[str]) -> dict[str, CanonicalFactEmbedding]:
        self.fact_ids = fact_ids
        return {fact_id: self.entries[fact_id] for fact_id in fact_ids if fact_id in self.entries}


def test_retriever_uses_one_query_embedding_and_persisted_fact_vectors() -> None:
    facts = [fact("a", "Alice carries an amulet"), fact("b", "Bob carries a map")]
    provider = Provider()
    store = Store({
        "a": CanonicalFactEmbedding(fact_id="a", embedding=(1.0, 0.0), model="model-v1"),
        "b": CanonicalFactEmbedding(fact_id="b", embedding=(0.0, 1.0), model="model-v1"),
    })
    retriever = EmbeddingCanonicalRetriever(
        provider, embedding_store=store, embedding_model="model-v1"
    )

    result = retriever.retrieve(facts, query="protective charm")

    assert [item.id for item in result] == ["a", "b"]
    assert provider.calls == ["protective charm"]
    assert store.fact_ids == ["a", "b"]


def test_retriever_ignores_embeddings_from_another_model() -> None:
    facts = [fact("a", "Alice carries an amulet"), fact("b", "Bob carries a map")]
    provider = Provider()
    store = Store({
        "a": CanonicalFactEmbedding(fact_id="a", embedding=(1.0, 0.0), model="old-model"),
        "b": CanonicalFactEmbedding(fact_id="b", embedding=(0.0, 1.0), model="model-v1"),
    })
    retriever = EmbeddingCanonicalRetriever(
        provider, embedding_store=store, embedding_model="model-v1"
    )

    result = retriever.retrieve(facts, query="protective charm")

    assert [item.id for item in result] == ["b"]
    assert provider.calls == ["protective charm"]
