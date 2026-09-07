# Documentation audit

**Baseline:** `main` at the start of the documentation reconciliation work.

This inventory classifies repository documentation against implemented code, tests, workflows and current product direction. The rule is to keep documentation that is useful and true, update documentation that describes a live concept but has drifted, and remove or explicitly archive documentation that can mislead implementation work.

## Classification

### Keep

- `docs/README.md` — canonical documentation index; keep as the entry point.
- `docs/glossary.md` — shared vocabulary; extend when new domain terms become stable.
- `docs/architecture/boundaries.md` — architectural boundary reference.
- `docs/architecture/chapter-workflow-recovery.md` — operational recovery reference.
- `docs/architecture/creative-brief.md` — product-domain architecture reference.
- `docs/architecture/document-ingestion.md` — live ingestion concern.
- `docs/development/setup.md` — developer onboarding.
- `docs/development/testing.md` — test strategy.
- `docs/development/configuration.md` — configuration reference.
- `docs/development/migrations.md` — migration guidance.
- `docs/development/ai-agent-workflow.md` — source-discovery workflow for AI agents.
- `docs/development/contributing.md` — contribution rules.
- `docs/security/authentication.md` — security reference.
- `docs/architecture/decisions/*` — historical ADRs; retain history and mark superseded decisions explicitly.

### Reconciled in this PR

- `docs/architecture/overview.md` — current architecture and persistence/consistency boundaries.
- `docs/architecture/workflows.md` — current workflow, validation and recovery behavior.
- `docs/architecture/approved-chapter-canon-flow.md` — Canon approval lifecycle.
- `docs/architecture/canon-assertion-extraction.md` — extraction versus detection versus promotion.
- `docs/architecture/canonical-review.md` — review semantics and evidence.
- `docs/architecture/canonical-context.md` — current Canon context terminology/ownership.
- `docs/architecture/consistency-engine.md` — `UnifiedConsistencyEngine`, detector composition and sequential execution.
- `docs/architecture/data-model.md` — assertions, evidence, conflicts, review decisions and canonical facts.
- `docs/architecture/deployment-guide.md` — current GCP/Cloud Build path.
- `docs/architecture/gcp-architecture.md` — current GCP topology/runtime assumptions.
- `docs/architecture/generation-review-correction.md` — consistency as a review input.
- `docs/product/roadmap.md` — current product sequencing and consistency-first priority.
- `docs/product/scope.md` — current MVP boundary and production persistence.
- `docs/product/positioning.md` — current differentiator and commercial hypothesis.
- `docs/product/vision.md` — current narrative-consistency product thesis.

### Keep as planning / contract history

- `docs/product/frontend-api-contract.md` — API contract reference; implementation truth remains code and tests.
- `docs/product/fe-2b2-studio-contract.md` and `docs/product/fe-2b-5-chapters-contract.md` — completed implementation history/contracts.
- `docs/product/analytics-plan.md` — telemetry plan; validate events against actual surfaces before enabling production tracking.
- `docs/product/b2c-france-commercial-readiness.md`, `docs/product/billing-capacity-policy.md`, `docs/product/infrastructure-costs.md`, `docs/product/legal-launch-checklist.md`, `docs/product/pricing-strategy.md` — commercial/operational planning documents; assumptions are not implementation truth.
- `docs/product/seo-content.md` and `docs/product/seo-content-implementation.md` — marketing/SEO planning references, outside the implementation source-of-truth path.

### Historical

- `docs/architecture/linguistic-validation-implementation.md` — historical implementation record. It must not be read as a statement of current workflow wiring or as a roadmap; current behavior belongs in the live architecture documents.

### No deletions

No document was identified as safe to delete solely because it is old. ADRs and product planning documents retain historical value. The dangerous case is stale implementation guidance; such documents should be reconciled or explicitly marked historical rather than silently removed.

## Source-of-truth hierarchy

1. Executable code and tests define implemented behavior.
2. Database migrations define persisted schema history.
3. ADRs define architectural decisions and historical rationale.
4. Current architecture/workflow documentation explains the implementation and must not contradict code.
5. Product documents define intent, scope and hypotheses; they are not implementation contracts unless explicitly labelled as such.

When a document says a capability is "planned", search the current repository for the capability and its tests before implementing it. Completed capabilities must not remain described as future work.

## Consistency-specific ownership

- `ExtractChapterAssertions`: extraction/proposal of assertions from approved chapter material.
- `DetectConflicts`: persisted assertion-vs-assertion conflict detection.
- `CanonDiagnosticChecker`: new-text-vs-active-Canon diagnostics.
- `UnifiedConsistencyEngine`: composition and stable deduplication of consistency detectors; current execution is sequential.
- `ConsistencyIssue`: author-facing consistency projection; it is not persisted Canon truth.
- Canon promotion/review remains an explicit author decision.

The product principle is: **L’IA propose, l’auteur décide.**
