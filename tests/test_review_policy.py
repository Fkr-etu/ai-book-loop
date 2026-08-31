from book_loop.application.policies.review import ReviewDecision, decide
from book_loop.domain.models import SceneReview


def test_good_review_is_accepted() -> None:
    review = SceneReview(score=8, approved=True)
    assert decide(review, attempt=1, max_retries=3, threshold=7) == ReviewDecision.ACCEPT


def test_failed_review_retries() -> None:
    review = SceneReview(score=5, approved=False)
    assert decide(review, attempt=1, max_retries=3, threshold=7) == ReviewDecision.RETRY


def test_exhausted_review_needs_human_review() -> None:
    review = SceneReview(score=5, approved=False)
    assert decide(review, attempt=3, max_retries=3, threshold=7) == ReviewDecision.NEEDS_REVIEW
