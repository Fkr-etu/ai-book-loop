from __future__ import annotations

from dataclasses import dataclass

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.policies.review import ReviewDecision, decide
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState


@dataclass(frozen=True)
class ChapterRunResult:
    draft: str
    summary: str | None
    decision: ReviewDecision
    attempts: int


class ChapterWorkflow:
    """Framework-light orchestration for one chapter; LangGraph can wrap this loop later."""

    def __init__(self, writer: WriterAgent, reviewer: ReviewerAgent, summarizer: SummarizerAgent,
                 context_builder: ContextBuilder, linter: ChapterLinter, *, max_retries: int, threshold: int):
        self.writer = writer
        self.reviewer = reviewer
        self.summarizer = summarizer
        self.context_builder = context_builder
        self.linter = linter
        self.max_retries = max_retries
        self.threshold = threshold

    def run(self, book: BookState, chapter_number: int) -> ChapterRunResult:
        if not book.outline_approved:
            raise ValueError("The global outline must be approved before generating chapters")
        context = self.context_builder.for_chapter(book, chapter_number).render()
        draft = ""
        for attempt in range(1, self.max_retries + 1):
            draft = self.writer.write(context=context)
            lint = self.linter.lint(draft)
            if not lint.valid:
                continue
            review = self.reviewer.review(context=context, draft=draft)
            decision = decide(review, attempt=attempt, max_retries=self.max_retries, threshold=self.threshold)
            if decision == ReviewDecision.ACCEPT:
                summary = self.summarizer.summarize(context=context, chapter=draft)
                return ChapterRunResult(draft=draft, summary=summary, decision=decision, attempts=attempt)
        return ChapterRunResult(draft=draft, summary=None, decision=ReviewDecision.NEEDS_REVIEW, attempts=self.max_retries)
