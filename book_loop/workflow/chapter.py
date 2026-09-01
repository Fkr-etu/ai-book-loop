from __future__ import annotations

from dataclasses import dataclass

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.policies.review import ReviewDecision, decide
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


@dataclass(frozen=True)
class ChapterRunResult:
    draft: str
    summary: str | None
    decision: ReviewDecision
    attempts: int


class ChapterWorkflow:
    """Orchestrate one chapter without coupling the core loop to a graph framework."""

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

    def run(self, *, book: BookState, chapter_number: int) -> ChapterRunResult:
        if not book.outline_approved:
            raise ValueError("The global outline must be approved before generating chapters")

        context = self.context_builder.for_chapter(book, chapter_number).render()
        draft = ""
        for attempt in range(1, self.max_retries + 1):
            draft = self.writer.write(context=context)
            self.repository.save_chapter_version(book.id, chapter_number, attempt, draft)

            lint = self.linter.lint(draft)
            if not lint.valid:
                if attempt == self.max_retries:
                    return ChapterRunResult(draft, None, ReviewDecision.NEEDS_REVIEW, attempt)
                continue

            review = self.reviewer.review(context=context, draft=draft)
            self.repository.save_review(book.id, chapter_number, attempt, review)
            decision = decide(
                review,
                attempt=attempt,
                max_retries=self.max_retries,
                threshold=self.review_threshold,
            )

            if decision == ReviewDecision.ACCEPT:
                summary = self.summarizer.summarize(context=context, chapter=draft)
                updated_book = self.repository.get(book.id)
                chapter = next(c for c in updated_book.chapters if c.number == chapter_number)
                chapter.status = "approved"
                chapter.current_version = attempt
                chapter.summary = summary
                self.repository.save(updated_book)
                return ChapterRunResult(draft, summary, decision, attempt)

            if decision == ReviewDecision.NEEDS_REVIEW:
                return ChapterRunResult(draft, None, decision, attempt)

        return ChapterRunResult(draft, None, ReviewDecision.NEEDS_REVIEW, self.max_retries)
