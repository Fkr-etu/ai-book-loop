# Canon Assertion Extraction

## Purpose

Stage 11 connects approved chapter versions to the existing knowledge-ingestion boundary. It extracts factual assertions and their evidence without promoting anything to Canon.

## Flow

```text
Approved Chapter Version
        |
        v
ExtractChapterAssertions
        |
        v
IngestDocument
        |
        +--> SourceDocument (approved_chapter)
        +--> DocumentChunk
        +--> Assertion (proposed)
        +--> Evidence
```

## Invariants

- Only chapters with status `approved` may enter this flow.
- The selected persisted chapter version is the source of truth for extraction.
- Assertions remain `proposed` after extraction.
- Every assertion has an evidence record pointing to its source document, chunk and character offsets.
- Re-ingesting the same chapter version is idempotent through the source content hash.
- No CanonicalFact is created by this stage.

## Boundary

`ExtractChapterAssertions` is an application use case. It reuses `IngestDocument`, so the Canon boundary remains explicit: extraction creates proposed knowledge only. Conflict detection and human review remain subsequent stages.
