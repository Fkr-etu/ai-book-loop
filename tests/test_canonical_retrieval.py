from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.domain.models import CanonicalFact


def fact(fact_id: str, statement: str, subject: str, predicate: str, object_: str) -> CanonicalFact:
    return CanonicalFact(
        id=fact_id,
        book_id="book-1",
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject=subject,
        predicate=predicate,
        object=object_,
        decision_id=f"decision-{fact_id}",
        version=1,
    )


def test_retriever_selects_relevant_facts_and_omits_irrelevant_ones():
    facts = [
        fact("z", "Alice owns a silver key", "Alice", "owns", "silver key"),
        fact("a", "The castle has a red gate", "castle", "has", "red gate"),
    ]

    result = CanonicalRetriever(top_k=10).retrieve(facts, query="Alice key")

    assert [item.id for item in result] == ["z"]


def test_retriever_order_is_deterministic_on_equal_scores():
    facts = [
        fact("b", "Alice knows Bob", "Alice", "knows", "Bob"),
        fact("a", "Alice knows Clara", "Alice", "knows", "Clara"),
    ]

    result = CanonicalRetriever().retrieve(facts, query="Alice knows")

    assert [item.id for item in result] == ["a", "b"]


def test_retriever_respects_top_k_and_empty_match():
    facts = [
        fact("a", "Alice is 32 years old", "Alice", "age", "32"),
        fact("b", "Bob is 41 years old", "Bob", "age", "41"),
    ]
    retriever = CanonicalRetriever(top_k=1)

    assert [item.id for item in retriever.retrieve(facts, query="Alice Bob age")] == ["a"]
    assert retriever.retrieve(facts, query="spaceship Mars") == []
