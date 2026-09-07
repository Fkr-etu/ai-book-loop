from __future__ import annotations

from book_loop.application.use_cases.analyze_canon_change import AnalyzeCanonChange
from book_loop.domain.models import Assertion, CanonicalFact, Evidence


class FakeKnowledgeRepository:
    def __init__(self) -> None:
        self.facts = [
            CanonicalFact(
                id="f1", book_id="book-1", assertion_id="a1", statement="Alice parent_of Bob",
                subject="Alice", predicate="parent_of", object="Bob", decision_id="d1",
                version=1, active=True, previous_fact_id=None,
            ),
            CanonicalFact(
                id="f2", book_id="book-1", assertion_id="a2", statement="Bob parent_of Claire",
                subject="Bob", predicate="parent_of", object="Claire", decision_id="d2",
                version=1, active=True, previous_fact_id=None,
            ),
        ]
        self.assertions = [
            Assertion(
                id="a2", source_document_id="source-1", chunk_id="chunk-1", statement="Bob parent_of Claire",
                subject="Bob", predicate="parent_of", object="Claire", confidence=0.9,
                evidence_id="e2",
            )
        ]
        self.evidence = [
            Evidence(
                id="e2", assertion_id="a2", source_document_id="source-1", chunk_id="chunk-1",
                start_offset=0, end_offset=19, excerpt="Bob parent_of Claire",
            )
        ]
        self.requested_book_ids: list[str] = []

    def list_active_canonical_facts(self, *, book_id: str) -> list[CanonicalFact]:
        self.requested_book_ids.append(book_id)
        return self.facts

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        self.requested_book_ids.append(book_id)
        return self.assertions

    def list_evidence(self, *, book_id: str) -> list[Evidence]:
        self.requested_book_ids.append(book_id)
        return self.evidence


def test_analyze_canon_change_loads_book_scoped_data_and_builds_report() -> None:
    repository = FakeKnowledgeRepository()

    report = AnalyzeCanonChange(repository).execute(book_id="book-1", changed_fact_id="f1")

    assert repository.requested_book_ids == ["book-1", "book-1", "book-1"]
    assert report.changed_fact_id == "f1"
    assert len(report.findings) == 1
    assert report.findings[0].fact_id == "f2"
    assert report.findings[0].excerpt == "Bob parent_of Claire"


def test_analyze_canon_change_rejects_unknown_fact() -> None:
    repository = FakeKnowledgeRepository()

    try:
        AnalyzeCanonChange(repository).execute(book_id="book-1", changed_fact_id="missing")
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected unknown active fact to raise KeyError")
