from __future__ import annotations

from uuid import uuid4

from book_loop.application.services.plan_limits import limits_for
from book_loop.domain.models import BookState, CreativeBrief, GrillPersonality, SubscriptionPlan
from book_loop.domain.protocols import BookRepository


class CreateBook:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        owner_id: str,
        title: str,
        theme: str,
        author_idea: str,
        lore: str = "",
        constraints: list[str] | None = None,
        creative_brief: CreativeBrief | None = None,
        grill_personality: GrillPersonality = GrillPersonality.CHALLENGER,
    ) -> BookState:
        book = BookState(
            id=str(uuid4()),
            owner_id=owner_id,
            title=title,
            theme=theme,
            author_idea=author_idea,
            creative_brief=creative_brief,
            lore=lore,
            constraints=constraints or [],
            grill_personality=grill_personality,
        )
        save_with_capacity = getattr(self.repository, "save_new_book_with_capacity", None)
        if save_with_capacity is not None:
            user = getattr(self.repository, "get_user_by_id")(owner_id)
            if user is None:
                raise PermissionError("Unknown owner")
            save_with_capacity(book, limits_for(SubscriptionPlan(user.plan)).max_active_projects)
        else:
            self.repository.save(book)
        return book
