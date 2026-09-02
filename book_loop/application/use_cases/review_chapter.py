from __future__ import annotations

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.application.policies.review import ReviewDecision, decide
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, ChapterStatus, SceneReview
from book_loop.domain.protocols import BookRepository


class ReviewChapter:
    def __init__(
        self,
        repository: BookRepository,
        reviewer: ReviewerAgent,
        context_builder: ContextBuilder,
        linter: ChapterLinter,
        max_retries: int = 3,
        threshold: int = 7,
    ) -> None:
        self.repository = repository
        self.reviewer = reviewer
        self.context_builder = context_builder
        self.linter = linter
        self.max_retries = max_retries
        self.threshold = threshold

    def execute(
        self,
        book: BookState,
        chapter_number: int,
        version_number: int | None = None,
        draft_text: str | None = None,
    ) -> tuple[BookState, SceneReview]:
        chapter = next(
            (c for c in book.chapters if c.number == chapter_number), None
        )
        if chapter is None:
            raise ValueError(f"Chapter {chapter_number} not found")

        version = version_number or chapter.current_version
        text = (
            draft_text
            or f"Contenu du chapitre {chapter.number} version {version}"
        )

        lint_result = self.linter.lint(text)
        context = self.context_builder.for_chapter(book, chapter_number)

        if not lint_result.valid:
            issues = lint_result.issues
            approved = False
            score = 0
            review = SceneReview(
                score=score,
                approved=approved,
                issues=issues,
                suggestions=["Réécrire sans termes anachroniques ou invalides."],
            )
        else:
            review = self.reviewer.review(context=context, draft=text)

        self.repository.save_review(
            book_id=book.id,
            chapter_number=chapter.number,
            version=version,
            review=review,
        )

        decision = decide(
            review,
            attempt=version,
            max_retries=self.max_retries,
            threshold=self.threshold,
        )

        if decision == ReviewDecision.ACCEPT:
            chapter.status = ChapterStatus.NEEDS_REVIEW
        else:
            chapter.status = ChapterStatus.REJECTED

        self.repository.save(book)
        return book, review
