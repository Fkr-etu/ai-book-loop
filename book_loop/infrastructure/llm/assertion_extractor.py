from __future__ import annotations

from pydantic import BaseModel

from book_loop.domain.models import DocumentChunk, ExtractedAssertion
from book_loop.domain.protocols import LLMProvider


class ExtractedAssertions(BaseModel):
    """Provider-facing wrapper because Gemini structured outputs are object-shaped."""

    assertions: list[ExtractedAssertion]


class LLMAssertionExtractor:
    """LLM adapter that converts a chunk into structured, non-canonical assertions."""

    SYSTEM_PROMPT = (
        "Extract factual assertions from the supplied source chunk. "
        "Only extract facts explicitly supported by the text. "
        "For each assertion provide the exact statement, subject, predicate, object, confidence, "
        "start_offset and end_offset. Offsets are character offsets within the supplied chunk. "
        "Do not infer facts that are not supported by the source. "
        "Prefer a small set of high-value assertions and keep statements concise. "
        "Return no more than 12 assertions."
    )

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def extract(self, *, chunk: DocumentChunk) -> list[ExtractedAssertion]:
        result = self._provider.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=f"SOURCE CHUNK:\n{chunk.content}",
            schema=ExtractedAssertions,
            thinking_level="medium",
            max_output_tokens=8192,
        )
        assertions = result.assertions
        for assertion in assertions:
            if assertion.end_offset > len(chunk.content):
                raise ValueError("Assertion extractor returned an out-of-range end offset")
            if assertion.start_offset >= assertion.end_offset:
                raise ValueError("Assertion extractor returned an invalid offset range")
        return assertions
