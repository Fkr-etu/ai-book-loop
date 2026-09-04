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

    @staticmethod
    def _reconcile_offsets(*, chunk_content: str, assertion: ExtractedAssertion) -> ExtractedAssertion:
        """Derive provenance offsets from source text instead of trusting the LLM."""
        start = chunk_content.find(assertion.statement)
        if start < 0:
            raise ValueError("Assertion extractor returned a statement not found in source chunk")
        return assertion.model_copy(
            update={"start_offset": start, "end_offset": start + len(assertion.statement)}
        )

    def extract(self, *, chunk: DocumentChunk) -> list[ExtractedAssertion]:
        result = self._provider.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=f"SOURCE CHUNK:\n{chunk.content}",
            schema=ExtractedAssertions,
            thinking_level="minimal",
            max_output_tokens=4096,
        )
        return [
            self._reconcile_offsets(chunk_content=chunk.content, assertion=assertion)
            for assertion in result.assertions
        ]
