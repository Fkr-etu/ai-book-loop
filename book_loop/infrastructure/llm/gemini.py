from __future__ import annotations

from book_loop.domain.protocols import LLMProvider


class GeminiProvider(LLMProvider):
    """Thin adapter kept behind the application-facing LLMProvider protocol."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError(
            "Gemini transport is intentionally isolated here; install/configure the "
            "chosen Gemini SDK before enabling live generation."
        )
