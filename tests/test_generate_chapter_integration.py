import json

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.domain.models import BookState, Chapter, ChapterStatus, Outline
from book_loop.workflow.chapter_graph import ChapterWorkflow, ChapterWorkflowState


class RecordingLLM:
    def __init__(
        self,
        drafts: list[str] | None = None,
        review_scores: list[int] | None = None,
    ) -> None:
        self.drafts = iter(drafts or ["A complete chapter draft."])
        self.review_scores = iter(review_scores or [9])
        self.writer_contexts: list[str] = []
        self.calls: list[tuple[str, str]] = []

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        prompt = system_prompt.lower()
        if prompt.startswith("you are the book's writer"):
            self.writer_contexts.append(user_prompt)
            return next(self.drafts)
        if "review" in prompt:
            score = next(self.review_scores)
            return json.dumps(
                {
                    "score": score,
                    "approved": score >= 7,
                    "issues": [],
                    "suggestions": [],
                }
            )
        if "summarize" in prompt:
            return "Canonical chapter summary."
        raise AssertionError(f"Unexpected system prompt: {system_prompt}")


class InMemoryRepository:
    def __init__(self, book: BookState) -> None:
        self.books = {book.id: book}
        self.versions: list[tuple[str, int, int, str]] = []
        self.reviews = []

    def save(self, book: BookState) -> None:
        self.books[book.id] = book

    def get(self, book_id: str) -> BookState:
        return self.books[book_id]

    def save_chapter_version(
        self, book_id: str, chapter_number: int, version: int, draft: str
    ) -> None:
        self.versions.append((book_id, chapter_number, version, draft))

    def save_review(self, book_id: str, chapter_number: int, version: int, review) -> None:
        self.reviews.append((book_id, chapter_number, version, review))


def make_workflow(
    book: BookState, repository: InMemoryRepository, llm: RecordingLLM
) -> ChapterWorkflow:
    return ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
    )


def make_outline(*chapters: tuple[int, str, str]) -> Outline:
    return Outline(
        chapters=[
            {"number": number, "title": title, "objective": objective}
            for number, title, objective in chapters
        ]
    )


def test_generate_chapter_passes_canonical_context_through_real_workflow() -> None:
    book = BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="A hidden heir returns home.",
        lore="The old kingdom forbids magic.",
        outline=make_outline(
            (1, "Return", "Introduce the protagonist's return."),
            (2, "The secret", "Reveal the first clue about the forbidden magic."),
        ),
        outline_approved=True,
        chapters=[
            Chapter(
                id="c1",
                number=1,
                title="Return",
                objective="Introduce the protagonist's return.",
                status=ChapterStatus.APPROVED,
                summary="The protagonist returns to the capital and hides their identity.",
                current_version=1,
            ),
            Chapter(
                id="c2",
                number=2,
                title="The secret",
                objective="Reveal the first clue about the forbidden magic.",
            ),
        ],
    )
    repository = InMemoryRepository(book)
    llm = RecordingLLM()
    use_case = GenerateChapter(make_workflow(book, repository, llm))

    result = use_case.execute(book, chapter_number=2)

    assert isinstance(result, ChapterWorkflowState)
    assert result.decision == "accept"
    assert result.summary == "Canonical chapter summary."
    assert result.attempt == 1
    assert len(llm.writer_contexts) == 1
    context = llm.writer_contexts[0]
    assert "The protagonist returns to the capital and hides their identity." in context
    assert "The old kingdom forbids magic." in context
    assert "Chapter 2: The secret" in context
    assert "Reveal the first clue about the forbidden magic." in context
    assert len(repository.versions) == 1
    assert len(repository.reviews) == 1
    assert repository.get("b1").chapters[1].status == ChapterStatus.APPROVED
    assert repository.get("b1").chapters[1].current_version == 1
    assert repository.get("b1").chapters[1].summary == "Canonical chapter summary."


def test_generate_chapter_retries_after_linter_failure_and_preserves_history() -> None:
    book = BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        outline=make_outline((1, "One", "Start")),
        outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="One", objective="Start")],
    )
    repository = InMemoryRepository(book)
    llm = RecordingLLM(drafts=["TODO: unfinished draft", "A corrected chapter draft."])
    use_case = GenerateChapter(make_workflow(book, repository, llm))

    result = use_case.execute(book, chapter_number=1)

    assert result.decision == "accept"
    assert result.attempt == 2
    assert [version[2] for version in repository.versions] == [1, 2]
    assert [version[3] for version in repository.versions] == [
        "TODO: unfinished draft",
        "A corrected chapter draft.",
    ]
    assert len(repository.reviews) == 1
    assert repository.reviews[0][2] == 2


def test_generate_chapter_retries_after_low_review_and_preserves_reviews() -> None:
    book = BookState(
        id="b1",
        title="Book",
        theme="Fantasy",
        author_idea="Idea",
        outline=make_outline((1, "One", "Start")),
        outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="One", objective="Start")],
    )
    repository = InMemoryRepository(book)
    llm = RecordingLLM(
        drafts=["First draft.", "Improved draft."],
        review_scores=[5, 9],
    )
    use_case = GenerateChapter(make_workflow(book, repository, llm))

    result = use_case.execute(book, chapter_number=1)

    assert result.decision == "accept"
    assert result.attempt == 2
    assert len(repository.versions) == 2
    assert [review[2] for review in repository.reviews] == [1, 2]
    assert [review[3].score for review in repository.reviews] == [5, 9]
    assert result.summary == "Canonical chapter summary."
