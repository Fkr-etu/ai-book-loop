from book_loop.application.services.canon_validation import CanonDiagnosticChecker
from book_loop.domain.models import (
    CanonicalFact,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    ExtractedAssertion,
    LinguisticCheckStatus,
)


class FakeExtractor:
    def __init__(self, assertions):
        self.assertions = assertions
        self.chunks = []

    def extract(self, *, chunk):
        self.chunks.append(chunk)
        return self.assertions


class FakeKnowledge:
    def __init__(self, facts):
        self.facts = facts
        self.book_ids = []

    def list_active_canonical_facts(self, *, book_id):
        self.book_ids.append(book_id)
        return self.facts


def fact(*, object_value="Marseille", assertion_id="canon-assertion"):
    return CanonicalFact(
        id="canon-fact",
        book_id="book-1",
        assertion_id=assertion_id,
        statement=f"Marie vit à {object_value}.",
        subject="Marie",
        predicate="lives_in",
        object=object_value,
        decision_id="decision-1",
        version=1,
        active=True,
    )


def assertion(*, object_value="Lyon"):
    statement = f"Marie vit à {object_value}."
    return ExtractedAssertion(
        statement=statement,
        subject="Marie",
        predicate="lives_in",
        object=object_value,
        confidence=0.94,
        start_offset=0,
        end_offset=len(statement),
    )


def make_checker(*, facts, assertions, book_id="book-1"):
    return CanonDiagnosticChecker(
        book_id=book_id,
        knowledge_repository=FakeKnowledge(facts),
        assertion_extractor=FakeExtractor(assertions),
    )


def test_detects_active_canon_contradiction_with_provenance():
    result = make_checker(facts=[fact()], assertions=[assertion()]).check(
        "Marie vit à Lyon."
    )

    assert result.status == LinguisticCheckStatus.ISSUES_FOUND
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.category == DiagnosticCategory.CANON
    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.source == DiagnosticSource.CANON
    assert diagnostic.rule_id == "CANON_ACTIVE_FACT_CONTRADICTION"
    assert diagnostic.related_assertion_id == "canon-assertion"
    assert diagnostic.start_offset == 0
    assert diagnostic.end_offset == len("Marie vit à Lyon.")
    assert diagnostic.metadata["canonical_fact_id"] == "canon-fact"
    assert diagnostic.metadata["canonical_fact_version"] == "1"
    assert diagnostic.metadata["canonical_object"] == "Marseille"
    assert diagnostic.metadata["chapter_object"] == "Lyon"


def test_compatible_restatement_is_not_a_contradiction():
    result = make_checker(
        facts=[fact()], assertions=[assertion(object_value="Marseille")]
    ).check("Marie vit à Marseille.")

    assert result.status == LinguisticCheckStatus.NO_ISSUES_FOUND
    assert result.diagnostics == []


def test_ignores_unrelated_subject_or_predicate():
    unrelated = ExtractedAssertion(
        statement="Paul travaille à Lyon.",
        subject="Paul",
        predicate="works_in",
        object="Lyon",
        confidence=0.9,
        start_offset=0,
        end_offset=len("Paul travaille à Lyon."),
    )

    result = make_checker(facts=[fact()], assertions=[unrelated]).check(
        "Paul travaille à Lyon."
    )

    assert result.status == LinguisticCheckStatus.NO_ISSUES_FOUND


def test_repository_contract_exposes_only_active_facts():
    result = make_checker(facts=[], assertions=[assertion()]).check(
        "Marie vit à Lyon."
    )

    assert result.status == LinguisticCheckStatus.NO_ISSUES_FOUND


def test_extractor_failure_is_visible_as_unavailable():
    class FailingExtractor:
        def extract(self, *, chunk):
            raise RuntimeError("extractor unavailable")

    result = CanonDiagnosticChecker(
        book_id="book-1",
        knowledge_repository=FakeKnowledge([fact()]),
        assertion_extractor=FailingExtractor(),
    ).check("Marie vit à Lyon.")

    assert result.status == LinguisticCheckStatus.CHECK_NOT_AVAILABLE
    assert "extractor unavailable" in result.error


def test_non_french_language_is_rejected():
    checker = make_checker(facts=[], assertions=[])

    try:
        checker.check("Marie lives in Lyon.", language="en")
    except ValueError as exc:
        assert "only French" in str(exc)
    else:
        raise AssertionError("Expected non-French validation to fail")


def test_book_id_is_required():
    try:
        CanonDiagnosticChecker(
            book_id="",
            knowledge_repository=FakeKnowledge([]),
            assertion_extractor=FakeExtractor([]),
        )
    except ValueError as exc:
        assert "book id" in str(exc)
    else:
        raise AssertionError("Expected missing book id to fail")
