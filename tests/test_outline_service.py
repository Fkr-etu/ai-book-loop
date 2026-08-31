from book_loop.application.services.outline import OutlineService
from book_loop.domain.models import BookState


class FakeOutlineAgent:
    def generate(self, **kwargs) -> str:
        return "Chapter 1 — The Beginning\nObjective: establish the conflict."


class InMemoryRepository:
    def __init__(self):
        self.books = {}

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]


def test_generated_outline_requires_explicit_approval() -> None:
    repository = InMemoryRepository()
    service = OutlineService(repository, FakeOutlineAgent())
    book = BookState(id="b1", title="Book", theme="Fantasy", author_idea="Idea")

    service.generate(book)
    assert book.outline
    assert book.outline_approved is False

    service.approve(book)
    assert book.outline_approved is True
