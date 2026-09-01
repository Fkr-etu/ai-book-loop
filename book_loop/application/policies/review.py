from __future__ import annotations

from enum import StrEnum

from book_loop.domain.models import SceneReview


class ReviewDecision(StrEnum):
    ACCEPT = "accept"
    RETRY = "retry"
    NEEDS_REVIEW = "needs_review"


def decide(review: SceneReview, *, attempt: int, max_retries: int, threshold: int) -> ReviewDecision:
    if review.score >= threshold and review.approved:
        return ReviewDecision.ACCEPT
    if attempt < max_retries:
        return ReviewDecision.RETRY
    return ReviewDecision.NEEDS_REVIEW
