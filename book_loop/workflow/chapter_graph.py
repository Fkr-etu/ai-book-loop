from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from typing import Literal
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from book_loop.agents.corrector import CorrectorAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.policies.review import ReviewDecision, decide
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linguistic_validation import LinguisticValidationService
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import (
    BookState,
    ChapterStatus,
    Diagnostic,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckStatus,
    SceneReview,
)
from book_loop.domain.workflow import ChapterWorkflowRun, WorkflowRunStatus, WorkflowStep
from book_loop.domain.protocols import BookRepository
from book_loop.infrastructure.database.workflow_store import SQLiteWorkflowRunStore


@dataclass
class ChapterWorkflowState:
    book: BookState
    chapter_number: int
    attempt: int = 0
    draft: str = ""
    review_score: float | None = None
    review: SceneReview | None = None
    decision: str | None = None
    summary: str | None = None
    idempotency_key: str = ""
    step: str = WorkflowStep.WRITE.value


class ChapterWorkflow:
    """Generate, validate, review and correct a chapter with durable checkpoints."""

    _locks: dict[str, Lock] = {}
    _locks_guard = Lock()

    def __init__(
        self,
        *,
        repository: BookRepository,
        writer: WriterAgent,
        reviewer: ReviewerAgent,
        summarizer: SummarizerAgent,
        context_builder: ContextBuilder,
        linter: ChapterLinter,
        corrector: CorrectorAgent | None = None,
        linguistic_validator_factory: Callable[[BookState], LinguisticValidationService]
        | None = None,
        linguistic_contextualizer: Callable[[str, list[Diagnostic]], list[Diagnostic]] | None = None,
        linguistic_language: str = "fr",
        max_retries: int = 3,
        review_threshold: int = 7,
        workflow_store=None,
    ) -> None:
        if max_retries <= 0:
            raise ValueError("max_retries must be positive")
        if not linguistic_language.strip():
            raise ValueError("linguistic_language must not be empty")
        self.repository = repository
        self.writer = writer
        self.reviewer = reviewer
        self.summarizer = summarizer
        self.context_builder = context_builder
        self.linter = linter
        self.corrector = corrector or CorrectorAgent(writer.llm)
        self.linguistic_validator_factory = linguistic_validator_factory
        self.linguistic_contextualizer = linguistic_contextualizer
        self.linguistic_language = linguistic_language
        self.max_retries = max_retries
        self.review_threshold = review_threshold
        self.workflow_store = workflow_store

    def _store(self):
        if self.workflow_store is not None:
            return self.workflow_store
        return None

    @classmethod
    def _lock_for(cls, key: str) -> Lock:
        with cls._locks_guard:
            return cls._locks.setdefault(key, Lock())

    def _next_attempt(self, state: ChapterWorkflowState) -> int:
        attempt = state.attempt + 1
        while True:
            try:
                self.repository.get_chapter_version(state.book.id, state.chapter_number, attempt)
            except KeyError:
                return attempt
            attempt += 1

    def _write(self, state: ChapterWorkflowState) -> dict:
        context = self.context_builder.for_chapter(state.book, state.chapter_number)
        draft = self.writer.write(context=context)
        attempt = self._next_attempt(state)
        self.repository.save_chapter_version(state.book.id, state.chapter_number, attempt, draft)
        return {"draft": draft, "attempt": attempt}

    @staticmethod
    def _review_from_linguistic_diagnostics(
        diagnostics: list[Diagnostic], *, unavailable_error: str | None = None
    ) -> SceneReview:
        issues = [diagnostic.message for diagnostic in diagnostics]
        suggestions = [suggestion for diagnostic in diagnostics for suggestion in diagnostic.suggestions]
        if unavailable_error:
            issues.insert(0, f"Linguistic validation unavailable: {unavailable_error}")
        return SceneReview(
            score=0,
            approved=False,
            issues=issues,
            suggestions=suggestions or ["Correct the blocking linguistic diagnostics before review."],
        )

    def _linguistic_review(self, state: ChapterWorkflowState) -> tuple[SceneReview | None, list[Diagnostic]]:
        if self.linguistic_validator_factory is None:
            return None, []
        result = self.linguistic_validator_factory(state.book).validate(
            state.draft, language=self.linguistic_language
        )
        diagnostics = list(result.diagnostics)
        if self.linguistic_contextualizer and diagnostics:
            contextualized = [d for d in diagnostics if d.source != DiagnosticSource.CANON]
            canon = [d for d in diagnostics if d.source == DiagnosticSource.CANON]
            if contextualized:
                contextualized = self.linguistic_contextualizer(state.draft, contextualized)
            diagnostics = contextualized + canon
        if result.status == LinguisticCheckStatus.CHECK_NOT_AVAILABLE:
            return self._review_from_linguistic_diagnostics(
                diagnostics, unavailable_error=result.error or "unknown checker failure"
            ), diagnostics
        blocking = [d for d in diagnostics if d.severity == DiagnosticSeverity.ERROR]
        if blocking:
            return self._review_from_linguistic_diagnostics(blocking), diagnostics
        return None, diagnostics

    def _review(self, state: ChapterWorkflowState) -> dict:
        context = self.context_builder.for_chapter(state.book, state.chapter_number)
        lint = self.linter.lint(state.draft)
        diagnostics: list[Diagnostic] = []
        if not lint.valid:
            review = SceneReview(
                score=0,
                approved=False,
                issues=lint.errors,
                suggestions=["Remove all lint errors before the next review."],
            )
        else:
            linguistic_review, diagnostics = self._linguistic_review(state)
            if linguistic_review is not None:
                review = linguistic_review
            else:
                review = self.reviewer.review(context=context, draft=state.draft, diagnostics=diagnostics)
        self.repository.save_review(state.book.id, state.chapter_number, state.attempt, review)
        decision = decide(
            review,
            attempt=state.attempt,
            max_retries=self.max_retries,
            threshold=self.review_threshold,
        )
        return {"decision": decision.value, "review_score": review.score, "review": review}

    def _correct(self, state: ChapterWorkflowState) -> dict:
        if state.review is None:
            raise ValueError("A review is required before correction")
        context = self.context_builder.for_chapter(state.book, state.chapter_number)
        draft = self.corrector.correct(context=context, draft=state.draft, review=state.review)
        attempt = self._next_attempt(state)
        self.repository.save_chapter_version(state.book.id, state.chapter_number, attempt, draft)
        return {"draft": draft, "attempt": attempt}

    def _summarize(self, state: ChapterWorkflowState) -> dict:
        context = self.context_builder.for_chapter(state.book, state.chapter_number)
        summary = self.summarizer.summarize(context=context, chapter=state.draft)
        book = self.repository.get(state.book.id)
        chapter = next(c for c in book.chapters if c.number == state.chapter_number)
        chapter.status = ChapterStatus.APPROVED
        chapter.current_version = state.attempt
        chapter.summary = summary
        self.repository.save(book)
        return {"summary": summary}

    def _route(self, state: ChapterWorkflowState) -> Literal["correct", "summarize", "end"]:
        if state.decision == ReviewDecision.ACCEPT.value:
            return "summarize"
        if state.decision == ReviewDecision.RETRY.value:
            return "correct"
        return "end"

    def build(self):
        graph = StateGraph(ChapterWorkflowState)
        graph.add_node("write", self._write)
        graph.add_node("review", self._review)
        graph.add_node("correct", self._correct)
        graph.add_node("summarize", self._summarize)
        graph.add_edge(START, "write")
        graph.add_edge("write", "review")
        graph.add_conditional_edges("review", self._route, {"correct": "correct", "summarize": "summarize", "end": END})
        graph.add_edge("correct", "review")
        graph.add_edge("summarize", END)
        return graph.compile()

    def _state_from_run(self, book: BookState, run: ChapterWorkflowRun) -> ChapterWorkflowState:
        return ChapterWorkflowState(
            book=book,
            chapter_number=run.chapter_number,
            attempt=run.attempt,
            draft=run.draft,
            review_score=run.review.score if run.review else None,
            review=run.review,
            decision=run.decision,
            summary=run.summary,
            idempotency_key=run.idempotency_key,
            step=run.step.value,
        )

    def _checkpoint(self, run: ChapterWorkflowRun) -> None:
        self._store().save(run)

    def _run_stepwise(self, *, book: BookState, run: ChapterWorkflowRun) -> ChapterWorkflowState:
        state = self._state_from_run(book, run)
        while run.status == WorkflowRunStatus.RUNNING:
            if run.step == WorkflowStep.WRITE:
                if run.attempt == 0:
                    run.attempt = self._next_attempt(state)
                    self._checkpoint(run)
                try:
                    draft = self.repository.get_chapter_version(book.id, run.chapter_number, run.attempt)
                except KeyError:
                    context = self.context_builder.for_chapter(book, run.chapter_number)
                    draft = self.writer.write(context=context)
                    self.repository.save_chapter_version(book.id, run.chapter_number, run.attempt, draft)
                run.draft = draft
                run.step = WorkflowStep.REVIEW
                self._checkpoint(run)
                state = self._state_from_run(book, run)
                continue

            if run.step == WorkflowStep.REVIEW:
                state = self._state_from_run(book, run)
                result = self._review(state) if run.review is None else {
                    "decision": run.decision,
                    "review_score": run.review.score,
                    "review": run.review,
                }
                run.review = result["review"]
                run.decision = result["decision"]
                run.step = (
                    WorkflowStep.SUMMARIZE
                    if run.decision == ReviewDecision.ACCEPT.value
                    else WorkflowStep.CORRECT
                    if run.decision == ReviewDecision.RETRY.value
                    else WorkflowStep.REVIEW
                )
                if run.step == WorkflowStep.REVIEW:
                    run.status = WorkflowRunStatus.NEEDS_REVIEW
                self._checkpoint(run)
                continue

            if run.step == WorkflowStep.CORRECT:
                state = self._state_from_run(book, run)
                next_attempt = self._next_attempt(state)
                run.attempt = next_attempt
                run.review = run.review
                self._checkpoint(run)
                try:
                    draft = self.repository.get_chapter_version(book.id, run.chapter_number, next_attempt)
                except KeyError:
                    context = self.context_builder.for_chapter(book, run.chapter_number)
                    draft = self.corrector.correct(context=context, draft=run.draft, review=run.review)
                    self.repository.save_chapter_version(book.id, run.chapter_number, next_attempt, draft)
                run.draft = draft
                run.step = WorkflowStep.REVIEW
                self._checkpoint(run)
                continue

            if run.step == WorkflowStep.SUMMARIZE:
                state = self._state_from_run(book, run)
                if run.summary is None:
                    run.summary = self.summarizer.summarize(
                        context=self.context_builder.for_chapter(book, run.chapter_number),
                        chapter=run.draft,
                    )
                updated_book = self.repository.get(book.id)
                chapter = next(c for c in updated_book.chapters if c.number == run.chapter_number)
                chapter.status = ChapterStatus.APPROVED
                chapter.current_version = run.attempt
                chapter.summary = run.summary
                self.repository.save(updated_book)
                run.status = WorkflowRunStatus.COMPLETED
                self._checkpoint(run)
                continue

        return self._state_from_run(book, run)

    def run(
        self,
        *,
        book: BookState,
        chapter_number: int,
        idempotency_key: str | None = None,
    ) -> ChapterWorkflowState:
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before generating chapters")
        key = idempotency_key or str(uuid4())
        if self._store() is None:
            # Tests and lightweight callers keep the same restart semantics in-process.
            from book_loop.infrastructure.database.workflow_store import InMemoryWorkflowRunStore

            self.workflow_store = InMemoryWorkflowRunStore()
        lock_key = f"{book.id}:{chapter_number}:{key}"
        with self._lock_for(lock_key):
            run = self._store().get_or_create(
                book_id=book.id, chapter_number=chapter_number, idempotency_key=key
            )
            if run.status in {WorkflowRunStatus.COMPLETED, WorkflowRunStatus.NEEDS_REVIEW}:
                return self._state_from_run(book, run)
            return self._run_stepwise(book=book, run=run)
