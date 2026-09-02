from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.application.services.retrieval_evaluation import (
    RetrievalEvaluationCase,
    RetrievalEvaluator,
)
from book_loop.domain.models import CanonicalFact


def fact(id: str, statement: str) -> CanonicalFact:
    return CanonicalFact(
        id=id,
        book_id="book-1",
        assertion_id=f"assertion-{id}",
        statement=statement,
        subject=statement.split()[0],
        predicate="has",
        object=statement.split()[-1],
        decision_id=f"decision-{id}",
    )


def test_evaluator_computes_precision_recall_hit_and_mrr() -> None:
    facts = [
        fact("a", "Alice has a red coat"),
        fact("b", "Bob has a blue boat"),
        fact("c", "Alice has a green scarf"),
    ]
    case = RetrievalEvaluationCase(
        query="Alice coat",
        relevant_fact_keys=frozenset({("a", 1)}),
    )

    result = RetrievalEvaluator(k=2).evaluate_case(CanonicalRetriever(), facts, case)

    assert result.precision_at_k == 0.5
    assert result.recall_at_k == 1.0
    assert result.hit_at_k is True
    assert result.mean_reciprocal_rank == 1.0


def test_evaluator_aggregates_cases_and_is_deterministic() -> None:
    facts = [
        fact("a", "Alice has a red coat"),
        fact("b", "Bob has a blue boat"),
        fact("c", "Alice has a green scarf"),
    ]
    cases = [
        RetrievalEvaluationCase("Alice coat", frozenset({("a", 1)})),
        RetrievalEvaluationCase("Bob boat", frozenset({("b", 1)})),
    ]
    evaluator = RetrievalEvaluator(k=1)

    first = evaluator.evaluate(CanonicalRetriever(top_k=3), facts, cases)
    second = evaluator.evaluate(CanonicalRetriever(top_k=3), facts, cases)

    assert first == second
    assert first.mean_precision_at_k == 1.0
    assert first.mean_recall_at_k == 1.0
    assert first.hit_rate_at_k == 1.0
    assert first.mean_reciprocal_rank == 1.0


def test_evaluator_handles_no_match_without_division_errors() -> None:
    facts = [fact("a", "Alice has a red coat")]
    case = RetrievalEvaluationCase("spaceship", frozenset({("b", 1)}))

    result = RetrievalEvaluator(k=3).evaluate_case(CanonicalRetriever(), facts, case)

    assert result.precision_at_k == 0.0
    assert result.recall_at_k == 0.0
    assert result.hit_at_k is False
    assert result.mean_reciprocal_rank == 0.0


def test_evaluator_validates_configuration() -> None:
    try:
        RetrievalEvaluator(k=0)
    except ValueError as exc:
        assert str(exc) == "k must be positive"
    else:
        raise AssertionError("expected ValueError")
