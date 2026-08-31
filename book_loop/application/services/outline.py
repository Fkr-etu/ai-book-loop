from __future__ import annotations

from book_loop.agents.outline import OutlineAgent
from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


class OutlineService:
    def __init__(self, repository: BookRepository, agent: OutlineAgent) -> None:
        self.repository = repository
        self.agent = agent

    def generate(self, book: BookState) -> BookState:
        book.outline = self.agent.generate(
            theme=book.theme,
            author_idea=book.author_idea,
            lore=book.lore,
            constraints=book.constraints,
        )
        book.outline_approved = False
        self.repository.save(book)
        return book

    def approve(self, book: BookState) -> BookState:
        if not book.outline:
            raise ValueError("Cannot approve an outline that has not been generated")
        book.outline_approved = True
        self.repository.save(book)
        return book
