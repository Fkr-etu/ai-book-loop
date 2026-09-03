from book_loop.agents.corrector import CorrectorAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, Chapter, Outline, SceneReview
from book_loop.workflow.chapter_graph import ChapterWorkflow


class SequenceLLM:
    def __init__(self, reviews):
        self.reviews = iter(reviews)
        self.correct_calls = 0

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        prompt = system_prompt.casefold()
        if "review" in prompt:
            return next(self.reviews)
        if "summar" in prompt:
            return "Final summary."
        if "editor" in prompt:
            self.correct_calls += 1
            return f"Corrected draft {self.correct_calls}."
        return "Initial draft."

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SceneReview],
        thinking_level: str = "medium",
        max_output_tokens: int | None = None,
    ) -> SceneReview:
        del system_prompt, user_prompt, thinking_level, max_output_tokens
        return schema.model_validate_json(next(self.reviews))


class Repository:
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


def make_book():
    return BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        outline=Outline(chapters=[{"number": 1, "title": "Beginning", "objective": "Start"}]),
        outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="Beginning", objective="Start")],
    )


def make_workflow(book, repository, llm, *, max_retries=3):
    return ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        corrector=CorrectorAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        max_retries=max_retries,
    )


def test_approval_on_first_review_does_not_correct():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM(['{"score": 9, "approved": true, "issues": [], "suggestions": []}'])

    result = make_workflow(book, repository, llm).run(book=book, chapter_number=1)

    assert result.decision == "accept"
    assert result.attempt == 1
    assert result.draft == "Initial draft."
    assert llm.correct_calls == 0
    assert [item[2] for item in repository.versions] == [1]
    assert [item[2] for item in repository.reviews] == [1]


def test_rejection_is_corrected_and_re_reviewed():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM([
        '{"score": 5, "approved": false, "issues": ["Weak opening"], "suggestions": ["Strengthen the opening"]}',
        '{"score": 9, "approved": true, "issues": [], "suggestions": []}',
    ])

    result = make_workflow(book, repository, llm).run(book=book, chapter_number=1)

    assert result.decision == "accept"
    assert result.attempt == 2
    assert result.draft == "Corrected draft 1."
    assert llm.correct_calls == 1
    assert [item[2] for item in repository.versions] == [1, 2]
    assert [item[3].score for item in repository.reviews] == [5, 9]


def test_max_retries_stops_without_infinite_loop():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM([
        '{"score": 4, "approved": false, "issues": ["Issue 1"], "suggestions": []}',
        '{"score": 4, "approved": false, "issues": ["Issue 2"], "suggestions": []}',
    ])

    result = make_workflow(book, repository, llm, max_retries=2).run(book=book, chapter_number=1)

    assert result.decision == "needs_review"
    assert result.attempt == 2
    assert result.summary is None
    assert len(repository.versions) == 2
    assert len(repository.reviews) == 2
    assert llm.correct_calls == 1


def test_invalid_max_retries_is_rejected():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM([])

    try:
        make_workflow(book, repository, llm, max_retries=0)
        assert False, "Expected validation error"
    except ValueError as exc:
        assert "max_retries" in str(exc)


def test_lint_failure_is_persisted_as_review():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM([
        '{"score": 9, "approved": true, "issues": [], "suggestions": []}',
    ])

    class EmptyWriter:
        def write(self, *, context):
            return "TODO"

    workflow = ChapterWorkflow(
        repository=repository,
        writer=EmptyWriter(),
        reviewer=ReviewerAgent(llm),
        corrector=CorrectorAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        max_retries=1,
    )

    result = workflow.run(book=book, chapter_number=1)

    assert result.decision == "needs_review"
    assert len(repository.reviews) == 1
    assert repository.reviews[0][3] == SceneReview(
        score=0,
        approved=False,
        issues=["Draft contains placeholders"],
        suggestions=["Remove all lint errors before the next review."],
    )
