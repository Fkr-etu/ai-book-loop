from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from langgraph.graph import END, START, StateGraph

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.policies.review import ReviewDecision, decide
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


@dataclass
class ChapterWorkflowState:
    book: BookState
    chapter_number: int
    attempt: int = 0
    draft: str = ""
    review_score: int | None = None
    decision: str | None = None
    summary: str | None = None


class ChapterWorkflow:
    def __init__(
        self,
        *,
        repository: BookRepository,
        writer: WriterAgent,
        reviewer: ReviewerAgent,
        summarizer: SummarizerAgent,
        context_builder: ContextBuilder,
        linter: ChapterLinter,
        max_retries: int = 3,
        review_threshold: int = 7,
    ) -> None:
        self.repository = repository
        self.writer = writer
        self.reviewer = reviewer
        self.summarizer = summarizer
        self.context_builder = context_builder
        self.linter = linter
        self.max_retries = max_retries
        self.review_threshold = review_threshold

    def _write(self, state: ChapterWorkflowState) -> dict:
        context = self.context_builder.for_chapter(state.book, state.chapter_number).render()
        draft = self.writer.write(context=context)
        attempt = state.attempt + 1
        self.repository.save_chapter_version(state.book.id, state.chapter_number, attempt, draft)
        return {"draft": draft, "attempt": attempt}

    def _review(self, state: ChapterWorkflowState) -> dict:
        context = self.context_builder.for_chapter(state.book, state.chapter_number).render()
        lint = self.linter.lint(state.draft)
        if not lint.valid:
            decision = ReviewDecision.RETRY if state.attempt < self.max_retries else ReviewDecision.NEEDS_REVIEW
            return {"decision": decision.value, "review_score": 0}

        review = self.reviewer.review(context=context, draft=state.draft)
        self.repository.save_review(state.book.id, state.chapter_number, state.attempt, review)
        decision = decide(
            review,
            attempt=state.attempt,
            max_retries=self.max_retries,
            threshold=self.review_threshold,
        )
        return {"decision": decision.value, "review_score": review.score}

    def _summarize(self, state: ChapterWorkflowState) -> dict:
        context = self.context_builder.for_chapter(state.book, state.chapter_number).render()
        summary = self.summarizer.summarize(context=context, chapter=state.draft)
        book = self.repository.get(state.book.id)
        chapter = next(c for c in book.chapters if c.number == state.chapter_number)
        chapter.status = "approved"
        chapter.current_version = state.attempt
        chapter.summary = summary
        self.repository.save(book)
        return {"summary": summary}

    def _route(self, state: ChapterWorkflowState) -> Literal["write", "summarize", "end"]:
        if state.decision == ReviewDecision.ACCEPT.value:
            return "summarize"
        if state.decision == ReviewDecision.RETRY.value:
            return "write"
        return "end"

    def build(self):
        graph = StateGraph(ChapterWorkflowState)
        graph.add_node("write", self._write)
        graph.add_node("review", self._review)
        graph.add_node("summarize", self._summarize)
        graph.add_edge(START, "write")
        graph.add_edge("write", "review")
        graph.add_conditional_edges(
            "review",
            self._route,
            {"write": "write", "summarize": "summarize", "end": END},
        )
        graph.add_edge("summarize", END)
        return graph.compile()

    def run(self, *, book: BookState, chapter_number: int) -> ChapterWorkflowState:
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before generating chapters")

        result = self.build().invoke(
            ChapterWorkflowState(book=book, chapter_number=chapter_number)
        )
        return ChapterWorkflowState(**result)
