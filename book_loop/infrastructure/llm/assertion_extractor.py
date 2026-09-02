from __future__ import annotations

import json

from book_loop.domain.models import DocumentChunk, ExtractedAssertion
from book_loop.domain.protocols import LLMProvider


class LLMAssertionExtractor:
    """LLM adapter that converts a chunk into structured, non-canonical assertions."""

    SYSTEM_PROMPT = (
        "Extract factual assertions from source text. Return ONLY a JSON array. "
        "Each item must contain statement, subject, predicate, object, confidence, "
        "start_offset and end_offset. Offsets are character offsets within the supplied text. "
        "Do not infer facts that are not supported by the text. Confidence must be between 0 and 1."
    )

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def extract(self, *, chunk: DocumentChunk) -> list[ExtractedAssertion]:
        raw = self._provider.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=f"SOURCE CHUNK:\n{chunk.content}",
        )
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("Assertion extractor must return a JSON array")
        return [ExtractedAssertion.model_validate(item) for item in payload]
