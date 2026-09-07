# Approved Chapter → Canon Flow

An approved chapter is the boundary between author-approved manuscript content and proposed Canon knowledge. Approval itself never makes chapter assertions canonical.

```text
chapter version
     ↓
author approval
     ↓
persisted source document + evidence
     ↓
proposed assertions
     ↓
consistency / conflict detection
     ↓
human assertion review
     ↓
CanonicalFact
```

## Responsibilities

1. **Approval** selects the persisted chapter version that is allowed to contribute knowledge.
2. **Extraction** creates proposed `Assertion` records with traceable `Evidence`.
3. **Detection** identifies competing claims or contradictions without deciding which claim is true.
4. **Review** records the author's/application decision and is the only path that promotes an assertion to `CanonicalFact`.
5. **Retrieval** may expose active Canon to generation and validation, but is read-only.

The current consistency architecture has two complementary detection surfaces:

- persisted assertion-vs-assertion conflicts for corpus consistency;
- new-text-vs-active-Canon diagnostics for immediate validation.

Both preserve the same product rule: **l'IA propose, l'auteur décide**.

## Invariant

Approval never promotes an assertion directly to `CanonicalFact`. The sync/extraction stage creates traceable proposals and the detection stage can create conflicts or diagnostics; human review remains authoritative for Canon state transitions.
