# Product Roadmap

This roadmap treats **narrative consistency** as the product direction and the **author/book workflow as the first commercial wedge**. Screenwriters and Game Masters are adjacent creator segments to validate after the Book loop proves repeated value.

## North star

Build an AI workflow that repeatedly **review → propose → validate → approve → update Canon**, so creators can use AI without losing control of an evolving narrative universe.

The strategic asset is not a generic writing assistant. It is the reusable engine that understands a long-lived narrative corpus, its claims, relationships, dependencies and approved state, and checks the effect of changes on that state.

## Current implementation status — September 2026

Implemented foundations include:

- structured book/outline/chapter domain model and explicit approval gates;
- bounded Writer → validation → Reviewer → Corrector → Summarizer chapter loop;
- deterministic chapter linting and linguistic validation;
- immutable chapter versions and persisted reviews;
- evidence-backed Canon assertions, conflicts, review decisions and canonical facts;
- durable chapter workflow runs in SQLite with checkpoints;
- idempotent chapter execution;
- restart recovery for persisted chapter versions;
- provider abstraction with Gemini as current implementation;
- deterministic/fake-based backend test strategy;
- frontend flows for project setup, Studio, chapters, characters, lore and Canon-related workflows.

Technical capability is not considered product validation. The remaining priority is proving that creators trust the loop and obtain repeated value from it.

## Product positioning

**Book Loop is a narrative consistency engine for creators who build complex, evolving universes.**

Core promise:

> **Keep your universe coherent, even as it grows and changes.**

Commercial wedge:

1. Authors / book projects.
2. Game Masters / RPG campaigns.
3. Screenwriters / screenplay or series continuity.

These are not three products at launch. They are three expressions of the same underlying narrative-state problem.

See [`positioning.md`](positioning.md) for the current product, competitive and business-model hypothesis.

## Phase 0 — Prove the Book wedge

**Goal:** prove that the agentic loop solves a painful continuity problem for real authors.

- [ ] Validate author intent capture and explicit constraints.
- [ ] Validate outline → draft workflow.
- [ ] Validate AI review / critique usefulness.
- [ ] Validate continuity checks against Canon.
- [ ] Validate explicit human approval gates.
- [ ] Validate canonical state updates after approval.
- [ ] Complete the end-to-end Studio loop for real projects.
- [ ] Observe repeated use across multiple chapters and revisions.
- [ ] Compare the workflow with a generic LLM + notes workflow.
- [ ] Validate willingness to pay.

**Exit criterion:** real authors repeatedly use the loop, trust the findings/Canon, and perceive a meaningful advantage over their current workflow.

## Phase 1 — Excellent agentic Book Loop

**Goal:** make the first product compelling without becoming a generic writing suite.

### Agentic workflow

- [x] Intent / creative brief capture foundations.
- [x] Context and research ingestion where useful.
- [x] Outline proposal and approval.
- [x] Chapter drafting as bounded agent proposals.
- [x] AI review with structured findings.
- [x] Continuity / quality validation foundations.
- [x] Revision proposals.
- [ ] Human approval of generated chapter revisions as a complete UX flow.
- [x] Canonical state update foundations.
- [ ] Repeatable next-chapter / revision loop validated through the full UI.

### Book intelligence

- [ ] Characters.
- [ ] Lore / world rules.
- [ ] Relationships.
- [ ] Timeline and events.
- [x] Chapter versions.
- [x] Provenance and review history.
- [x] Canonical summaries.
- [x] Deterministic validation where possible.

**Exit criterion:** the product's main advantage over a generic LLM is its persistent, review-driven loop and trusted narrative Canon.

## Phase 2 — Narrative Canon primitives

**Goal:** generalize the underlying state model without prematurely changing the Book UX.

- [ ] Define domain-neutral narrative entity model.
- [x] Define canonical claims / facts.
- [ ] Model relationships and dependencies.
- [ ] Model events and temporal assertions.
- [ ] Model rules / constraints.
- [x] Attach provenance and confidence to claims.
- [x] Track versions and approval decisions.
- [x] Link claims to source content.
- [ ] Separate domain-specific presentation from the underlying engine.

The current Canon implementation is deliberately book-focused. Generalization should be driven by evidence from adjacent creator workflows.

**Exit criterion:** book continuity can be expressed with reusable narrative primitives without degrading the author experience.

## Phase 3 — Change impact / narrative regression engine

**Goal:** turn continuity into an explicit change-analysis capability.

- [ ] `What breaks if I change this?`.
- [ ] Find content affected by a changed claim.
- [ ] Detect stale assertions.
- [x] Detect contradictory assertions.
- [ ] Track dependency chains.
- [ ] Add temporal consistency checks.
- [ ] Add entity state checks.
- [ ] Produce evidence-backed regression reports.
- [ ] Re-run analysis after proposed fixes.

For books this is narrative continuity. The same mechanism should later be testable on campaigns and screenplays.

## Phase 4 — Game Master / RPG validation

**Goal:** test whether the same Canon and change-review engine creates strong value for persistent tabletop RPG campaigns.

Target ICP: GMs running campaigns with enough accumulated NPCs, factions, locations, events, relationships and player decisions that manual continuity becomes difficult.

