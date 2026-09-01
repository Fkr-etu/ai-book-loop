# AI Book Loop — Agent Instructions

## Mission

AI Book Loop helps an author produce a coherent book chapter by chapter while preserving author intent and canonical continuity.

## Before changing code

1. Read this file.
2. Read `docs/architecture/principles.md` and the relevant architecture/workflow documentation.
3. Inspect the relevant domain models, use cases, ports, and adapters.
4. Read relevant ADRs when changing an architectural boundary or technology decision.
5. Run the test suite before and after the change when practical.

## Architecture boundaries

The dependency direction is:

`CLI / adapters -> Application use cases -> Domain / ports <- Infrastructure adapters`

Rules:

- Business actions belong in explicit application use cases.
- Domain code must not depend on infrastructure or an LLM provider.
- CLI code must not access SQLite or instantiate LLM providers directly.
- Agents are adapters/capabilities, not business use cases.
- Deterministic business rules belong in Python, not prompts.
- Keep LangGraph isolated to workflow orchestration; use plain Python when it is sufficient.
- Keep the LLM provider configurable and behind an application-facing port.
- Preserve chapter history; do not overwrite drafts or reviews when a new version is produced.

## Author intent and continuity

The author's theme, idea, lore, and constraints are first-class inputs. Generated content must be evaluated against them.

Chapter generation is chapter-scoped, but every chapter receives canonical context derived from the book state and prior approved material. A chapter must not be generated before the outline is approved.

## Cost discipline

Avoid unnecessary LLM calls. Prefer deterministic validation before calling an LLM, keep prompts focused, and reuse persisted canonical information instead of regenerating it.

## Testing

Tests must run without real LLM calls. Use fakes/mocks for providers. CI is the final gate: do not consider a change complete while the test pipeline is failing.

## Documentation maintenance

Update documentation in the same change when behavior, architecture, workflow, configuration, or a documented constraint changes.

Add an ADR for a significant architectural decision. Do not rewrite historical ADRs; supersede them with a new ADR when necessary.

Keep one canonical source for each piece of information. Avoid duplicating architecture or workflow descriptions across documents.

## Definition of Done

A change is complete when:

- the implementation is covered by appropriate tests;
- architecture boundaries remain intact;
- relevant documentation is updated;
- significant architectural decisions have an ADR;
- unnecessary LLM cost has been considered;
- CI passes;
- the change is committed with a focused message and pushed to the working branch.
