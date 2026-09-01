from __future__ import annotations

from book_loop.domain.protocols import LLMProvider
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.llm.gemini import GeminiProvider
from book_loop.infrastructure.llm.fake import FakeLLMProvider


def create_llm(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "fake" or not settings.gemini_api_key:
        return FakeLLMProvider()
    if settings.llm_provider == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.llm_model)
    return FakeLLMProvider()
