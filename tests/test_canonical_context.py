from book_loop.application.services.context import ContextBuilder
from book_loop.domain.models import BookState, CanonicalFact, Chapter


class FakeKnowledgeRepository:
    def __init__(self, facts):
        self.facts = facts

    def list_active_canonical_facts(self, *, book_id):
        return self.facts


class SelectingRetriever:
    def __init__(self, selected):
        self.selected = selected
        self.queries = []

    def retrieve(self, facts, *, query):
        self.queries.append((list(facts), query))
        return self.selected


def make_book():
    return BookState(
        id="book-1",
        title="Test Book",
        author_idea="idea",
        theme="theme",
        lore="lore",
        constraints=[],
        outline_approved=True,
        chapters=[
            Chapter(
                id="chapter-1",
                number=1,
                title="Alice's age",
                objective="Write about Alice's age",
            )
        ],
    )


def make_fact(fact_id="fact-1", statement="Alice is 32 years old"):
    return CanonicalFact(
        id=fact_id,
        book_id="book-1",
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject="Alice",
        predicate="age",
        object="32",
        decision_id=f"decision-{fact_id}",
        version=1,
    )


def test_context_includes_active_canonical_knowledge():
    facts = [make_fact()]
    context = ContextBuilder(FakeKnowledgeRepository(facts)).for_chapter(make_book(), 1)

    assert "CANONICAL KNOWLEDGE:" in context
    assert "Alice is 32 years old" in context
    assert "fact_id=fact-1" in context


def test_context_accepts_a_custom_retrieval_strategy():
    available = [make_fact()]
    selected = [make_fact("fact-selected", "Alice carries a silver key")]
    retriever = SelectingRetriever(selected)

    context = ContextBuilder(
        FakeKnowledgeRepository(available),
        retriever=retriever,
    ).for_chapter(make_book(), 1)

    assert "Alice carries a silver key" in context
    assert "Alice is 32 years old" not in context
    assert len(retriever.queries) == 1
    queried_facts, query = retriever.queries[0]
    assert queried_facts == available
    assert "Alice's age" in query
    assert "Write about Alice's age" in query
