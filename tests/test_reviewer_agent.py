import pytest

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.domain.models import SceneReview


class FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        return self.response


def test_reviewer_accepts_plain_json() -> None:
    agent = ReviewerAgent(
        FakeLLM('{"score": 9, "approved": true, "issues": [], "suggestions": []}')
    )
    result = agent.review(context="Context", draft="Draft")
    assert result == SceneReview(score=9, approved=True, issues=[], suggestions=[])


def test_reviewer_accepts_fenced_json() -> None:
    agent = ReviewerAgent(
        FakeLLM(
            '```json\n{"score": 8, "approved": true, "issues": [], "suggestions": ["Keep the pace"]}\n```'
        )
    )
    result = agent.review(context="Context", draft="Draft")
    assert result == SceneReview(
        score=8, approved=True, issues=[], suggestions=["Keep the pace"]
    )


def test_reviewer_rejects_invalid_json() -> None:
    agent = ReviewerAgent(FakeLLM("not json"))
    with pytest.raises(ValueError, match="invalid structured output"):
        agent.review(context="Context", draft="Draft")
