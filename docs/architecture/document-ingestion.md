# Document ingestion

The document ingestion engine implements the first stage of ADR 001's canonical knowledge lifecycle.

```text
SourceDocument -> chunks -> extraction -> Assertions -> Evidence
```

Ingestion output is deliberately non-canonical. Assertions start with `proposed` status and require a later review/approval workflow before they can contribute to Canon.

## Boundaries

- `IngestDocument` is the application use case.
- `AssertionExtractor` is an application-facing port.
- `LLMAssertionExtractor` is an infrastructure adapter around the existing `LLMProvider` port.
- `KnowledgeRepository` persists source documents, chunks, assertions, and evidence.
- SQLite is the current persistence implementation; the schema is additive and keeps source material and provenance auditable.

## Invariants

- Source content is normalized and identified by a SHA-256 content hash.
- Re-ingesting the same `(book_id, content_hash)` is idempotent and does not call the extractor again.
- Every assertion has evidence pointing to a source document and chunk.
- Extractor confidence is bounded to `[0, 1]`.
- Evidence offsets are validated deterministically in Python.
- Contradictory assertions are stored independently; ingestion never resolves conflicts.
- No ingestion operation promotes an assertion to Canon.

## Retrieval

No vector index is required by ingestion. Relational persistence remains the source of truth; semantic retrieval can be added later as an optimization without changing the ingestion contract.
