from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, Chapter
from book_loop.workflow.chapter import ChapterWorkflow


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if "Review" in system_prompt:
            return '{"score": 9, "approved": true, "issues": [], "suggestions": []}'
        if "canonical continuity" in system_prompt.lower():
            return "Canonical summary."
        return "A valid chapter draft."


def make_workflow(llm: FakeLLM) -> ChapterWorkflow:
    return ChapterWorkflow(
        repository=FakeRepository(),
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        max_retries=3,
        review_threshold=7,
    )


class FakeRepository:
    def __init__(self):
        self.books = {}

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]

    def save_chapter_version(self, book_id, chapter_number, version, draft):
        return None

    def save_review(self, book_id, chapter_number, version, review):
        return None


def test_workflow_requires_approved_outline() -> None:
    book = BookState(id="b", title="B", theme="T", author_idea="I", outline="Outline", outline_approved=False,
                     chapters=[Chapter(id="c", number=1, title="One", objective="Start")])
    llm = FakeLLM()
    workflow = make_workflow(llm)
    try:
        workflow.run(book=book, chapter_number=1)
        assert False, "expected approval gate"
    except ValueError as exc:
        assert "approve the outline" in str(exc)


def test_workflow_generates_reviews_and_summary() -> None:
    book = BookState(id="b", title="B", theme="T", author_idea="I", outline="Outline", outline_approved=True,
                     chapters=[Chapter(id="c", number=1, title="One", objective="Start")])
    repository = FakeRepository()
    repository.save(book)
    llm = FakeLLM()
    workflow = ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        max_retries=3,
        review_threshold=7,
    )
    result = workflow.run(book=book, chapter_number=1)
    assert result.decision.value == "accept"
    assert result.summary == "Canonical summary."
    assert result.attempts == 1
