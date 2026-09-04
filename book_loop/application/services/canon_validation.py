from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from book_loop.domain.models import (
    CanonicalFact,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    DocumentChunk,
    LinguisticCheckResult,
    LinguisticCheckStatus,
)
from book_loop.domain.protocols import AssertionExtractor, KnowledgeRepository


class CanonDiagnosticChecker:
    """Compare extracted chapter assertions with one book's active Canon."""

    def __init__(
        self,
        *,
        book_id: str,
        knowledge_repository: KnowledgeRepository,
        assertion_extractor: AssertionExtractor,
    ) -> None:
        if not book_id.strip():
            raise ValueError("CanonDiagnosticChecker requires a book id")
        self.book_id = book_id
        self._knowledge = knowledge_repository
        self._extractor = assertion_extractor

    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult:
        if language.lower() not in {"fr", "fr-fr"}:
            raise ValueError("CanonDiagnosticChecker currently supports only French")
        if not text.strip():
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.NO_ISSUES_FOUND,
                checker="canon",
            )

        try:
            chunk = DocumentChunk(
                id=str(uuid5(NAMESPACE_URL, f"canon-check:{self.book_id}:{text}")),
                source_document_id=f"canon-check:{self.book_id}",
                content=text,
                sequence=0,
                start_offset=0,
                end_offset=len(text),
                metadata={"ephemeral": "true"},
            )
            extracted = self._extractor.extract(chunk=chunk)
            facts = self._knowledge.list_active_canonical_facts(book_id=self.book_id)
            diagnostics = self._diagnostics(extracted, facts)
        except Exception as exc:
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.CHECK_NOT_AVAILABLE,
                checker="canon",
                error=str(exc),
            )

        return LinguisticCheckResult(
            status=(
                LinguisticCheckStatus.ISSUES_FOUND
                if diagnostics
                else LinguisticCheckStatus.NO_ISSUES_FOUND
            ),
            diagnostics=diagnostics,
            checker="canon",
        )

    @staticmethod
    def _diagnostics(extracted, facts: list[CanonicalFact]) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for assertion in extracted:
            for fact in facts:
                if not CanonDiagnosticChecker._same_subject_predicate(assertion, fact):
                    continue
                if assertion.object.strip().casefold() == fact.object.strip().casefold():
                    continue
                diagnostics.append(
                    Diagnostic(
                        category=DiagnosticCategory.CANON,
                        severity=DiagnosticSeverity.ERROR,
                        source=DiagnosticSource.CANON,
                        message=(
                            f"Chapter assertion contradicts active Canon fact: "
                            f"{fact.statement}"
                        ),
                        start_offset=assertion.start_offset,
                        end_offset=assertion.end_offset,
                        original_text=assertion.statement,
                        confidence=min(1.0, max(0.0, assertion.confidence)),
                        rule_id="CANON_ACTIVE_FACT_CONTRADICTION",
                        related_assertion_id=fact.assertion_id,
                        metadata={
                            "canonical_fact_id": fact.id,
                            "canonical_fact_version": str(fact.version),
                            "canonical_object": fact.object,
                            "chapter_subject": assertion.subject,
                            "chapter_predicate": assertion.predicate,
                            "chapter_object": assertion.object,
                        },
                    )
                )
        return diagnostics

    @staticmethod
    def _same_subject_predicate(assertion, fact: CanonicalFact) -> bool:
        return (
            assertion.subject.strip().casefold() == fact.subject.strip().casefold()
            and assertion.predicate.strip().casefold() == fact.predicate.strip().casefold()
        )
