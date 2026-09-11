# Product Roadmap

This roadmap treats **narrative consistency** as the product direction and the **author/book workflow as the first commercial wedge**. Screenwriters and Game Masters are adjacent creator segments to validate only after the Book loop proves repeated value.

## North star

Build an AI workflow that repeatedly **review → propose → validate → approve → update Canon**, so creators can use AI without losing control of an evolving narrative universe.

## Current implementation status — September 2026

The current product already includes:

- structured book/outline/chapter domain models and approval gates;
- bounded Writer → validation → Reviewer → Corrector → Summarizer chapter workflow;
- deterministic and linguistic validation;
- immutable chapter versions and persisted reviews;
- evidence-backed Canon assertions, conflicts, review decisions and canonical facts;
- narrative events, temporal relations and entity-state foundations;
- durable chapter workflow execution state and recovery in production PostgreSQL;
- PostgreSQL-backed asynchronous analysis jobs with a dedicated worker, leases and recovery;
- idempotent chapter execution;
- Gemini as the current LLM implementation behind a provider abstraction;
- deterministic/fake-based backend tests;
- frontend flows covering project setup, Studio, chapters, characters, lore and Canon/review workflows;
- Critical Eye / Œil critique MVP for narrative sparring;
- Stripe billing and capacity controls.

Technical capability is not product validation. The immediate product priority is evidence from real creators.

## Phase 0 — Prove the Book wedge

**Goal:** prove that the loop solves a painful continuity problem for real authors.

- [ ] Validate author intent capture and explicit constraints.
- [ ] Validate outline → draft workflow.
- [ ] Validate AI review / critique usefulness, including the Critical Eye.
- [ ] Validate continuity checks against Canon.
- [ ] Validate explicit human approval gates.
- [ ] Validate canonical state updates after approval.
- [x] Complete the end-to-end Studio loop for real projects at the application/E2E level.
- [ ] Observe repeated use across multiple chapters and revisions with real authors.
- [ ] Compare the workflow with a generic LLM + notes workflow.
- [ ] Validate willingness to pay.

**Exit criterion:** real authors repeatedly use the loop, trust the findings/Canon, and perceive a meaningful advantage over their current workflow.

## Phase 1 — Excellent agentic Book Loop

**Goal:** make the first product compelling without becoming a generic writing suite.

### Agentic workflow

- [x] Intent / creative brief foundations.
- [x] Context and research ingestion where implemented.
- [x] Outline proposal and approval.
- [x] Chapter drafting as bounded agent proposals.
- [x] AI review with structured findings.
- [x] Continuity / quality validation foundations.
- [x] Revision proposal foundations.
- [x] Human approval of generated chapter revisions as an application/UI decision loop.
- [x] Canonical state update foundations.
- [x] Multi-chapter author loop covered by E2E tests.
- [x] Critical Eye narrative sparring MVP.
- [x] Long-running analysis execution decoupled from HTTP requests.

### Book intelligence

- [x] Characters.
- [x] Lore / world rules.
- [x] Chapter versions.
- [x] Provenance and review history.
- [x] Canonical summaries.
- [x] Deterministic validation where possible.
- [x] Narrative event / temporal / entity-state foundations.
- [ ] Richer relationships and timeline intelligence.

**Exit criterion:** the product's main advantage over a generic LLM is its persistent, review-driven loop and trusted narrative Canon, demonstrated by real users.

## Phase 2 — Narrative Canon primitives

**Goal:** generalize the underlying state model without prematurely changing the Book UX.

- [x] Define initial domain narrative state primitives.
- [x] Canonical claims / facts.
- [x] Initial relationship and dependency structures.
- [x] Model events and temporal assertions foundations.
- [ ] Model rules / constraints as a first-class narrative subsystem.
- [x] Provenance and confidence on claims.
- [x] Versions and approval decisions.
- [x] Link claims to source content.
- [ ] Separate domain-specific presentation from the underlying engine.

Generalization should be driven by evidence from adjacent creator workflows.

## Phase 3 — Change impact / narrative regression engine

**Goal:** turn continuity into explicit change analysis.