- [ ] Interview GMs about campaign continuity pain.
- [ ] Test Canon on real campaign notes.
- [ ] Model session events and player decisions.
- [ ] Test NPC / faction / location state changes.
- [ ] Test contradiction and temporal checks across sessions.
- [ ] Measure time saved versus existing notes/wiki tools.
- [ ] Obtain strong repeated-use signal before building dedicated UX.

**Decision gate:** only build dedicated GM features if the same core consistency problem is frequent, painful and valuable enough to support recurring use.

## Phase 5 — Screenwriter validation

**Goal:** test whether the narrative consistency engine transfers to screenplay and series workflows.

Target ICP: individual screenwriters or small creative teams managing evolving scripts, drafts, characters, scenes and timelines.

- [ ] Interview screenwriters about continuity/revision pain.
- [ ] Test screenplay/series Canon representation.
- [ ] Test scene-level change impact.
- [ ] Test character/timeline regressions.
- [ ] Compare with existing screenplay editors and generic LLM workflows.
- [ ] Obtain repeated-use / buying signal.

**Principle:** complement professional screenplay editors before attempting to replace them.

## Phase 6 — Creator integrations

**Goal:** become a consistency layer around creators' existing sources rather than forcing migration.

Prioritize only from observed demand:

- [ ] Markdown / text / structured files.
- [ ] Import/export of existing story or campaign knowledge.
- [ ] Git / GitHub where relevant to creative workflows.
- [ ] Notion / Confluence only if creator research demonstrates demand.
- [ ] API / webhooks.

**Principle:** integrate with existing sources of truth before becoming a system of record for every creator workflow.

## Phase 7 — Creator SaaS maturity

**Goal:** turn validated creator value into a sustainable subscription product.

- [ ] Production billing.
- [ ] Usage controls and quotas.
- [ ] Subscription lifecycle.
- [ ] Multi-project support.
- [ ] Collaboration where users demand it.
- [ ] Review queues and shared decisions.
- [ ] Export/publishing workflows.
- [ ] Clear plan boundaries based on real usage.

Pricing should remain simple and outcome-oriented. See [`pricing-strategy.md`](pricing-strategy.md).

## Phase 8 — Documentation / company knowledge QA experiment

**Goal:** test the original long-term hypothesis that the Canon/change-regression engine also applies to non-fiction organizational knowledge.

This phase is intentionally **after creator-market validation**. It is not the current product positioning.

- [ ] Identify documentation-heavy design partners.
- [ ] Map real sources and change workflows.
- [ ] Identify costly knowledge regressions.
- [ ] Reuse narrative claim/dependency primitives.
- [ ] Prove that the same engine catches meaningful regressions.
- [ ] Obtain a paid pilot before building a B2B product.

Potential future positioning:

> **Documentation QA: test knowledge changes before they become company-wide misinformation.**

If the problem does not demonstrate sufficient pain, frequency and willingness to pay, stop expansion.

## Phase 9 — Agentic resolution / knowledge infrastructure

Only after repeated commercial evidence:

- [ ] Agent investigation of detected regressions.
- [ ] Proposed minimal fixes.
- [ ] Re-validation after fixes.
- [ ] API / webhooks.
- [ ] Multi-user governance.
- [ ] Audit logs.
- [ ] Enterprise access controls.
- [ ] SSO / security / compliance.
- [ ] Private deployment where justified.

## LLM strategy

The LLM layer is an enabling capability, not the product moat. Model quality and pricing will change; the Canon, provenance, evidence, approval history and regression logic should remain provider-independent.

Current provider abstraction:

```text
LLMProvider
├── GeminiProvider
├── OpenAIProvider
├── AnthropicProvider
└── MistralProvider
```

Keep Gemini as the initial implementation. Add providers only when representative benchmarks show a meaningful quality, cost or latency advantage.

Do not make model choice the primary marketing message.

## Deferred / explicitly deprioritized

- [ ] Competing directly with generic AI writing assistants on generation volume.
- [ ] Building a simple lore/wiki product.
- [ ] Replacing professional screenplay editors.
- [ ] Replacing established RPG campaign-management tools as static systems of record.
- [ ] Building three separate vertical products before validating the common problem.
- [ ] Documentation/company knowledge SaaS before creator-market evidence.
- [ ] Large-scale vector/RAG infrastructure before a measured retrieval bottleneck.
- [ ] Enterprise infrastructure before product-market evidence.
- [ ] Metrics/observability work that does not directly support current product reliability or economics.

## Existing technical assets to preserve

- explicit application use cases;
- replaceable LLM providers;
- approval gates;
- chapter versions and review decisions;
- canonical summaries;
- bounded retries;
- persistence and history;
- lore / character / outline workflows;
- validation and linting;
- durable workflow checkpoints and idempotency.

## Decision gates

Every expansion must answer:

1. **Value:** does the loop solve a painful continuity problem?
2. **Trust:** do users trust the Canon and evidence?
3. **Frequency:** does the workflow recur often enough for SaaS retention?
4. **Differentiation:** is the advantage meaningful versus a generic LLM plus existing tools?
5. **Willingness to pay:** does the outcome justify payment?
6. **Economics:** can the workflow maintain healthy margins?

If a gate fails, revisit the problem/ICP before adding product or platform complexity.
