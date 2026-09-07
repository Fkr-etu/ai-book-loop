from book_loop.application.use_cases.consistency_engine import UnifiedConsistencyEngine


class FakeDetector:
    def __init__(self, issues):
        self.issues = issues

    def detect(self, *, book_id: str):
        return self.issues


def test_engine_fuses_detectors_and_deduplicates_stable_ids() -> None:
    first = type("Issue", (), {"id": "issue-1"})()
    duplicate = type("Issue", (), {"id": "issue-1"})()
    second = type("Issue", (), {"id": "issue-2"})()

    engine = UnifiedConsistencyEngine(
        (
            FakeDetector([first, second]),
            FakeDetector([duplicate]),
        )
    )

    result = engine.detect(book_id="book-1")

    assert result == [first, second]


def test_engine_rejects_detector_issue_without_stable_id() -> None:
    engine = UnifiedConsistencyEngine((FakeDetector([object()]),))

    try:
        engine.detect(book_id="book-1")
    except ValueError as exc:
        assert "stable id" in str(exc)
    else:
        raise AssertionError("Expected detector contract validation to fail")
