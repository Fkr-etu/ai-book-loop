import os

from book_loop.domain.models import BookState, Outline, SceneReview
from book_loop.infrastructure.database.postgres import PostgresBookRepository


DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")


def repository() -> PostgresBookRepository:
    return PostgresBookRepository(DATABASE_URL)


def test_book_round_trip() -> None:
    repo = repository()
    book = BookState(id="book-1", title="Test", theme="Fantasy", author_idea="A test idea")
    repo.save(book)
    assert repo.get("book-1") == book


def test_structured_outline_round_trip() -> None:
    repo = repository()
    book = BookState(
        id="book-1",
        title="Test",
        theme="Fantasy",
        author_idea="A test idea",
        outline=Outline(
            chapters=[
                {"number": 1, "title": "Opening", "objective": "Introduce the hero", "synopsis": "An inciting event."},
                {"number": 2, "title": "Crossing", "objective": "Raise the stakes"},
            ]
        ),
    )
    repo.save(book)
    loaded = repo.get("book-1")
    assert loaded.outline == book.outline
    assert loaded.outline.chapters[0].synopsis == "An inciting event."


def test_chapter_version_and_review_are_persisted() -> None:
    repo = repository()
    review = SceneReview(score=8, approved=True, issues=["minor"], suggestions=["keep"])
    repo.save_chapter_version("book-1", 1, 2, "Draft v2")
    repo.save_review("book-1", 1, 2, review)
    version = repo._connection.execute("SELECT draft FROM chapter_versions WHERE book_id=? AND chapter_number=? AND version=?", ("book-1", 1, 2)).fetchone()
    saved_review = repo._connection.execute("SELECT score, approved, issues, suggestions FROM reviews WHERE book_id=? AND chapter_number=? AND version=?", ("book-1", 1, 2)).fetchone()
    assert version["draft"] == "Draft v2"
    assert saved_review["score"] == 8
    assert saved_review["approved"] is True
