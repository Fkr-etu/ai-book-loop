# Documentation audit

**Baseline:** `main` on 11 September 2026, after the PostgreSQL analysis-job worker and Critical Eye MVP work.

This inventory classifies repository documentation against implemented code, tests, workflows and current product direction. The rule is: keep documentation that is useful and true, update documentation that describes a live concept but has drifted, and explicitly mark historical/planning material so it cannot be mistaken for implementation truth.

## Classification

### Keep / current

- `docs/README.md` — canonical documentation index.
- `docs/glossary.md` — shared vocabulary.
- `docs/architecture/overview.md` — current architecture.
- `docs/architecture/principles.md` — architectural invariants.
- `docs/architecture/boundaries.md` — architectural boundaries.
- `docs/architecture/workflows.md` — current workflows.
- `docs/architecture/chapter-workflow-recovery.md` — chapter recovery behavior and limitations.
- `docs/architecture/async-analysis-jobs.md` — long-running analysis queue, worker, leases and recovery.
- `docs/architecture/data-model.md` — persisted domain, workflow and analysis-job model.
- `docs/architecture/narrative-state.md` — narrative events, temporal relations and entity state.
- `docs/architecture/consistency-engine.md` — consistency detector composition.
- `docs/architecture/consistency-issue-contract.md` — author-facing consistency finding contract.
- `docs/architecture/canonical-review.md` — review semantics.
- `docs/architecture/canonical-context.md` — Canon context.
- `docs/architecture/approved-chapter-canon-flow.md` — Canon lifecycle.
- `docs/architecture/canon-assertion-extraction.md` — extraction/provenance.
- `docs/architecture/document-ingestion.md` — ingestion design.
- `docs/architecture/critical-eye.md` — Critical Eye / Œil critique boundaries.
- `docs/architecture/deployment-guide.md` and `docs/architecture/gcp-architecture.md` — deployment/runtime reference.
- `docs/development/*` — setup, testing, configuration, migrations, contributing and AI-agent workflow.
- `docs/security/authentication.md` — security reference; update when security behavior changes.
- `docs/architecture/decisions/*` — historical ADRs; preserve history and supersede decisions explicitly.

### Current product documents

- `docs/product/positioning.md` — current positioning and commercial model hypothesis.
- `docs/product/scope.md` — current MVP boundary.
- `docs/product/roadmap.md` — current sequencing and implementation status.
- `docs/product/pricing-strategy.md` — current pricing hypothesis.
- `docs/product/infrastructure-costs.md` — current infrastructure/unit-economics planning.

### Planning / operational references

- `docs/product/analytics-plan.md` — telemetry plan.
- `docs/product/b2c-france-commercial-readiness.md` — commercial-readiness planning.
- `docs/product/billing-capacity-policy.md` — implemented billing/capacity model and operating assumptions.
- `docs/product/legal-launch-checklist.md` — launch/legal checklist.
- `docs/product/seo-content.md` — consolidated SEO content, positioning and technical SEO baseline.
- `docs/product/seo-operations.md` — SEO production/deployment operations.
- `docs/product/ui-ux-audit.md` — UX audit/reference.

### Historical implementation records

- `docs/architecture/linguistic-validation-implementation.md` — historical implementation record; current workflow wiring belongs in live architecture documentation.

## Removed during this consolidation

- `docs/architecture/consistency-issue-contract-v2.md` — duplicate of the canonical consistency issue contract.

## Source-of-truth hierarchy

1. Executable code and tests define implemented behavior.
2. Database migrations define persisted schema history.
3. ADRs define architectural decisions and historical rationale.
4. Current architecture/workflow documentation explains implementation and must not contradict code.
5. Product documents define intent, scope and hypotheses; they are not implementation contracts unless explicitly labelled as such.

When a document says a capability is planned, search the current repository and tests before implementing it. Completed capabilities must not remain described as future work.

## Known reconciliation rules

- Production persistence is PostgreSQL/Cloud SQL. SQLite must not be described as the production persistence layer.
- Long-running analysis execution uses PostgreSQL `analysis_jobs` and a separate worker with transactional claiming and leases.
- Gemini is the current implemented LLM provider. Do not list OpenAI, Anthropic or Mistral as implemented providers without corresponding code.
- Stripe billing and workflow capacity controls are implemented; they must not remain described as future infrastructure.
- The Critical Eye is an implemented MVP capability, but its conversation is intentionally not persisted and it does not mutate Canon or manuscript content.
- Legal/commercial documents may still contain launch prerequisites and hypotheses; they must not be interpreted as proof of legal readiness or product-market fit.

## Consistency-specific ownership

- `ExtractChapterAssertions`: extraction/proposal of assertions from source material.
- `DetectConflicts`: persisted assertion-vs-assertion conflict detection.
- `CanonDiagnosticChecker`: new-text-vs-active-Canon diagnostics.
- `UnifiedConsistencyEngine`: detector composition and stable deduplication.
- `ConsistencyIssue`: author-facing consistency projection, not Canon truth.
- Canon promotion/review remains an explicit author decision.

The product principle is: **L’IA propose, l’auteur décide.**
