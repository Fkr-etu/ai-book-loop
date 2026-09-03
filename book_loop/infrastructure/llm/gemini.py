from __future__ import annotations

from google import genai
from google.genai import types

from book_loop.domain.protocols import LLMProvider


class GeminiProvider(LLMProvider):
    """Gemini API adapter kept behind the application-facing LLMProvider protocol."""

    def __init__(self, *, api_key: str, model: str) -> None:
        if not api_key.strip():
            raise ValueError("A Gemini API key is required for live generation")
        if not model.strip():
            raise ValueError("A Gemini model is required for live generation")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        text = response.text
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response")
        return text.strip()
