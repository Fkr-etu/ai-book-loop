from __future__ import annotations

from book_loop.domain.models import DocumentChunk
from book_loop.infrastructure.llm.assertion_extractor import ExtractedAssertionDraft, ExtractedAssertions, LLMAssertionExtractor
from book_loop.infrastructure.nlp.predicate_normalizer import RuleBasedPredicateNormalizer


class FakeProvider:
    def generate_structured(self, *, system_prompt, user_prompt, schema, thinking_level="medium", max_output_tokens=None):
        del system_prompt, user_prompt, schema, thinking_level, max_output_tokens
        return ExtractedAssertions(
            assertions=[
                ExtractedAssertionDraft(
                    statement="Marie habite à Paris.",
                    subject="Marie",
                    predicate="réside",
                    object="Paris",
                    confidence=0.97,
                )
            ]
        )


def test_extractor_normalizes_predicate_before_consistency_layer() -> None:
    extractor = LLMAssertionExtractor(
        FakeProvider(),
        predicate_normalizer=RuleBasedPredicateNormalizer(),
        language="fr",
    )

    result = extractor.extract(
        chunk=DocumentChunk(
            id="chunk-1",
            source_document_id="source-1",
            content="Marie habite à Paris.",
            sequence=0,
            start_offset=0,
            end_offset=len("Marie habite à Paris."),
        )
    )

    assert len(result) == 1
    assert result[0].predicate == "lives_in"
    assert result[0].statement == "Marie habite à Paris."
    assert result[0].object == "Paris"
