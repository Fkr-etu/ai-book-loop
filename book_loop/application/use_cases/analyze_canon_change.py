from __future__ import annotations

from book_loop.application.services.regression_report import RegressionReport, RegressionReportBuilder
from book_loop.domain.protocols import KnowledgeRepository


class AnalyzeCanonChange:
    """Analyze the source-backed regression impact of an active Canon fact."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        report_builder: RegressionReportBuilder | None = None,
    ) -> None:
        self.repository = repository
        self.report_builder = report_builder or RegressionReportBuilder()

    def execute(self, *, book_id: str, changed_fact_id: str) -> RegressionReport:
        facts = self.repository.list_active_canonical_facts(book_id=book_id)
        return self.report_builder.build(
            facts,
            self.repository.list_assertions(book_id=book_id),
            self.repository.list_evidence(book_id=book_id),
            changed_fact_id=changed_fact_id,
        )
