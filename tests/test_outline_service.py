from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.domain.models import BookState, Outline


class FakeOutlineAgent:
    def generate(self, **kwargs) -> Outline:
        return Outline(
            chapters=[
                {"number": 1, "title": "The Beginning", "objective": "Establish the conflict"}
            ]
        )


class InMemoryRepository:
    def __init__(self):
        self.books = {}

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]


def test_generated_outline_requires_explicit_approval() -> None:
    repository = InMemoryRepository()
    agent = FakeOutlineAgent()
    book = BookState(id="b1", title="Book", theme="Fantasy", author_idea="Idea")

    GenerateOutline(repository, agent).execute(book)
    assert book.outline is not None
    assert book.outline.chapters[0].title == "The Beginning"
    assert book.outline_approved is False

    ApproveOutline(repository).execute(book)
    assert book.outline_approved is True
