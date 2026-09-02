# Canonical context

The third stage of ADR 001 makes approved knowledge available to chapter generation.

```text
CanonicalFact (active)
        ↓
   ContextBuilder
        ↓
 chapter generation
        ↓
      Writer
```

Only active `CanonicalFact` records are exposed. Proposed, deferred, rejected, and inactive historical facts are never injected into generation context.

Each canonical entry carries its fact and assertion identifiers so downstream tooling can retain provenance. The underlying chain remains:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`

`ContextBuilder` accepts an optional `KnowledgeRepository`, preserving compatibility for callers that do not configure knowledge storage yet.

Vector search, semantic ranking, and chapter-specific retrieval are intentionally deferred. This stage provides deterministic canonical context first; retrieval optimization can be added without weakening the canonical boundary.
