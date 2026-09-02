from book_loop.domain.models import BookState, Outline, SceneReview
from book_loop.infrastructure.database.repository import SQLiteBookRepository


def test_book_round_trip(tmp_path) -> None:
    repository = SQLiteBookRepository(f"sqlite:///{tmp_path / 'book.db'}")
    book = BookState(id="book-1", title="Test", theme="Fantasy", author_idea="A test idea")

    repository.save(book)

    assert repository.get("book-1") == book


def test_structured_outline_round_trip(tmp_path) -> None:
    repository = SQLiteBookRepository(f"sqlite:///{tmp_path / 'book.db'}")
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

    repository.save(book)

    loaded = repository.get("book-1")
    assert loaded.outline == book.outline
    assert loaded.outline.chapters[0].synopsis == "An inciting event."


def test_chapter_version_and_review_are_persisted(tmp_path) -> None:
    repository = SQLiteBookRepository(f"sqlite:///{tmp_path / 'book.db'}")
    review = SceneReview(score=8, approved=True, issues=["minor"], suggestions=["keep"])

    repository.save_chapter_version("book-1", 1, 2, "Draft v2")
    repository.save_review("book-1", 1, 2, review)

    version = repository._connection.execute(
        "SELECT draft FROM chapter_versions WHERE book_id=? AND chapter_number=? AND version=?",
        ("book-1", 1, 2),
    ).fetchone()
    saved_review = repository._connection.execute(
        "SELECT score, approved, issues, suggestions FROM reviews WHERE book_id=? AND chapter_number=? AND version=?",
        ("book-1", 1, 2),
    ).fetchone()

    assert version[0] == "Draft v2"
    assert saved_review[0] == 8
    assert saved_review[1] == 1
