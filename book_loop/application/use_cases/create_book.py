from __future__ import annotations

from uuid import uuid4

from book_loop.application.ports.book_usage import BookUsagePort
from book_loop.application.services.book_identity import book_identity
from book_loop.application.services.plan_limits import limits_for
from book_loop.domain.models import BookState, SubscriptionPlan
from book_loop.domain.protocols import BookRepository


class CreateBook:
    def __init__(self, repository: BookRepository, book_usage: BookUsagePort | None = None) -> None:
        self.repository = repository
        self.book_usage = book_usage

    def execute(
        self,
        *,
        owner_id: str,
        title: str,
        theme: str,
        author_idea: str,
        lore: str = "",
        constraints: list[str] | None = None,
    ) -> BookState:
        book = BookState(
            id=str(uuid4()),
            owner_id=owner_id,
            title=title,
            theme=theme,
            author_idea=author_idea,
            lore=lore,
            constraints=constraints or [],
        )
        save_with_capacity = getattr(self.repository, "save_new_book_with_capacity", None)
        if save_with_capacity is not None:
            user = getattr(self.repository, "get_user_by_id")(owner_id)
            if user is None:
                raise PermissionError("Unknown owner")
            save_with_capacity(book, limits_for(SubscriptionPlan(user.plan)).max_active_projects)
        else:
            self.repository.save(book)

        if self.book_usage is not None:
            self.book_usage.register_book_identity(
                book_id=book.id,
                identity=book_identity(
                    title=title,
                    theme=theme,
                    author_idea=author_idea,
                    lore=lore,
                    constraints=constraints,
                ),
            )
        return book
