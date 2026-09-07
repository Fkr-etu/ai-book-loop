# AI Agent Workflow

This project is developed with AI coding agents. The goal of this document is not to constrain implementation style; it is to make repository knowledge discoverable and prevent an agent from rebuilding capabilities that already exist.

## Core rule

> **SEARCH → INSPECT → REUSE → EXTEND → CREATE only when necessary.**

An agent must not treat the absence of a feature name in its current task description as evidence that the feature is absent from the repository.

## Required pre-change reconnaissance

For every non-trivial change, an agent should establish:

1. **Current base** — inspect the current `main`, not an old PR branch or conversation snapshot.
2. **Capability search** — search for the requested business concept and its likely synonyms.
3. **Symbol search** — search for relevant classes, functions, ports, repository methods, API routes, and test names.
4. **Architecture search** — inspect the relevant architecture document and ADRs.
5. **Test search** — inspect tests that exercise the capability, including integration/E2E tests.
6. **Dependency search** — inspect the composition root and call sites before adding a new service or adapter.

### Example search vocabulary

For a consistency feature, do not search only for `consistency`. Also search for terms such as:

- Canon / canonical
- assertion
- evidence / provenance
- conflict
- diagnostic
- validation
- continuity
- review
- `DetectConflicts`
- `CanonDiagnosticChecker`
- `AnalyzeConsistency`
- `UnifiedConsistencyEngine`

The exact terms vary by task. The principle is to search by **concept + implementation symbol + persistence/API surface + tests**.

## Build an inventory before adding code

For a proposed capability, answer these questions explicitly in the working notes or PR description:

| Question | Evidence to inspect |
|---|---|
| Does the capability already exist? | repository search + current implementation |
| Is there an existing domain model? | `book_loop/domain/` |
| Is there an existing use case/service? | `book_loop/application/` |
| Is there an existing port? | `book_loop/domain/protocols.py` and related ports |
| Is there an existing persistence path? | repository implementation + schema/migrations |
| Is there an existing API? | API routes and contract tests |
| Is there an existing frontend surface? | `web/src/` and E2E tests |
| Is there an existing detector/validator? | application services + validation tests |
| Is there an existing test proving the behavior? | `tests/` and frontend E2E |
| Is there an ADR explaining the boundary? | `docs/architecture/decisions/` |

If several answers are yes, the default action is **integration or refactoring**, not a new implementation.

## Avoiding duplicate implementations

A duplicate implementation is particularly dangerous when two components appear to solve the same problem but have different persistence, confidence, provenance, or approval semantics.

Before creating a new service, detector, validator, repository method, or domain object:

- identify existing code that owns the rule;
- identify all current callers;
- identify the tests that protect it;
- decide whether the new requirement changes the responsibility or only adds a new entry point;
- preserve one source of truth for the underlying rule.

For consistency specifically:

- `CanonDiagnosticChecker` owns the current new-text-vs-active-Canon diagnostic rule;
- `DetectConflicts` owns persisted assertion-vs-assertion conflict detection;
- `UnifiedConsistencyEngine` owns detector composition and stable issue deduplication;
- `AnalyzeConsistency` owns the author-facing consistency application entry point;
- Canon review owns the decision that changes canonical state.

These responsibilities must not be silently collapsed into a second parallel implementation.

## Reading order for common tasks

### New domain/application behavior

1. `AGENTS.md`
2. `docs/architecture/system-map.md`
3. `docs/architecture/principles.md`
4. relevant `domain/` models and protocols
5. relevant application use cases/services
6. repository adapters and composition root
7. focused tests
8. relevant ADRs

### Workflow changes

Also read:

- `docs/architecture/workflows.md`
- `docs/architecture/chapter-workflow-recovery.md`
- workflow implementation and run-store code
- recovery/idempotency tests

### Canon/consistency changes

Also read:

- `docs/architecture/canon-assertion-extraction.md`
- `docs/architecture/canonical-review.md`
- `docs/architecture/canonical-context.md`
- `docs/architecture/consistency-engine.md`
- `docs/architecture/data-model.md`
- Canon/consistency tests

### Frontend changes

Also inspect:

- backend API contract first;
- `web/src/types/`;
- `web/src/services/api.ts`;
- existing state/store behavior;
- the corresponding E2E tests.

The frontend must not become a second source of truth for persisted business state.

## Documentation rules for agents

Do not create a new document merely because a feature was implemented.

Prefer updating an existing canonical document when the information already has a home. Add a new document only when it answers a distinct recurring question.

Use this split:

- **System map:** where something exists and how to navigate to it.
- **Architecture overview:** responsibilities and boundaries.
- **Focused architecture docs:** workflow/data/feature behavior.
- **ADR:** why a significant decision was made.
- **Development docs:** how to work safely in the repository.
- **Product docs:** what the product is trying to achieve and why.
- **Glossary:** stable vocabulary.

Never copy a full architecture description into multiple documents. Link to the canonical explanation instead.

## Change protocol

Before coding:

```text
Task
 ↓
Current main
 ↓
Search concept + symbols + tests
 ↓
Read canonical docs
 ↓
Map existing responsibility
 ↓
Reuse / extend?
 ├─ yes → implement integration/refactor
 └─ no  → introduce smallest new abstraction
```

After coding:

```text
Implementation
 ↓
Focused tests
 ↓
Regression tests
 ↓
Documentation update
 ↓
Full CI / integration checks as appropriate
 ↓
Review diff for duplicate logic
 ↓
Focused commit / PR
```

## What not to trust as current truth

The following can provide useful historical context but must not override the current repository:

- old conversations;
- old PR descriptions;
- stale branches;
- generated summaries;
- memory of a previous implementation;
- a task description that assumes something does not exist.

When in doubt, inspect `main`.

## PR checklist for AI-generated changes

- [ ] I started from current `main`.
- [ ] I searched for the business concept and relevant synonyms.
- [ ] I searched for implementation symbols and tests.
- [ ] I inspected existing callers and the composition root.
- [ ] I reused existing behavior where possible.
- [ ] I can explain why any new abstraction is necessary.
- [ ] I did not duplicate an existing deterministic rule.
- [ ] I preserved author approval and Canon invariants.
- [ ] I added/updated tests.
- [ ] I updated the canonical documentation only where needed.
- [ ] I checked the final diff for accidental duplication or dead paths.
- [ ] CI is green before considering the change complete.
