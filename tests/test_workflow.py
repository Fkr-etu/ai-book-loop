from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, Chapter, Outline
from book_loop.workflow.chapter_graph import ChapterWorkflow, ChapterWorkflowState
from book_loop.domain.models import SceneReview


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        prompt = system_prompt.casefold()
        if "review" in prompt:
            return '{"score": 8, "approved": true, "issues": [], "suggestions": []}'
        if "summarize" in prompt:
            return "Canonical chapter summary."
        return "A complete chapter draft."

    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema, thinking_level="medium", max_output_tokens=None):
        self.calls += 1
        prompt = system_prompt.casefold()
        if "review" in prompt:
            return schema.model_validate({"score": 8, "approved": True, "issues": [], "suggestions": []})
        raise AssertionError("Unexpected structured generation request")


class InMemoryRepository:
    def __init__(self, book):
        self.books = {book.id: book}
        self.versions = []
        self.reviews = []

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]

    def save_chapter_version(self, book_id, chapter_number, version, draft):
        self.versions.append((book_id, chapter_number, version, draft))

    def save_review(self, book_id, chapter_number, version, review):
        self.reviews.append((book_id, chapter_number, version, review))


def make_workflow(book, repository):
    llm = FakeLLM()
    return ChapterWorkflow(
        repository=repository, writer=WriterAgent(llm), reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm), context_builder=ContextBuilder(),
        linter=ChapterLinter(),
    )


def make_outline() -> Outline:
    return Outline(chapters=[{"number": 1, "title": "Beginning", "objective": "Start"}])


def test_workflow_requires_approved_outline():
    book = BookState(
        id="b1", title="Book", theme="Fantasy", author_idea="Idea",
        outline=make_outline(), outline_approved=False,
        chapters=[Chapter(id="c1", number=1, title="Beginning", objective="Start")],
    )
    repository = InMemoryRepository(book)
    workflow = make_workflow(book, repository)

    try:
        workflow.run(book=book, chapter_number=1)
        assert False, "Expected approval gate"
    except ValueError as exc:
        assert "approve the outline" in str(exc)


def test_workflow_accepts_and_summarizes():
    book = BookState(
        id="b1", title="Book", theme="Fantasy", author_idea="Idea",
        outline=make_outline(), outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="Beginning", objective="Start")],
    )
    repository = InMemoryRepository(book)
    workflow = make_workflow(book, repository)

    result = workflow.run(book=book, chapter_number=1)

    assert isinstance(result, ChapterWorkflowState)
    assert result.decision == "accept"
    assert result.summary == "Canonical chapter summary."
    assert len(repository.versions) == 1
    assert len(repository.reviews) == 1
    assert repository.get("b1").chapters[0].current_version == 1
