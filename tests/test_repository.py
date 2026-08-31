from book_loop.domain.models import BookState
from book_loop.infrastructure.database.repository import SQLiteBookRepository


def test_book_round_trip(tmp_path) -> None:
    repository = SQLiteBookRepository(f"sqlite:///{tmp_path / 'book.db'}")
    book = BookState(id="book-1", title="Test", theme="Fantasy", author_idea="A test idea")

    repository.save(book)

    assert repository.get("book-1") == book
