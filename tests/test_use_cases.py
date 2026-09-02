import pytest

from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.application.use_cases.update_outline import UpdateOutline
from book_loop.domain.models import BookState, Outline


class Repository:
    def __init__(self):
        self.books = {}

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]


class OutlineAgent:
    def generate(self, **kwargs):
        return Outline(
            chapters=[
                {"number": 1, "title": "The beginning", "objective": "Start the conflict", "synopsis": "An inciting event."},
                {"number": 2, "title": "The conflict", "objective": "Escalate the conflict", "synopsis": "The stakes rise."},
            ]
        )


def test_use_cases_compose_without_services():
    repository = Repository()
    book = CreateBook(repository).execute(title="Book", theme="Fantasy", author_idea="Idea")
    GenerateOutline(repository, OutlineAgent()).execute(book)
    ApproveOutline(repository).execute(book)
    AddChapter(repository).execute(book, chapter_number=1)

    assert book.outline_approved is True
    assert book.chapters[0].number == 1
    assert book.chapters[0].title == "The beginning"
    assert book.chapters[0].objective == "Start the conflict"


def test_structured_outline_round_trips_through_repository():
    repository = Repository()
    book = CreateBook(repository).execute(title="Book", theme="Fantasy", author_idea="Idea")
    outline = Outline(chapters=[{"number": 1, "title": "Opening", "objective": "Introduce the hero"}])
    UpdateOutline(repository).execute(book, outline=outline)

    loaded = repository.get(book.id)
    assert loaded.outline == outline


def test_update_outline_invalidates_previous_approval():
    repository = Repository()
    book = CreateBook(repository).execute(title="Book", theme="Fantasy", author_idea="Idea")
    GenerateOutline(repository, OutlineAgent()).execute(book)
    ApproveOutline(repository).execute(book)

    updated_outline = Outline(
        chapters=[{"number": 1, "title": "Rewritten", "objective": "Change the opening"}]
    )
    updated = UpdateOutline(repository).execute(book, outline=updated_outline)

    assert updated.outline == updated_outline
    assert updated.outline_approved is False
    assert repository.get(book.id).outline_approved is False


def test_add_chapter_rejects_unknown_or_duplicate_outline_chapter():
    repository = Repository()
    book = CreateBook(repository).execute(title="Book", theme="Fantasy", author_idea="Idea")
    GenerateOutline(repository, OutlineAgent()).execute(book)
    ApproveOutline(repository).execute(book)

    with pytest.raises(ValueError, match="Unknown chapter"):
        AddChapter(repository).execute(book, chapter_number=3)

    AddChapter(repository).execute(book, chapter_number=1)
    with pytest.raises(ValueError, match="already exists"):
        AddChapter(repository).execute(book, chapter_number=1)


def test_update_outline_rejects_empty_outline():
    repository = Repository()
    book = BookState(id="1", title="T", theme="Th", author_idea="I")

    with pytest.raises(ValueError, match="cannot be empty"):
        UpdateOutline(repository).execute(book, outline=Outline.model_construct(chapters=[]))
