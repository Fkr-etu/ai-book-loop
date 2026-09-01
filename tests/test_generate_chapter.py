import pytest

from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.domain.models import BookState, Chapter, ChapterStatus


class FakeWorkflow:
    def __init__(self):
        self.calls = []

    def run(self, *, book, chapter_number):
        self.calls.append((book.id, chapter_number))
        return "result"


def make_book(*, previous_status=ChapterStatus.APPROVED):
    return BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        outline="Chapter 1\nChapter 2",
        outline_approved=True,
        chapters=[
            Chapter(
                id="c1",
                number=1,
                title="Beginning",
                objective="Start",
                status=previous_status,
                current_version=1,
                summary="Previous canonical summary",
            ),
            Chapter(id="c2", number=2, title="Middle", objective="Continue"),
        ],
    )


def test_generate_chapter_requires_previous_chapter_to_be_approved():
    workflow = FakeWorkflow()
    use_case = GenerateChapter(workflow)

    with pytest.raises(ValueError, match="Chapter 1 must be approved"):
        use_case.execute(make_book(previous_status=ChapterStatus.DRAFT), chapter_number=2)

    assert workflow.calls == []


def test_generate_first_chapter_without_previous_chapter():
    workflow = FakeWorkflow()
    use_case = GenerateChapter(workflow)
    book = BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        outline="Chapter 1",
        outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="Beginning", objective="Start")],
    )

    assert use_case.execute(book, chapter_number=1) == "result"
    assert workflow.calls == [("b1", 1)]
