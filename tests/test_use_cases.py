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


def test_update_book_use_case():
    from book_loop.application.use_cases.update_book import UpdateBook
    repository = Repository()
    book = CreateBook(repository).execute(title="Book", theme="Fantasy", author_idea="Idea")
    updated = UpdateBook(repository).execute(book.id, {"title": "Updated Title"})
    assert updated.title == "Updated Title"


def test_generate_chapter_exceptions():
    from book_loop.application.use_cases.generate_chapter import GenerateChapter
    from book_loop.domain.models import Chapter, ChapterStatus
    import pytest

    class DummyWorkflow:
        def run(self, book, chapter_number):
            return "OK"

    workflow = DummyWorkflow()
    use_case = GenerateChapter(workflow)

    # 1. Outline not approved
    book = BookState(id="1", title="T", theme="Th", author_idea="I", outline_approved=False)
    with pytest.raises(ValueError, match="approve"):
        use_case.execute(book, 1)

    # 2. Unknown chapter
    book.outline_approved = True
    with pytest.raises(ValueError, match="Unknown chapter"):
        use_case.execute(book, 99)

    # 3. Previous chapter not approved
    chap1 = Chapter(id="c1", number=1, title="C1", objective="O1", status=ChapterStatus.DRAFT)
    chap2 = Chapter(id="c2", number=2, title="C2", objective="O2", status=ChapterStatus.DRAFT)
    book.chapters = [chap1, chap2]
    with pytest.raises(ValueError, match="must be approved"):
        use_case.execute(book, 2)
