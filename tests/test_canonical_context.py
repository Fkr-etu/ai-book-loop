from book_loop.application.services.context import ContextBuilder
from book_loop.domain.models import BookState, CanonicalFact, Chapter


class FakeKnowledgeRepository:
    def __init__(self, facts):
        self.facts = facts

    def list_active_canonical_facts(self, *, book_id):
        return self.facts


def test_context_includes_active_canonical_knowledge():
    book = BookState(
        id="book-1", author_idea="idea", theme="theme", lore="lore",
        constraints=[], outline_approved=True,
        chapters=[Chapter(number=1, title="First", objective="Write it")],
    )
    facts = [CanonicalFact(
        id="fact-1", book_id="book-1", assertion_id="assertion-1",
        statement="Alice is 32 years old", subject="Alice", predicate="age",
        object="32", decision_id="decision-1", version=1,
    )]
    context = ContextBuilder(FakeKnowledgeRepository(facts)).for_chapter(book, 1)
    assert "CANONICAL KNOWLEDGE:" in context
    assert "Alice is 32 years old" in context
    assert "fact_id=fact-1" in context
