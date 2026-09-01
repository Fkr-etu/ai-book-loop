from book_loop.application.services.context import ContextBuilder
from book_loop.domain.models import BookState, Chapter


def test_context_contains_author_intent_and_canonical_history() -> None:
    book = BookState(
        id="book-1",
        title="The Book",
        theme="identity",
        author_idea="A hidden heir discovers the truth.",
        lore="The kingdom forbids magic.",
        constraints=["First person"],
        outline="Chapter 1: discovery\nChapter 2: confrontation",
        outline_approved=True,
        chapters=[
            Chapter(id="c1", number=1, title="Discovery", objective="Discover the secret", summary="The heir learns the truth."),
            Chapter(id="c2", number=2, title="Confrontation", objective="Face the ruler"),
        ],
    )

    context = ContextBuilder().for_chapter(book, 2)

    assert "A hidden heir discovers the truth." in context
    assert "The kingdom forbids magic." in context
    assert "First person" in context
    assert "The heir learns the truth." in context
    assert "Face the ruler" in context


def test_context_excludes_current_and_future_chapter_summaries() -> None:
    book = BookState(
        id="book-1", title="The Book", theme="theme", author_idea="idea",
        outline="outline", outline_approved=True,
        chapters=[
            Chapter(id="c1", number=1, title="One", objective="one", summary="Past"),
            Chapter(id="c2", number=2, title="Two", objective="two", summary="Current"),
            Chapter(id="c3", number=3, title="Three", objective="three", summary="Future"),
        ],
    )

    context = ContextBuilder().for_chapter(book, 2)

    assert "Past" in context
    assert "Current" not in context
    assert "Future" not in context
