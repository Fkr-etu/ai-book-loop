from __future__ import annotations

from book_loop.domain.models import BookState, Chapter
from book_loop.domain.protocols import BookRepository
from book_loop.workflow.chapter_graph import ChapterWorkflow


class ChapterService:
    def __init__(self, repository: BookRepository, workflow: ChapterWorkflow) -> None:
        self.repository = repository
        self.workflow = workflow

    def add_chapter(self, book: BookState, *, number: int, title: str, objective: str) -> BookState:
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before adding chapters")
        if any(chapter.number == number for chapter in book.chapters):
            raise ValueError(f"Chapter {number} already exists")
        if number != len(book.chapters) + 1:
            raise ValueError("Chapters must be created sequentially")
        book.chapters.append(Chapter(id=f"{book.id}:chapter:{number}", number=number, title=title, objective=objective))
        self.repository.save(book)
        return book

    def generate(self, book: BookState, *, chapter_number: int):
        if chapter_number < 1 or chapter_number > len(book.chapters):
            raise ValueError(f"Unknown chapter: {chapter_number}")
        return self.workflow.run(book=book, chapter_number=chapter_number)
