from __future__ import annotations

from book_loop.domain.models import BookState
from book_loop.workflow.chapter_graph import ChapterWorkflow, ChapterWorkflowState


class GenerateChapter:
    def __init__(self, workflow: ChapterWorkflow) -> None:
        self.workflow = workflow

    def execute(self, book: BookState, *, chapter_number: int) -> ChapterWorkflowState:
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before generating chapters")
        if not any(chapter.number == chapter_number for chapter in book.chapters):
            raise ValueError(f"Unknown chapter: {chapter_number}")
        return self.workflow.run(book=book, chapter_number=chapter_number)
