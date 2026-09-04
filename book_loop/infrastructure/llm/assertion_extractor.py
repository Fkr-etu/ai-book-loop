from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from book_loop.domain.models import DocumentChunk, ExtractedAssertion
from book_loop.domain.protocols import LLMProvider

logger = logging.getLogger(__name__)


class ExtractedAssertionDraft(BaseModel):
    """Provider-facing assertion shape; source provenance is derived outside the LLM."""

    statement: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedAssertions(BaseModel):
    """Provider-facing wrapper because Gemini structured outputs are object-shaped."""

    assertions: list[ExtractedAssertionDraft]


class LLMAssertionExtractor:
    """LLM adapter that converts a chunk into structured, non-canonical assertions."""

    SYSTEM_PROMPT = (
        "Extract factual assertions from the supplied source chunk. "
        "Only extract facts explicitly supported by the text. "
        "For each assertion provide the exact statement, subject, predicate, object and confidence. "
        "The statement must be an exact contiguous excerpt from the supplied source chunk; "
        "do not paraphrase it. Do not infer facts that are not supported by the source. "
        "Prefer a small set of high-value assertions and keep statements concise. "
        "Return no more than 12 assertions."
    )

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    @staticmethod
    def _to_extracted_assertion(*, chunk_content: str, draft: ExtractedAssertionDraft) -> ExtractedAssertion:
        """Build source provenance only when the statement has one unique source location."""
        positions: list[int] = []
        start = 0
        while True:
            index = chunk_content.find(draft.statement, start)
            if index < 0:
                break
            positions.append(index)
            start = index + 1

        if not positions:
            raise ValueError("Assertion extractor returned a statement not found in source chunk")
        if len(positions) > 1:
            raise ValueError("Assertion extractor returned an ambiguous statement found multiple times in source chunk")

        start = positions[0]
        return ExtractedAssertion(
            statement=draft.statement,
            subject=draft.subject,
            predicate=draft.predicate,
            object=draft.object,
            confidence=draft.confidence,
            start_offset=start,
            end_offset=start + len(draft.statement),
        )

    def extract(self, *, chunk: DocumentChunk) -> list[ExtractedAssertion]:
        result = self._provider.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=f"SOURCE CHUNK:\n{chunk.content}",
            schema=ExtractedAssertions,
            thinking_level="minimal",
            max_output_tokens=4096,
        )
        assertions: list[ExtractedAssertion] = []
        for draft in result.assertions:
            try:
                assertions.append(
                    self._to_extracted_assertion(chunk_content=chunk.content, draft=draft)
                )
            except ValueError:
                logger.warning(
                    "Dropping ungrounded or ambiguous assertion from source chunk %s: %r",
                    chunk.id,
                    draft.statement,
                )
        return assertions
