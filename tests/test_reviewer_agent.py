import pytest

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.domain.models import SceneReview


class FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.structured_calls = 0
        self.schema = None
        self.thinking_level = None
        self.max_output_tokens = None

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        return self.response

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SceneReview],
        thinking_level: str = "medium",
        max_output_tokens: int | None = None,
    ) -> SceneReview:
        del system_prompt, user_prompt
        self.structured_calls += 1
        self.schema = schema
        self.thinking_level = thinking_level
        self.max_output_tokens = max_output_tokens
        return schema.model_validate_json(self.response)


def test_reviewer_uses_typed_structured_output() -> None:
    llm = FakeLLM('{"score": 9, "approved": true, "issues": [], "suggestions": []}')
    result = ReviewerAgent(llm).review(context="Context", draft="Draft")

    assert result == SceneReview(score=9, approved=True, issues=[], suggestions=[])
    assert llm.structured_calls == 1
    assert llm.schema is SceneReview
    assert llm.thinking_level == "medium"
    assert llm.max_output_tokens == 2048


def test_reviewer_accepts_fractional_score() -> None:
    llm = FakeLLM('{"score": 8.5, "approved": true, "issues": [], "suggestions": []}')
    result = ReviewerAgent(llm).review(context="Context", draft="Draft")
    assert result.score == pytest.approx(8.5)


def test_reviewer_rejects_invalid_structured_output() -> None:
    llm = FakeLLM("not json")
    with pytest.raises(ValueError, match="invalid structured output"):
        ReviewerAgent(llm).review(context="Context", draft="Draft")
