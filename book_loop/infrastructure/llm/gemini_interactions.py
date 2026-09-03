from __future__ import annotations

from google import genai

from book_loop.domain.protocols import LLMProvider


class GeminiInteractionsProvider(LLMProvider):
    """Gemini Interactions API adapter behind the application-facing protocol."""

    def __init__(self, *, api_key: str, model: str) -> None:
        if not api_key.strip():
            raise ValueError("A Gemini API key is required for live generation")
        if not model.strip():
            raise ValueError("A Gemini model is required for live generation")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        interaction = self.client.interactions.create(
            model=self.model,
            input=user_prompt,
            system_instruction=system_prompt,
        )
        text = interaction.output_text
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response")
        return text.strip()