- [x] Detect contradictory assertions.
- [x] Initial change-impact analysis foundations.
- [x] Initial temporal consistency checks.
- [x] Initial entity-state checks.
- [ ] Answer `What breaks if I change this?` end-to-end in the author workflow.
- [ ] Find content affected by a changed claim.
- [ ] Detect stale assertions.
- [ ] Track dependency chains comprehensively.
- [ ] Produce evidence-backed regression reports end-to-end.
- [ ] Re-run analysis after proposed fixes.

The checked items above represent technical foundations already present; they are not evidence that the complete product experience is validated.

## Phase 4 — Game Master / RPG validation

Validate campaign continuity with real GMs before building dedicated UX.

- [ ] Interview GMs about campaign continuity pain.
- [ ] Test Canon on real campaign notes.
- [ ] Model session events and player decisions.
- [ ] Test NPC / faction / location state changes.
- [ ] Test contradiction and temporal checks across sessions.
- [ ] Measure time saved versus existing tools.
- [ ] Obtain repeated-use and buying signal.

## Phase 5 — Screenwriter validation

Validate continuity across screenplay/series scenes, drafts, characters and timelines before building dedicated workflows.

- [ ] Interview screenwriters.
- [ ] Test screenplay/series Canon representation.
- [ ] Test scene-level change impact.
- [ ] Test character/timeline regressions.
- [ ] Compare with existing screenplay editors and generic LLM workflows.
- [ ] Obtain repeated-use / buying signal.

## Phase 6 — Creator integrations

Prioritize only from observed demand:

- [ ] Markdown / text / structured files.
- [x] Git / GitHub import foundations.
- [ ] Import/export of existing story or campaign knowledge beyond current imports.
- [ ] Notion / Confluence only if research demonstrates demand.
- [ ] API / webhooks.

## Phase 7 — Creator SaaS maturity

Stripe billing and capacity controls are already implemented; this phase now concerns **maturing and validating** the commercial system rather than first implementation.

- [x] Production billing foundations.
- [x] Usage controls and workflow capacity.
- [x] Subscription checkout / lifecycle foundations.
- [ ] Measure real plan usage and margins.
- [ ] Tune plan boundaries from evidence.
- [ ] Multi-project experience beyond current plan limits where evidence warrants it.
- [ ] Collaboration where users demand it.
- [ ] Export/publishing workflows.

## Phase 8 — Documentation / company knowledge QA experiment

Only after creator-market validation:

- [ ] Identify documentation-heavy design partners.
- [ ] Map real sources and change workflows.
- [ ] Identify costly knowledge regressions.
- [ ] Reuse claim/dependency/approval primitives.
- [ ] Prove meaningful regression detection.
- [ ] Obtain a paid pilot before building a B2B product.

## Phase 9 — Agentic resolution / knowledge infrastructure

Only after repeated commercial evidence:

- [ ] Agent investigation of detected regressions.
- [ ] Proposed minimal fixes.
- [ ] Re-validation after fixes.
- [ ] Multi-user governance.
- [ ] Audit logs.
- [ ] Enterprise access controls.
- [ ] SSO / security / compliance.
- [ ] Private deployment where justified.

## LLM strategy

The LLM layer is an enabling capability, not the product moat. **Gemini is the current implementation.** The provider abstraction should remain provider-independent, but additional providers should be added only when representative benchmarks demonstrate a meaningful quality, cost or latency advantage.

Do not document OpenAI, Anthropic or Mistral as implemented providers unless the corresponding code exists.

## Deferred / explicitly deprioritized

- Competing with generic AI writing assistants on generation volume.
- Building a simple lore/wiki product.
- Replacing professional screenplay editors.
- Replacing established RPG campaign-management tools as static systems of record.
- Building separate vertical products before validating the common problem.
- Documentation/company knowledge SaaS before creator-market evidence.
- Large-scale vector/RAG infrastructure before a measured retrieval bottleneck.
- Enterprise infrastructure before product-market evidence.

## Decision gates

Every expansion must answer:

1. **Value:** does the loop solve a painful continuity problem?
2. **Trust:** do users trust the Canon and evidence?
3. **Frequency:** does the workflow recur often enough for retention?
4. **Differentiation:** is the advantage meaningful versus a generic LLM plus existing tools?
5. **Willingness to pay:** does the outcome justify payment?
6. **Economics:** can the workflow maintain healthy margins?

If a gate fails, revisit the problem/ICP before adding product or platform complexity.
