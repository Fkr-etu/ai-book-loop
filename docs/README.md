# Documentation

This directory is the project knowledge base. Keep documentation small, canonical, and versioned with the code.

## Where to look

- `product/` — product vision, MVP scope, and roadmap.
- `architecture/overview.md` — current system architecture.
- `architecture/principles.md` — architectural invariants and boundaries.
- `architecture/workflows.md` — business workflows, especially chapter generation.
- `architecture/data-model.md` — persisted domain model and continuity data.
- `architecture/decisions/` — Architecture Decision Records (ADRs).
- `development/` — setup, testing, configuration, and contribution workflow.
- `glossary.md` — project-specific terminology.

## Documentation rule

Documentation describing current behavior is updated in the same change as the code. Historical architectural decisions are preserved as ADRs and superseded rather than rewritten.

`AGENTS.md` is the operational entry point for AI coding agents. It contains rules and points to the canonical documentation; it should not duplicate detailed architecture documentation.
