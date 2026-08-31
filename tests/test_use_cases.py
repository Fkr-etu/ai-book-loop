from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.domain.models import BookState


class Repository:
    def __init__(self):
        self.books = {}

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]


class OutlineAgent:
    def generate(self, **kwargs):
        return "Chapter 1: The beginning"


def test_use_cases_compose_without_services():
    repository = Repository()
    book = CreateBook(repository).execute(title="Book", theme="Fantasy", author_idea="Idea")
    GenerateOutline(repository, OutlineAgent()).execute(book)
    ApproveOutline(repository).execute(book)
    AddChapter(repository).execute(book, title="Beginning", objective="Start the conflict")

    assert book.outline_approved is True
    assert book.chapters[0].number == 1
