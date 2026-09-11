# Documentation

This directory is the project's canonical knowledge base. Keep documentation small, focused, and versioned with the code. **Code and tests define implemented behavior; product documents define intent and hypotheses; ADRs preserve historical decisions.**

## Start here

### Product

- `product/positioning.md` — current positioning, personas, differentiation and business-model hypotheses.
- `product/scope.md` — current product boundary.
- `product/roadmap.md` — sequencing and next product work.
- `product/pricing-strategy.md` — pricing and unit-economics hypotheses.
- `product/infrastructure-costs.md` — infrastructure cost scenarios.
- `product/analytics-plan.md` — product analytics plan.
- `product/b2c-france-commercial-readiness.md` — commercial-readiness planning.
- `product/billing-capacity-policy.md` — billing/capacity planning.
- `product/legal-launch-checklist.md` — launch/legal checklist.
- `product/seo-content.md` — consolidated SEO content, positioning and technical SEO baseline.
- `product/seo-operations.md` — SEO production/deployment operations.
- `product/ui-ux-audit.md` — UX audit/reference.

### Architecture

- `architecture/overview.md` — current system architecture and responsibilities.
- `architecture/principles.md` — architectural invariants.
- `architecture/boundaries.md` — dependency boundaries.
- `architecture/workflows.md` — current book/chapter workflows and recovery semantics.
- `architecture/data-model.md` — persisted domain and workflow/job model.
- `architecture/async-analysis-jobs.md` — PostgreSQL analysis queue, worker, leases and recovery.
- `architecture/approved-chapter-canon-flow.md` — approved-chapter/Canon lifecycle.
- `architecture/canon-assertion-extraction.md` — assertion extraction and provenance.
- `architecture/canonical-review.md` — Canon review semantics.
- `architecture/canonical-context.md` — Canon context construction.
- `architecture/consistency-engine.md` — current consistency detector composition.
- `architecture/consistency-issue-contract.md` — author-facing consistency finding contract.
- `architecture/narrative-state.md` — narrative events, temporal relations and entity state.
- `architecture/chapter-workflow-recovery.md` — durable chapter workflow recovery semantics.
- `architecture/document-ingestion.md` — document-ingestion design.
- `architecture/generation-review-correction.md` — generation/review/correction boundaries.
- `architecture/critical-eye.md` — Critical Eye / Œil critique architecture and MVP boundaries.
- `architecture/deployment-guide.md` — production deployment operations.
- `architecture/gcp-architecture.md` / `architecture/hosting-options.md` — infrastructure reference and hosting decisions.
- `architecture/linguistic-validation-implementation.md` — historical implementation note; not the current source of truth.
- `architecture/documentation-audit.md` — documentation audit and classification.
- `architecture/decisions/` — historical architecture decisions (ADRs).

### Development

- `development/setup.md` — local setup and project commands.
- `development/testing.md` — testing strategy.
- `development/configuration.md` — configuration rules.
- `development/migrations.md` — database migration guidance.
- `development/contributing.md` — contribution workflow.
- `development/ai-agent-workflow.md` — mandatory workflow for AI-assisted changes.
- `glossary.md` — project terminology.

## Source-of-truth rules

- **Current implementation** → code + tests.
- **Persisted schema history** → Alembic migrations.
- **Current architecture** → `architecture/overview.md` and the focused architecture documents linked above.
- **Architecture invariants** → `architecture/principles.md`.
- **Current workflows/recovery** → `architecture/workflows.md` + `architecture/chapter-workflow-recovery.md`.
- **Long-running analysis execution** → `architecture/async-analysis-jobs.md`.
- **Consistency architecture** → `architecture/consistency-engine.md`.
- **Persisted knowledge model** → `architecture/data-model.md`.
- **Product intent/scope** → `product/positioning.md`, `product/scope.md`, `product/roadmap.md`.
- **Historical decisions** → `architecture/decisions/`.
- **AI-agent operating rules** → root `AGENTS.md` and `development/ai-agent-workflow.md`.

Do not use a product roadmap as evidence that a capability is unimplemented. Search the code and tests first. Do not use an ADR as the current implementation contract when later code or an explicit superseding ADR changed the decision.

## Documentation maintenance

Documentation describing current behavior is updated in the same change as the code. Significant architectural decisions get an ADR. When a decision changes, preserve the old ADR and supersede it rather than rewriting history. Planning documents should clearly label assumptions and targets. Avoid creating separate documents for the same source of truth; consolidate when two planning notes cover the same subject.
