from book_loop.application.services.context import CanonicalContext, ContextBuilder
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

    assert isinstance(context, CanonicalContext)
    assert context.author_idea == "A hidden heir discovers the truth."
    assert context.lore == "The kingdom forbids magic."
    assert context.constraints == ("First person",)
    assert len(context.previous_summaries) == 1
    summary = context.previous_summaries[0]
    assert summary.chapter_number == 1
    assert summary.title == "Discovery"
    assert summary.summary == "The heir learns the truth."
    assert context.chapter_objective == "Face the ruler"
    rendered = context.render()
    assert "A hidden heir discovers the truth." in rendered
    assert "The heir learns the truth." in rendered


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

    assert len(context.previous_summaries) == 1
    assert context.previous_summaries[0].chapter_number == 1
