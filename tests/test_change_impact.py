from book_loop.application.services.change_impact import ChangeImpactAnalyzer
from book_loop.domain.models import CanonicalFact


def fact(
    fact_id: str,
    *,
    subject: str,
    predicate: str,
    object: str,
    active: bool = True,
) -> CanonicalFact:
    return CanonicalFact(
        id=fact_id,
        book_id="book-1",
        assertion_id=f"assertion-{fact_id}",
        statement=f"{subject} {predicate} {object}",
        subject=subject,
        predicate=predicate,
        object=object,
        decision_id=f"decision-{fact_id}",
        active=active,
    )


def test_finds_direct_explicit_dependents() -> None:
    facts = [
        fact("f1", subject="Alice", predicate="parent_of", object="Bob"),
        fact("f2", subject="Bob", predicate="lives_in", object="Paris"),
        fact("f3", subject="Claire", predicate="lives_in", object="Rome"),
    ]

    result = ChangeImpactAnalyzer().analyze(facts, changed_fact_id="f1")

    assert result.affected_fact_ids == ("f2",)


def test_follows_transitive_explicit_dependencies() -> None:
    facts = [
        fact("f1", subject="Alice", predicate="parent_of", object="Bob"),
        fact("f2", subject="Bob", predicate="parent_of", object="Claire"),
        fact("f3", subject="Claire", predicate="lives_in", object="Paris"),
    ]

    result = ChangeImpactAnalyzer().analyze(facts, changed_fact_id="f1")

    assert result.affected_fact_ids == ("f2", "f3")


def test_ignores_inactive_facts() -> None:
    facts = [
        fact("f1", subject="Alice", predicate="parent_of", object="Bob"),
        fact("f2", subject="Bob", predicate="lives_in", object="Paris", active=False),
    ]

    result = ChangeImpactAnalyzer().analyze(facts, changed_fact_id="f1")

    assert result.affected_fact_ids == ()


def test_requires_active_changed_fact() -> None:
    facts = [
        fact("f1", subject="Alice", predicate="parent_of", object="Bob", active=False),
    ]

    try:
        ChangeImpactAnalyzer().analyze(facts, changed_fact_id="f1")
    except KeyError as exc:
        assert str(exc) == "'Unknown active canonical fact: f1'"
    else:
        raise AssertionError("Expected inactive changed fact to be rejected")
