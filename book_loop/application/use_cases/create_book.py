from __future__ import annotations

from uuid import uuid4

from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


class CreateBook:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        title: str,
        theme: str,
        author_idea: str,
        lore: str = "",
        constraints: list[str] | None = None,
    ) -> BookState:
        book = BookState(
            id=str(uuid4()),
            title=title,
            theme=theme,
            author_idea=author_idea,
            lore=lore,
            constraints=constraints or [],
        )
        self.repository.save(book)
        return book
