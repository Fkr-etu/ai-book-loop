import pytest

from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.domain.models import Chapter, SubscriptionPlan, User
from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.infrastructure.database.workflow_store import InMemoryWorkflowRunStore


class Repository:
    def __init__(self) -> None:
        self.books = {}
        self.users = {
            "user-a": User(id="user-a", email="a@example.com", password_hash="x", plan=SubscriptionPlan.FREE),
            "user-b": User(id="user-b", email="b@example.com", password_hash="x", plan=SubscriptionPlan.FREE),
        }

    def save(self, book) -> None:
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def consume_workflow_capacity(self, *, quota_subject: str, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        return True


class BookUsage:
    def __init__(self) -> None:
        self.identities = {}
        self.identity_users = {}
        self.consumed = set()

    def get_book_identity(self, *, book_id: str) -> str | None:
        return self.identities.get(book_id)

    def consume_free_workflow_capacity(self, *, user_id: str, book_id: str, book_identity: str, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        request_key = (user_id, period_start, idempotency_key)
        if request_key in self.consumed:
            return True
        owner = self.identity_users.get(book_identity)
        if owner is not None and owner != user_id:
            return False
        used = sum(1 for subject, period, _ in self.consumed if subject == user_id and period == period_start)
        if used >= monthly_limit:
            return False
        self.identity_users.setdefault(book_identity, user_id)
        self.identities.setdefault(book_id, book_identity)
        self.consumed.add(request_key)
        return True

    def consume_workflow_capacity(self, *, quota_subject: str, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        key = (quota_subject, period_start, idempotency_key)
        if key in self.consumed:
            return True
        used = sum(1 for subject, period, _ in self.consumed if subject == quota_subject and period == period_start)
        if used >= monthly_limit:
            return False
        self.consumed.add(key)
        return True


class Workflow:
    def start_run(self, *, book_id: str, chapter_number: int, idempotency_key: str):
        return ChapterWorkflowRun(id=f"run-{idempotency_key}", book_id=book_id, chapter_number=chapter_number, idempotency_key=idempotency_key)

    def run(self, **kwargs):
        raise AssertionError("start() must not execute the workflow")


def make_book(repository: Repository, usage: BookUsage, owner_id: str):
    book = CreateBook(repository, usage).execute(
        owner_id=owner_id,
        title="The Same Book",
        theme="Fantasy",
        author_idea="A hidden heir returns home",
        lore="An old kingdom forbids magic",
        constraints=["No anachronisms"],
    )
    book.outline_approved = True
    book.chapters.append(Chapter(id=f"chapter-{book.id}", number=1, title="Opening", objective="Start"))
    return book


def make_use_case(repository: Repository, usage: BookUsage) -> GenerateChapter:
    return GenerateChapter(Workflow(), repository, InMemoryWorkflowRunStore(), usage)


def test_free_capacity_is_not_shared_but_same_book_is_rejected_for_another_account() -> None:
    repository = Repository()
    usage = BookUsage()
    book_a = make_book(repository, usage, "user-a")
    book_b = make_book(repository, usage, "user-b")
    use_case = make_use_case(repository, usage)

    use_case.start(book_a, 1, idempotency_key="attempt-a")

    with pytest.raises(PermissionError, match="already used the free tier"):
        use_case.start(book_b, 1, idempotency_key="attempt-b")

    assert ("user-a", "attempt-a") in {(subject, key) for subject, _, key in usage.consumed}
    assert not any(subject == "user-b" for subject, _, _ in usage.consumed)


def test_same_account_can_retry_the_same_book_until_its_own_quota_is_exhausted() -> None:
    repository = Repository()
    usage = BookUsage()
    book = make_book(repository, usage, "user-a")
    use_case = make_use_case(repository, usage)

    for index in range(5):
        use_case.start(book, 1, idempotency_key=f"attempt-{index}")

    with pytest.raises(PermissionError, match="already used the free tier"):
        use_case.start(book, 1, idempotency_key="attempt-5")


def test_free_capacity_is_idempotent_for_the_same_request_key() -> None:
    repository = Repository()
    usage = BookUsage()
    book = make_book(repository, usage, "user-a")
    use_case = make_use_case(repository, usage)

    use_case.start(book, 1, idempotency_key="same-request")
    use_case.start(book, 1, idempotency_key="same-request")

    assert len(usage.consumed) == 1


def test_free_book_identity_survives_book_edits() -> None:
    repository = Repository()
    usage = BookUsage()
    book_a = make_book(repository, usage, "user-a")
    book_a.title = "A Different Display Title"
    book_b = make_book(repository, usage, "user-b")
    use_case = make_use_case(repository, usage)

    use_case.start(book_a, 1, idempotency_key="attempt-a")

    with pytest.raises(PermissionError, match="already used the free tier"):
        use_case.start(book_b, 1, idempotency_key="attempt-b")
