from book_loop.application.services.context import ContextBuilder
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.domain.models import BookState, Chapter


class FakeWriter:
    def __init__(self) -> None:
        self.context = None

    def write(self, *, context: str) -> str:
        self.context = context
        return "draft"


class FakeWorkflow:
    def __init__(self, writer: FakeWriter) -> None:
        self.writer = writer

    def run(self, *, book: BookState, chapter_number: int):
        context = ContextBuilder().for_chapter(book, chapter_number).render()
        self.writer.write(context=context)
        return None


def test_generate_chapter_passes_previous_canonical_summary_to_writer() -> None:
    writer = FakeWriter()
    book = BookState(
        id="book-1",
        title="The Book",
        theme="identity",
        author_idea="A hidden heir discovers the truth.",
        lore="The kingdom forbids magic.",
        outline="Chapter 1: discovery\nChapter 2: confrontation",
        outline_approved=True,
        chapters=[
            Chapter(id="c1", number=1, title="Discovery", objective="Discover", summary="The heir learns the truth."),
            Chapter(id="c2", number=2, title="Confrontation", objective="Face the ruler"),
        ],
    )

    GenerateChapter(workflow=FakeWorkflow(writer)).execute(book, 2)

    assert writer.context is not None
    assert "The heir learns the truth." in writer.context
    assert "Face the ruler" in writer.context
    assert "A hidden heir discovers the truth." in writer.context
