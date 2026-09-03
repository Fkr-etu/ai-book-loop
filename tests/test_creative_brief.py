import pytest

from book_loop.application.services.context import ContextBuilder
from book_loop.application.use_cases.set_creative_brief import SetCreativeBrief
from book_loop.domain.models import BookState, Chapter, CreativeBrief


class Repository:
    def __init__(self, book):
        self.book = book
        self.save_calls = 0

    def save(self, book):
        self.book = book
        self.save_calls += 1

    def get(self, book_id):
        return self.book


def make_book():
    return BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        chapters=[Chapter(id="c1", number=1, title="Beginning", objective="Start")],
    )


def test_creative_brief_requires_premise():
    with pytest.raises(ValueError):
        CreativeBrief(premise="")


def test_set_creative_brief_persists_without_llm():
    book = make_book()
    repository = Repository(book)
    brief = CreativeBrief(
        premise="A cartographer discovers a hidden city.",
        audience="Adult fantasy readers",
        tone="Wonder and tension",
        themes=["identity", "discovery"],
        must_include=["a living map"],
        must_avoid=["gratuitous violence"],
    )

    result = SetCreativeBrief(repository).execute(book, brief)

    assert result.creative_brief == brief
    assert repository.book.creative_brief == brief
    assert repository.save_calls == 1


def test_context_includes_structured_creative_brief():
    book = make_book()
    book.creative_brief = CreativeBrief(
        premise="A cartographer discovers a hidden city.",
        audience="Adult readers",
        tone="Wonder",
        themes=["identity", "discovery"],
        must_include=["a living map"],
        must_avoid=["gratuitous violence"],
    )

    context = ContextBuilder().for_chapter(book, 1)

    assert "CREATIVE BRIEF:" in context
    assert "Premise: A cartographer discovers a hidden city." in context
    assert "Audience: Adult readers" in context
    assert "Themes: identity, discovery" in context
    assert "Must include: a living map" in context
    assert "Must avoid: gratuitous violence" in context


def test_context_handles_missing_creative_brief():
    context = ContextBuilder().for_chapter(make_book(), 1)

    assert "No structured creative brief provided." in context
