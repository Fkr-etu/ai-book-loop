from __future__ import annotations

from book_loop.domain.models import DocumentChunk
from book_loop.infrastructure.llm.assertion_extractor import (
    ExtractedAssertionDraft,
    LLMAssertionExtractor,
)


def draft(statement: str) -> ExtractedAssertionDraft:
    return ExtractedAssertionDraft(
        statement=statement,
        subject="Alice",
        predicate="occupation",
        object="archivist",
        confidence=0.99,
    )


def test_provenance_requires_a_unique_statement_location():
    content = "Alice is an archivist. Later, Alice is an archivist."

    try:
        LLMAssertionExtractor._to_extracted_assertion(
            chunk_content=content,
            draft=draft("Alice is an archivist."),
        )
    except ValueError as exc:
        assert "ambiguous" in str(exc)
    else:
        raise AssertionError("Expected repeated source statement to be rejected")


def test_provenance_accepts_a_unique_statement_location():
    content = "Alice is an archivist. Bob is a sailor."

    assertion = LLMAssertionExtractor._to_extracted_assertion(
        chunk_content=content,
        draft=draft("Bob is a sailor."),
    )

    assert assertion.start_offset == content.index("Bob is a sailor.")
    assert assertion.end_offset == assertion.start_offset + len(assertion.statement)


def test_extraction_drops_ambiguous_candidates_but_keeps_valid_candidates():
    class FakeProvider:
        def generate_structured(self, **kwargs):
            return type(
                "Result",
                (),
                {
                    "assertions": [
                        draft("Alice is an archivist."),
                        draft("Bob is a sailor."),
                    ]
                },
            )()

    content = "Alice is an archivist. Bob is a sailor. Alice is an archivist."
    chunk = DocumentChunk(
        id="chunk-1",
        source_document_id="source-1",
        content=content,
        sequence=0,
        start_offset=0,
        end_offset=len(content),
    )

    assertions = LLMAssertionExtractor(FakeProvider()).extract(chunk=chunk)

    assert [assertion.statement for assertion in assertions] == ["Bob is a sailor."]
