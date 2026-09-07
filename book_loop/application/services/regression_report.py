from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from book_loop.domain.models import Assertion, CanonicalFact, Evidence
from book_loop.application.services.change_impact import ChangeImpactAnalyzer


@dataclass(frozen=True)
class RegressionFinding:
    """One affected assertion with its source evidence."""

    fact_id: str
    assertion_id: str
    statement: str
    source_document_id: str
    chunk_id: str
    excerpt: str
    start_offset: int
    end_offset: int


@dataclass(frozen=True)
class RegressionReport:
    """Evidence-backed projection of a canonical change impact."""

    changed_fact_id: str
    findings: tuple[RegressionFinding, ...]


class RegressionReportBuilder:
    """Project canonical change impact onto source-backed assertions.

    The builder only joins persisted identifiers. It does not infer semantic
    dependencies and does not mutate Canonical state.
    """

    def __init__(self, analyzer: ChangeImpactAnalyzer | None = None) -> None:
        self._analyzer = analyzer or ChangeImpactAnalyzer()

    def build(
        self,
        facts: Iterable[CanonicalFact],
        assertions: Iterable[Assertion],
        evidence: Iterable[Evidence],
        *,
        changed_fact_id: str,
    ) -> RegressionReport:
        facts_list = list(facts)
        impact = self._analyzer.analyze(facts_list, changed_fact_id=changed_fact_id)
        impacted_ids = set(impact.affected_fact_ids)

        fact_by_id = {fact.id: fact for fact in facts_list}
        assertions_by_id = {assertion.id: assertion for assertion in assertions}
        evidence_by_assertion = {item.assertion_id: item for item in evidence}

        findings: list[RegressionFinding] = []
        for fact_id in impact.affected_fact_ids:
            fact = fact_by_id[fact_id]
            assertion = assertions_by_id.get(fact.assertion_id)
            item = evidence_by_assertion.get(fact.assertion_id)
            if assertion is None or item is None:
                continue
            findings.append(
                RegressionFinding(
                    fact_id=fact.id,
                    assertion_id=assertion.id,
                    statement=assertion.statement,
                    source_document_id=item.source_document_id,
                    chunk_id=item.chunk_id,
                    excerpt=item.excerpt,
                    start_offset=item.start_offset,
                    end_offset=item.end_offset,
                )
            )

        return RegressionReport(
            changed_fact_id=changed_fact_id,
            findings=tuple(findings),
        )
