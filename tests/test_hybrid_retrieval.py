from book_loop.application.services.hybrid_retrieval import HybridCanonicalRetriever
from book_loop.domain.models import CanonicalFact


class FakeRetriever:
    def __init__(self, rankings: list[str]) -> None:
        self.rankings = rankings

    def retrieve(self, facts, *, query: str):
        by_id = {item.id: item for item in facts}
        return [by_id[item_id] for item_id in self.rankings if item_id in by_id]


def fact(fact_id: str, statement: str) -> CanonicalFact:
    return CanonicalFact(
        id=fact_id,
        book_id="book-1",
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject=fact_id,
        predicate="related_to",
        object="story",
        decision_id=f"decision-{fact_id}",
        version=1,
    )


def test_hybrid_fuses_lexical_and_semantic_rankings():
    facts = [fact("a", "Alice has a key"), fact("b", "The castle has a gate"), fact("c", "Bob has a map")]
    lexical = FakeRetriever(["a", "b"])
    semantic = FakeRetriever(["b", "c"])

    result = HybridCanonicalRetriever(lexical, semantic).retrieve(facts, query="key")

    assert [item.id for item in result] == ["b", "a", "c"]


def test_hybrid_order_is_deterministic_for_equal_rrf_scores():
    facts = [fact("b", "B"), fact("a", "A")]
    lexical = FakeRetriever(["b"])
    semantic = FakeRetriever(["a"])

    result = HybridCanonicalRetriever(lexical, semantic).retrieve(facts, query="x")

    assert [item.id for item in result] == ["a", "b"]


def test_hybrid_respects_top_k_and_empty_inputs():
    facts = [fact("a", "A"), fact("b", "B")]
    retriever = HybridCanonicalRetriever(FakeRetriever(["a", "b"]), FakeRetriever(["b", "a"]), top_k=1)

    assert [item.id for item in retriever.retrieve(facts, query="x")] == ["a"]
    assert retriever.retrieve([], query="x") == []
    assert retriever.retrieve(facts, query=" ") == []


def test_hybrid_rejects_invalid_configuration():
    lexical = FakeRetriever([])
    semantic = FakeRetriever([])

    for kwargs in ({"top_k": -1}, {"rrf_k": -1}):
        try:
            HybridCanonicalRetriever(lexical, semantic, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid configuration must raise ValueError")
