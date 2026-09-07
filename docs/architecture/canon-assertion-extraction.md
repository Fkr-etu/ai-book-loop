# Canon Assertion Extraction

## Purpose

Approved chapter versions are the boundary between manuscript content accepted by the author and proposed knowledge. The extraction stage turns that content into traceable assertions and evidence without promoting anything to Canon.

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
                     |
                     v
             consistency detection
                     |
              human review
                     |
                CanonicalFact
```

`ExtractChapterAssertions` is therefore an ingestion/provenance stage, not a consistency detector and not a Canon promotion mechanism.

## Invariants

- Only chapters with status `approved` may enter this flow.
- The selected persisted chapter version is the source of truth for extraction.
- Assertions remain `proposed` after extraction.
- Every assertion has evidence pointing to its source document, chunk and character offsets.
- Re-ingesting the same chapter version is idempotent through the source content hash.
- No `CanonicalFact` is created by this stage.
- Detection may identify competing assertions, but detection never selects the canonical value.

## Consistency boundary

The persisted assertion/conflict path and the author-facing consistency path are separate responsibilities:

- `DetectConflicts` compares persisted assertions and records evidence-backed `Conflict` entities.
- `CanonDiagnosticChecker` compares newly supplied text with active `CanonicalFact` records and emits diagnostics for the validation surface.
- The unified consistency layer composes detector implementations into the shared `ConsistencyIssue` contract.

These mechanisms may share assertion extraction and knowledge persistence, but they must not silently promote proposed assertions or invent canonical truth.

## Boundary

`ExtractChapterAssertions` is an application use case. It reuses `IngestDocument`, so the Canon boundary remains explicit: extraction creates proposed knowledge only. Conflict detection, consistency projection and human review are subsequent stages.
