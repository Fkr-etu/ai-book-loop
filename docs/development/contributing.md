# Contributing

## Development loop

1. Start from an up-to-date `main` branch.
2. Read `AGENTS.md`.
3. Read `docs/architecture/system-map.md` and the architecture/workflow documentation relevant to the change.
4. Search the repository for the requested capability, synonyms, implementation symbols, API routes, persistence paths, and tests.
5. Inspect existing implementations and their callers before designing a new abstraction.
6. Create a focused feature or fix branch.
7. Make the smallest coherent change that preserves the architecture.
8. Add or update tests.
9. Update the canonical documentation in the same change when behavior or architecture changes.
10. Run the relevant test suite.
11. Review the diff specifically for duplicated logic, dead paths, and accidental second sources of truth.
12. Commit with a focused message.
13. Push the branch and open a pull request.

The default implementation strategy is:

> **SEARCH → INSPECT → REUSE → EXTEND → CREATE only when necessary.**

A previous PR, task description, or conversation is historical context. The current repository is the source of truth.

## Architectural changes

If a change alters a significant technology or boundary decision, add an ADR. Keep historical ADRs immutable and mark newer decisions as superseding older ones.

## Documentation

Use the documentation split defined in `docs/architecture/system-map.md`:

- system map — where capabilities and canonical implementations live;
- architecture overview — responsibilities and boundaries;
- focused architecture docs — workflow/data/feature behavior;
- ADRs — why significant decisions were made;
- development docs — how to work safely;
- product docs — product intent and strategy;
- glossary — stable vocabulary.

Do not create a new document if an existing canonical document can answer the question. Prefer updating and linking existing documentation over copying the same explanation into several places.

## Pull requests

PRs should explain the intent, the architectural impact, how the change reuses or extends existing code, and how it was validated. If a new abstraction was introduced, explain why an existing one could not be extended cleanly.

Do not merge with a failing test pipeline.
