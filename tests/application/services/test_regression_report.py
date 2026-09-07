from book_loop.application.services.regression_report import RegressionReportBuilder, RegressionRisk
from book_loop.domain.models import Assertion, CanonicalFact, Evidence


def fact(fid: str, aid: str, subject: str, predicate: str, obj: str) -> CanonicalFact:
    return CanonicalFact(
        id=fid, book_id="book-1", assertion_id=aid, statement=f"{subject} {predicate} {obj}",
        subject=subject, predicate=predicate, object=obj, decision_id=f"decision-{fid}",
        version=1, active=True, previous_fact_id=None,
    )


def assertion(aid: str, statement: str) -> Assertion:
    return Assertion(
        id=aid, source_document_id="source-1", chunk_id="chunk-1", statement=statement,
        subject="Bob", predicate="parent_of", object="Claire", confidence=0.9,
        evidence_id=f"evidence-{aid}",
    )


def evidence(aid: str) -> Evidence:
    return Evidence(
        id=f"evidence-{aid}", assertion_id=aid, source_document_id="source-1",
        chunk_id="chunk-1", start_offset=4, end_offset=20, excerpt="Bob parent_of Claire",
    )


def test_build_projects_transitive_impact_to_source_evidence() -> None:
    facts = [
        fact("f1", "a1", "Alice", "parent_of", "Bob"),
        fact("f2", "a2", "Bob", "parent_of", "Claire"),
        fact("f3", "a3", "Claire", "lives_in", "Paris"),
    ]
    assertions = [
        assertion("a2", "Bob parent_of Claire"),
        Assertion(
            id="a3", source_document_id="source-1", chunk_id="chunk-2", statement="Claire lives_in Paris",
            subject="Claire", predicate="lives_in", object="Paris", confidence=0.8, evidence_id="evidence-a3",
        ),
    ]
    evidence_items = [evidence("a2"), Evidence(
        id="evidence-a3", assertion_id="a3", source_document_id="source-1", chunk_id="chunk-2",
        start_offset=0, end_offset=21, excerpt="Claire lives_in Paris",
    )]

    report = RegressionReportBuilder().build(
        facts, assertions, evidence_items, changed_fact_id="f1"
    )

    assert report.changed_fact_id == "f1"
    assert [item.fact_id for item in report.findings] == ["f2", "f3"]
    assert report.findings[0].excerpt == "Bob parent_of Claire"
    assert report.findings[0].risk is RegressionRisk.HIGH
    assert report.findings[0].dependency_depth == 1
    assert report.findings[1].source_document_id == "source-1"
    assert report.findings[1].risk is RegressionRisk.MEDIUM
    assert report.findings[1].dependency_depth == 2


def test_build_skips_impacted_facts_without_persisted_evidence() -> None:
    facts = [fact("f1", "a1", "Alice", "parent_of", "Bob"), fact("f2", "a2", "Bob", "parent_of", "Claire")]
    assertions = [assertion("a2", "Bob parent_of Claire")]

    report = RegressionReportBuilder().build(facts, assertions, [], changed_fact_id="f1")

    assert report.findings == ()
