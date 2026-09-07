# AI Book Loop — Agent Instructions

## Mission

AI Book Loop helps an author produce a coherent book chapter by chapter while preserving author intent and canonical continuity.

The current product wedge is the book-writing experience. The core technical value is evidence-backed continuity: Book Loop should know what has been approved, what is merely proposed, what conflicts, and where claims came from.

> **L'IA propose, l'auteur décide.**

## Source-of-truth hierarchy

When deciding what currently exists or how the system behaves, use this order:

1. Current code on `main`.
2. Tests on `main`.
3. Focused architecture documentation.
4. ADRs for historical architectural intent.
5. README/product documentation for orientation.
6. PRs and commits for history.
7. Conversation history or memory only as context.

Never assume a capability is missing because it was not mentioned in a task or because an old conversation did not mention it.

See `docs/architecture/system-map.md` for the repository navigation map and `docs/development/ai-agent-workflow.md` for the complete AI development protocol.

## Before changing code

1. Read this file.
2. Start from an up-to-date `main` branch.
3. Read `docs/architecture/system-map.md` and the relevant architecture/workflow documentation.
4. Search the repository for the requested business concept, synonyms, implementation symbols, API surfaces, persistence paths, and tests.
5. Inspect existing implementations and their callers before designing a new abstraction.
6. Read relevant ADRs when changing an architectural boundary or technology decision.
7. Run the relevant tests before and after the change when practical.

### Mandatory anti-duplication rule

> **SEARCH → INSPECT → REUSE → EXTEND → CREATE only when necessary.**

Before adding a use case, service, detector, validator, repository method, domain object, API route, or frontend state model, establish that an existing implementation cannot be reused or extended cleanly.

For consistency work, always search at minimum for `CanonDiagnosticChecker`, `DetectConflicts`, `AnalyzeConsistency`, `UnifiedConsistencyEngine`, assertions, evidence, conflicts, diagnostics, Canon, and related tests.

If an existing component already owns the deterministic rule, keep it as the source of truth. Adapt or compose it rather than implementing the same rule twice.

## Architecture boundaries

The dependency direction is:

`CLI / adapters -> application use cases -> domain / ports <- infrastructure implementations`

Rules:

- Business actions belong in explicit application use cases.
- Domain code must not depend on infrastructure or an LLM provider.
- CLI code must not access SQLite or instantiate LLM providers directly.
- Agents are adapters/capabilities, not business use cases.
- Deterministic business rules belong in Python, not prompts.
- Keep LangGraph isolated to workflow orchestration; use plain Python when it is sufficient.
- Keep the LLM provider configurable and behind an application-facing port.
- Preserve chapter history; do not overwrite drafts or reviews when a new version is produced.
- The backend remains authoritative for persisted business state; the frontend is a client, not a second domain implementation.

## Author intent and continuity

The author's theme, idea, lore, and constraints are first-class inputs. Generated content must be evaluated against them.

Chapter generation is chapter-scoped, but every chapter receives canonical context derived from the book state and prior approved material. A chapter must not be generated before the outline is approved.

Canon is never silently changed by generation, extraction, validation, or an LLM response. Detection proposes; explicit review decisions change canonical state.

## Cost discipline

Avoid unnecessary LLM calls. Prefer deterministic validation before calling an LLM, keep prompts focused, and reuse persisted canonical information instead of regenerating it.

## Testing

Tests must run without real LLM calls. Use fakes/mocks for providers. CI is the final gate: do not consider a change complete while the test pipeline is failing.

For consistency changes, test both the underlying detector and its integration/fusion behavior. Stable issue identity and idempotency are part of the contract.

## Documentation maintenance

Update documentation in the same change when behavior, architecture, workflow, configuration, or a documented constraint changes.

Use the documentation split described in `docs/architecture/system-map.md`:

- system map = where things exist;
- architecture overview = responsibilities and boundaries;
- focused docs = workflow/data/feature behavior;
- ADR = why a significant decision was made;
- development docs = how to work safely;
- product docs = product intent and strategy;
- glossary = stable vocabulary.

Add an ADR for a significant architectural decision. Do not rewrite historical ADRs; supersede them with a new ADR when necessary.

Keep one canonical source for each piece of information. Avoid duplicating architecture or workflow descriptions across documents. Prefer links to the canonical explanation.

If documentation already answers the question, update it rather than creating another document.

## Definition of Done

A change is complete when:

- the implementation is covered by appropriate tests;
- architecture boundaries remain intact;
- relevant documentation is updated;
- significant architectural decisions have an ADR;
- unnecessary LLM cost has been considered;
- the final diff contains no accidental duplicate implementation;
- CI passes;
- the change is committed with a focused message and pushed to the working branch.
