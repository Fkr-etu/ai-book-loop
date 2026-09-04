from book_loop.agents.corrector import CorrectorAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linguistic_validation import LinguisticValidationService
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import (
    BookState,
    Chapter,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckResult,
    LinguisticCheckStatus,
    Outline,
)
from book_loop.workflow.chapter_graph import ChapterWorkflow


class SequenceLLM:
    def __init__(self, review_json: str):
        self.review_json = review_json
        self.correct_calls = 0
        self.review_calls = 0

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        prompt = system_prompt.casefold()
        if "editor" in prompt:
            self.correct_calls += 1
            return f"Corrected draft {self.correct_calls}."
        if "summar" in prompt:
            return "Final summary."
        return "Initial draft."

    def generate_structured(self, *, system_prompt, user_prompt, schema, thinking_level="medium", max_output_tokens=None):
        del system_prompt, user_prompt, thinking_level, max_output_tokens
        self.review_calls += 1
        return schema.model_validate_json(self.review_json)


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

    def get_chapter_version(self, book_id, chapter_number, version):
        for item in reversed(self.versions):
            if item[:3] == (book_id, chapter_number, version):
                return item[3]
        raise KeyError((book_id, chapter_number, version))

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


def test_blocking_linguistic_error_enters_correction_loop_before_reviewer():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM('{"score": 9, "approved": true, "issues": [], "suggestions": []}')
    blocking = Diagnostic(
        category=DiagnosticCategory.AGREEMENT,
        severity=DiagnosticSeverity.ERROR,
        source=DiagnosticSource.NLP,
        message="Possible agreement error",
        confidence=0.93,
        suggestions=["Corriger l'accord"],
    )
    clean = LinguisticCheckResult(
        status=LinguisticCheckStatus.NO_ISSUES_FOUND,
        checker="test",
    )

    class SequenceChecker:
        def __init__(self):
            self.results = iter([
                LinguisticCheckResult(
                    status=LinguisticCheckStatus.ISSUES_FOUND,
                    checker="test",
                    diagnostics=[blocking],
                ),
                clean,
            ])

        def check(self, text, *, language="fr"):
            return next(self.results)

    validator = LinguisticValidationService([SequenceChecker()])
    workflow = ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        corrector=CorrectorAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        linguistic_validator_factory=lambda _book: validator,
    )

    result = workflow.run(book=book, chapter_number=1)

    assert result.decision == "accept"
    assert result.attempt == 2
    assert llm.correct_calls == 1
    assert llm.review_calls == 1
    assert repository.reviews[0][3].issues == ["Possible agreement error"]


def test_linguistic_checker_unavailable_is_fail_closed_when_enabled():
    book = make_book()
    repository = Repository(book)
    llm = SequenceLLM('{"score": 9, "approved": true, "issues": [], "suggestions": []}')
    unavailable = LinguisticValidationService([])

    class FailingChecker:
        def check(self, text, *, language="fr"):
            raise RuntimeError("checker offline")

    unavailable = LinguisticValidationService([FailingChecker()])
    workflow = ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        corrector=CorrectorAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        linguistic_validator_factory=lambda _book: unavailable,
        max_retries=1,
    )

    result = workflow.run(book=book, chapter_number=1)

    assert result.decision == "needs_review"
    assert llm.review_calls == 0
    assert "Linguistic validation unavailable" in repository.reviews[0][3].issues[0]
