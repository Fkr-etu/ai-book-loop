from __future__ import annotations

from typing import TypeVar

from google import genai
from pydantic import BaseModel

from book_loop.domain.protocols import LLMProvider

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class GeminiProvider(LLMProvider):
    """Gemini Interactions API adapter kept behind the application-facing LLMProvider protocol."""

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
            generation_config={"thinking_level": "medium"},
        )
        text = interaction.output_text
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response")
        return text.strip()

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[StructuredModel],
        thinking_level: str = "medium",
        max_output_tokens: int | None = None,
    ) -> StructuredModel:
        """Generate and validate a response using Gemini's native JSON-schema output."""
        generation_config: dict[str, object] = {"thinking_level": thinking_level}
        if max_output_tokens is not None:
            generation_config["max_output_tokens"] = max_output_tokens

        interaction = self.client.interactions.create(
            model=self.model,
            input=user_prompt,
            system_instruction=system_prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": schema.model_json_schema(),
            },
            generation_config=generation_config,
        )
        text = interaction.output_text
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty structured response")
        try:
            return schema.model_validate_json(text)
        except ValueError as exc:
            raise ValueError(
                f"Gemini returned structured output that does not match {schema.__name__}"
            ) from exc
