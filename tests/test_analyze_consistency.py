from book_loop.application.use_cases.analyze_consistency import AnalyzeConsistency
from book_loop.domain.models import Assertion, AssertionStatus, ConflictStatus, Evidence


class FakeKnowledgeRepository:
    def __init__(self) -> None:
        self.assertions: list[Assertion] = []
        self.evidence: list[Evidence] = []
        self.conflicts = []

    def list_assertions(self, *, book_id: str):
        return self.assertions

    def list_evidence(self, *, book_id: str):
        return self.evidence

    def list_conflicts(self, *, book_id: str):
        return self.conflicts

    def save_conflict(self, conflict):
        self.conflicts.append(conflict)


def assertion(*, assertion_id: str, object_value: str, evidence_id: str) -> Assertion:
    return Assertion(
        id=assertion_id,
        source_document_id=f"source-{assertion_id}",
        chunk_id=f"chunk-{assertion_id}",
        statement=f"Alice a les yeux {object_value}.",
        subject="Alice",
        predicate="eye_color",
        object=object_value,
        confidence=0.95,
        status=AssertionStatus.PROPOSED,
        evidence_id=evidence_id,
    )


def evidence(*, evidence_id: str, assertion_id: str, excerpt: str) -> Evidence:
    return Evidence(
        id=evidence_id,
        assertion_id=assertion_id,
        source_document_id=f"source-{assertion_id}",
        chunk_id=f"chunk-{assertion_id}",
        start_offset=0,
        end_offset=len(excerpt),
        excerpt=excerpt,
    )


def test_analysis_returns_evidence_backed_issue_without_deciding_for_author():
    repository = FakeKnowledgeRepository()
    repository.assertions = [
        assertion(assertion_id="a1", object_value="bleus", evidence_id="e1"),
        assertion(assertion_id="a2", object_value="verts", evidence_id="e2"),
    ]
    repository.evidence = [
        evidence(evidence_id="e1", assertion_id="a1", excerpt="Alice avait les yeux bleus."),
        evidence(evidence_id="e2", assertion_id="a2", excerpt="Alice avait les yeux verts."),
    ]

    issues = AnalyzeConsistency(repository).execute(book_id="book-1")

    assert len(issues) == 1
    issue = issues[0]
    assert issue.category == "contradiction"
    assert issue.severity == "warning"
    assert issue.status == ConflictStatus.OPEN.value
    assert issue.left_assertion_id == "a1"
    assert issue.right_assertion_id == "a2"
    assert issue.left_evidence
    assert issue.right_evidence
    assert issue.resolution_assertion_id is None


def test_analysis_is_idempotent_and_reuses_existing_conflict():
    repository = FakeKnowledgeRepository()
    repository.assertions = [
        assertion(assertion_id="a1", object_value="bleus", evidence_id="e1"),
        assertion(assertion_id="a2", object_value="verts", evidence_id="e2"),
    ]

    use_case = AnalyzeConsistency(repository)
    first = use_case.execute(book_id="book-1")
    second = use_case.execute(book_id="book-1")

    assert [issue.id for issue in first] == [issue.id for issue in second]
    assert len(repository.conflicts) == 1
