from __future__ import annotations

from book_loop.domain.models import BookState
from book_loop.workflow.chapter_graph import ChapterWorkflow, ChapterWorkflowState


class GenerateChapter:
    def __init__(self, workflow: ChapterWorkflow) -> None:
        self.workflow = workflow

    def execute(
        self,
        book: BookState,
        chapter_number: int,
        *,
        idempotency_key: str | None = None,
    ) -> ChapterWorkflowState:
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before generating chapters")
        chapter = next(
            (chapter for chapter in book.chapters if chapter.number == chapter_number),
            None,
        )
        if chapter is None:
            raise ValueError(f"Unknown chapter: {chapter_number}")

        previous = next(
            (candidate for candidate in book.chapters if candidate.number == chapter_number - 1),
            None,
        )
        if previous is not None and previous.status.value != "approved" and not previous.summary:
            raise ValueError(
                f"Chapter {chapter_number - 1} must be approved before generating chapter {chapter_number}"
            )

        # The default key represents the next chapter version. Repeating the same
        # request while that version is still in progress therefore resumes it;
        # after completion current_version advances and a later call intentionally
        # creates a new generation run.
        key = idempotency_key or f"chapter:{book.id}:{chapter_number}:v{chapter.current_version + 1}"
        return self.workflow.run(
            book=book,
            chapter_number=chapter_number,
            idempotency_key=key,
        )
