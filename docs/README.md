# Documentation

This directory is the project's canonical knowledge base. Keep documentation small, focused, and versioned with the code.

## Start here

### Product

- `product/vision.md` — **why** the product exists and the long-term thesis.
- `product/strategy.md` — strategic choices, moat, sequencing logic, and infrastructure gates.
- `product/scope.md` — **what is in the current MVP** and what is explicitly out.
- `product/roadmap.md` — **what comes next**, from Book validation through future Knowledge QA.
- `product/pricing-strategy.md` — pricing and unit-economics hypotheses.
- `product/infrastructure-costs.md` — infrastructure cost scenarios and migration triggers.

### Architecture

- `architecture/overview.md` — current system architecture and responsibilities.
- `architecture/principles.md` — architectural invariants.
- `architecture/boundaries.md` — dependency boundaries.
- `architecture/workflows.md` — current book/chapter workflows.
- `architecture/data-model.md` — persisted domain model and canonical-state evolution.
- `architecture/canonical-review.md` — implemented Canon review semantics.
- `architecture/document-ingestion.md` — document-ingestion design and boundaries.
- `architecture/decisions/` — historical architecture decisions (ADRs).

### Development

- `development/setup.md` — local setup and how to run the project.
- `development/testing.md` — testing strategy.
- `development/configuration.md` — configuration rules.
- `development/contributing.md` — contribution workflow.
- `glossary.md` — project terminology.

## Source-of-truth rules

Use one canonical document for each type of information:

- **Vision** → `product/vision.md`
- **Strategy** → `product/strategy.md`
- **Current scope** → `product/scope.md`
- **Roadmap / sequencing** → `product/roadmap.md`
- **Pricing** → `product/pricing-strategy.md`
- **Current architecture** → `architecture/overview.md`
- **Architecture invariants** → `architecture/principles.md`
- **Persisted model** → `architecture/data-model.md`
- **Historical decisions** → `architecture/decisions/`
- **Operational agent rules** → root `AGENTS.md`

Do not duplicate roadmap phases in scope documents or architectural rules in ADRs. ADRs are historical records; current behavior belongs in the current architecture/workflow documents.

## Documentation maintenance

Documentation describing current behavior is updated in the same change as the code. Significant architectural decisions get an ADR. When a decision changes, preserve the old ADR and supersede it with a new one rather than rewriting history.
