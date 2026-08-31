from __future__ import annotations

from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.llm.gemini import GeminiLLM


def create_llm(settings: Settings):
    if settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        return GeminiLLM(api_key=settings.gemini_api_key, model=settings.llm_model)
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
