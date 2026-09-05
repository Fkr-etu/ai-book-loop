from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, Chapter, Outline, SceneReview
from book_loop.infrastructure.database.workflow_store import InMemoryWorkflowRunStore
from book_loop.workflow.chapter_graph import ChapterWorkflow


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
        return schema.model_validate({"score": 8, "approved": True, "issues": [], "suggestions": []})


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
        if any(v[:3] == (book_id, chapter_number, version) for v in self.versions):
            raise ValueError("duplicate chapter version")
        self.versions.append((book_id, chapter_number, version, draft))

    def get_chapter_version(self, book_id, chapter_number, version):
        for stored_book_id, stored_chapter_number, stored_version, draft in reversed(self.versions):
            if (stored_book_id, stored_chapter_number, stored_version) == (book_id, chapter_number, version):
                return draft
        raise KeyError((book_id, chapter_number, version))

    def save_review(self, book_id, chapter_number, version, review):
        self.reviews.append((book_id, chapter_number, version, review))


def make_book():
    return BookState(
        id="recovery-book",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        outline=Outline(chapters=[{"number": 1, "title": "Beginning", "objective": "Start"}]),
        outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="Beginning", objective="Start")],
    )


def make_workflow(book, repository, store):
    llm = FakeLLM()
    workflow = ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        workflow_store=store,
    )
    return workflow, llm


def test_same_idempotency_key_does_not_generate_twice():
    book = make_book()
    repository = InMemoryRepository(book)
    store = InMemoryWorkflowRunStore()
    workflow, llm = make_workflow(book, repository, store)

    first = workflow.run(book=book, chapter_number=1, idempotency_key="request-1")
    calls_after_first = llm.calls
    second = workflow.run(book=book, chapter_number=1, idempotency_key="request-1")

    assert first.summary == second.summary == "Canonical chapter summary."
    assert second.attempt == 1
    assert len(repository.versions) == 1
    assert len(repository.reviews) == 1
    assert llm.calls == calls_after_first


def test_checkpoint_can_be_resumed_by_a_new_workflow_instance():
    book = make_book()
    repository = InMemoryRepository(book)
    store = InMemoryWorkflowRunStore()
    workflow, _ = make_workflow(book, repository, store)

    # Simulate a process stopping after the durable chapter artifact was written.
    run = store.get_or_create(book_id=book.id, chapter_number=1, idempotency_key="request-2")
    run.attempt = 1
    store.save(run)
    repository.save_chapter_version(book.id, 1, 1, "Persisted draft before restart")

    restarted, llm = make_workflow(book, repository, store)
    result = restarted.run(book=book, chapter_number=1, idempotency_key="request-2")

    assert result.draft == "Persisted draft before restart"
    assert result.summary == "Canonical chapter summary."
    assert len(repository.versions) == 1
    assert llm.calls == 2  # reviewer + summarizer; the writer was not called after restart
