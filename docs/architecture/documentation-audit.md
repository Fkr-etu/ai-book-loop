# Documentation audit

**Baseline:** `main` at the start of the documentation reconciliation work.

This inventory classifies repository documentation against the implemented code, tests, workflows and current product direction. The rule is to keep documentation that is useful and true, update documentation that describes a live concept but has drifted, and remove or archive documentation that can mislead implementation work.

## Classification

### Keep

- `docs/README.md` — canonical documentation index; keep as the entry point.
- `docs/glossary.md` — useful shared vocabulary; keep and extend when new domain terms become stable.
- `docs/architecture/boundaries.md` — architectural boundary reference remains useful.
- `docs/architecture/chapter-workflow-recovery.md` — operational workflow/recovery concern remains relevant.
- `docs/architecture/creative-brief.md` — product-domain architecture remains relevant.
- `docs/architecture/document-ingestion.md` — ingestion remains a live architectural concern.
- `docs/development/setup.md` — developer onboarding remains required.
- `docs/development/testing.md` — test strategy remains required.
- `docs/development/configuration.md` — configuration reference remains required.
- `docs/development/migrations.md` — migration guidance remains required.
- `docs/development/ai-agent-workflow.md` — mandatory source-discovery workflow for AI agents.
- `docs/development/contributing.md` — contribution rules remain useful.
- `docs/security/authentication.md` — security reference remains required.
- `docs/architecture/decisions/*` — ADRs are historical architecture decisions; retain unless a decision is explicitly superseded, in which case mark it superseded rather than silently deleting history.

### Update / reconcile

- `docs/architecture/approved-chapter-canon-flow.md` — align with current approval → assertion extraction → conflict detection → explicit review → Canon lifecycle.
- `docs/architecture/canon-assertion-extraction.md` — distinguish extraction from detection and Canon promotion; document current consistency surfaces.
- `docs/architecture/canonical-review.md` — align review semantics with `ConsistencyIssue`, provenance and explicit author decisions.
- `docs/architecture/canonical-context.md` — verify terminology and ownership against current Canon/knowledge repository implementation; avoid presenting speculative context assembly as implemented behavior.
- `docs/architecture/consistency-engine.md` — current architecture must describe `UnifiedConsistencyEngine`, detector composition, stable IDs/deduplication and the fact that execution is currently sequential.
- `docs/architecture/data-model.md` — keep as the data model authority, but reconcile it with assertions, evidence, conflicts, review decisions, canonical facts and consistency projections.
- `docs/architecture/deployment-guide.md` — reconcile with the current Cloud Build/deployment path and security configuration.
- `docs/architecture/gcp-architecture.md` — reconcile with the deployed GCP topology and current build/runtime assumptions.
- `docs/architecture/generation-review-correction.md` — preserve the workflow but make consistency analysis a first-class review input rather than implying a purely generation-centric loop.
- `docs/product/frontend-api-contract.md` — treat as a contract reference only where it matches the current API; reconcile after frontend/API evolution.
- `docs/product/fe-2b2-studio-contract.md` and `docs/product/fe-2b-5-chapters-contract.md` — retain as implementation history/contracts, but mark completed work and avoid presenting completed FE-2B milestones as future work.
- `docs/product/roadmap.md` — update the product direction so Corpus Intelligence / Consistency Engine is the differentiating core; remove completed work from future milestones.
- `docs/product/scope.md` — reconcile with the current MVP scope and consistency-first product direction.
- `docs/product/positioning.md` — reconcile messaging with the current differentiator: Book Loop detects and explains consistency conflicts with evidence while the author decides.
- `docs/product/analytics-plan.md` — keep, but ensure events correspond to actual product surfaces and current north-star behavior.
- `docs/product/b2c-france-commercial-readiness.md`, `docs/product/billing-capacity-policy.md`, `docs/product/infrastructure-costs.md`, `docs/product/legal-launch-checklist.md`, `docs/product/pricing-strategy.md` — keep as planning documents, but label assumptions/targets clearly and do not treat them as implementation truth.
- `docs/product/seo-content.md` and `docs/product/seo-content-implementation.md` — retain only as marketing/SEO planning references; keep them out of the implementation source-of-truth path.

### Do not delete by default

No repository documentation was identified as safe to delete solely because it is old. ADRs and product planning documents have historical value. The dangerous case is stale implementation guidance; those documents should be explicitly marked as planning/history or reconciled with code.

## Source-of-truth hierarchy

1. Executable code and tests define implemented behavior.
2. Database migrations define persisted schema history.
3. ADRs define architectural decisions and their historical rationale.
4. Architecture documentation explains the current implementation and must not contradict code.
5. Product documents define intent, scope and hypotheses; they are not implementation contracts unless explicitly labelled as such.

When a document says that a capability is "planned", first search `main` for the capability and its tests. Completed capabilities must not remain described as future work.

## Consistency-specific ownership

- `ExtractChapterAssertions`: extraction/proposal of assertions from approved chapter material.
- `DetectConflicts`: persisted assertion-vs-assertion conflict detection.
- `CanonDiagnosticChecker`: new-text-vs-active-Canon diagnostics.
- `UnifiedConsistencyEngine`: composition and stable deduplication of consistency detectors.
- `ConsistencyIssue`: author-facing consistency projection; it is not itself persisted Canon truth.
- Canon promotion/review remains an explicit author decision.

The product principle is: **L’IA propose, l’auteur décide.**
