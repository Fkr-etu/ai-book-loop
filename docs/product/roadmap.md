# Product Roadmap

This roadmap keeps the **agentic book loop** as the first product and treats broader documentation / company knowledge QA as a deliberate expansion of the same underlying engine.

## North star

Build an AI agentic workflow that can repeatedly **review → propose → validate → approve → update canonical state**, first for books and later for other high-value documentation.

The strategic asset is not a generic writing assistant. It is the reusable engine that understands a long-lived corpus, its claims and dependencies, and the effect of changes on that corpus.

## Phase 0 — Book product validation

**Goal:** prove that the agentic loop is genuinely useful for real book creation/revision.

- [ ] Validate author intent capture and project constraints.
- [ ] Validate outline → draft workflow.
- [ ] Validate AI review / critique.
- [ ] Validate continuity checks against canonical state.
- [ ] Validate explicit human approval gates.
- [ ] Validate canonical summaries / state updates after approval.
- [ ] Observe repeated use across multiple chapters and revisions.
- [ ] Measure where the loop saves time versus a generic LLM workflow.

**Exit criterion:** real users repeatedly use the loop and trust its reviews/canonical state enough to continue a project through multiple iterations.

## Phase 1 — Excellent agentic book loop

**Goal:** make the first product compelling without turning it into a generic writing suite.

### Agentic workflow

- [ ] Intent / creative brief capture.
- [ ] Context and research ingestion where useful.
- [ ] Outline proposal and approval.
- [ ] Chapter drafting as bounded agent proposals.
- [ ] AI review with structured findings.
- [ ] Continuity / quality validation.
- [ ] Revision proposals.
- [ ] Human approval.
- [ ] Canonical state update.
- [ ] Repeatable next-chapter / revision loop.

### Book intelligence

- [ ] Characters.
- [ ] Lore / world rules.
- [ ] Relationships.
- [Timeline and events.
- [ ] Chapter versions.
- [ ] Provenance and review history.
- [ ] Canonical summaries.
- [ ] Deterministic validation where possible.

**Exit criterion:** the product's main advantage over a generic LLM is the persistent, agentic, review-driven loop and its ability to maintain book coherence.

## Phase 2 — Generalize the underlying knowledge model

**Goal:** extract reusable primitives without prematurely changing the book UX.

- [ ] Define a domain-neutral entity model.
- [ ] Define canonical claims / facts.
- [ ] Model relationships and dependencies.
- [ ] Model events and temporal assertions.
- [ ] Model rules / constraints.
- [ ] Attach provenance and confidence to claims.
- [ ] Track versions and approval decisions.
- [ ] Link claims to source content.
- [ ] Separate domain-specific presentation from the underlying engine.

Example:

```text
Book:
  "Sarah learns the truth in chapter 18."

Company documentation:
  "API v3 requires OAuth 2.0."

Both become:
  canonical claim + source + validity + dependencies + review history
```

**Exit criterion:** book continuity logic can be expressed using the generalized model without degrading the book product.

## Phase 3 — Change impact / regression engine

**Goal:** make the engine answer the consequences of change.

- [ ] `What breaks if I change this?`.
- [ ] Find content affected by a changed claim.
- [ ] Detect stale assertions.
- [ ] Detect contradictory assertions.
- [ ] Track dependency chains.
- [ ] Add temporal consistency checks.
- [ ] Add entity state / knowledge checks.
- [ ] Produce evidence-backed regression reports.
- [ ] Re-run analysis after proposed fixes.

For books, this is narrative continuity. The same mechanism will later power documentation regression testing.

## Phase 4 — Documentation QA design partners

**Goal:** test whether the book-derived engine solves a valuable problem outside fiction.

Initial ICP hypothesis: software / B2B SaaS companies with substantial, frequently changing documentation and multiple contributors.

- [ ] Interview at least 10 documentation-heavy teams.
- [ ] Map current sources: Git, Notion, Confluence, docs, wiki, support, etc.
- [ ] Identify costly documentation regressions.
- [ ] Identify existing review / release gates.
- [ ] Recruit at least 3 design partners.
- [ ] Run the engine on real corpora.
- [ ] Obtain at least 1 paid pilot or equivalent strong buying signal.
- [ ] Measure time saved / regressions avoided.

**Critical falsification question:**

> Do documentation inconsistencies cost enough, happen often enough, and occur early enough that companies will pay for automated knowledge regression testing?

If not, stop expansion and revisit the ICP/problem.

## Phase 5 — Documentation regression MVP

**Goal:** productize the generalized loop for company documentation.

```text
Source documents
      ↓
Claim extraction
      ↓
Canonical knowledge
      ↓
New / changed content
      ↓
Regression analysis
      ↓
Findings + evidence
      ↓
Human review
      ↓
Approved knowledge
```

- [ ] Documentation corpus ingestion.
- [ ] Claim extraction and provenance.
- [ ] Canonical knowledge approval.
- [ ] New-content checks.
- [ ] Contradiction detection.
- [ ] Stale-content detection.
- [ ] Evidence-backed findings.
- [ ] Human approval.
- [ ] Knowledge health / regression report.

## Phase 6 — Integrate with existing company workflow

**Goal:** become a QA layer rather than another documentation editor.

Prioritize based on design-partner demand:

- [ ] Git / GitHub repositories.
- [ ] Markdown / JSON / CSV.
- [ ] Notion / Confluence.
- [ ] Google Docs and similar document sources.
- [ ] Help center / support content.
- [ ] API and webhooks.
- [ ] CI checks for documentation changes.
- [ ] Slack / issue tracker notifications.

**Principle:** do not require migration from the customer's existing source of truth.

## Phase 7 — General knowledge QA SaaS

**Goal:** turn the engine into a recurring B2B product.

- [ ] Multi-user workspaces.
- [ ] Roles and permissions.
- [ ] Review queues.
- [ ] Issue assignment.
- [ ] Comments and decisions.
- [ ] Audit logs.
- [ ] Knowledge-health metrics.
- [ ] Scheduled / event-driven checks.
- [ ] Usage controls and quotas.
- [ ] Team / workspace billing.

Potential positioning:

> **Documentation QA: test knowledge changes before they become company-wide misinformation.**

## Phase 8 — Agentic resolution

**Goal:** generalize the book-writing agent loop into a documentation repair loop.

```text
Regression
   ↓
Agent investigation
   ↓
Proposed fix
   ↓
Validation
   ↓
Human approval
   ↓
Updated content / knowledge
```

- [ ] Suggest minimal documentation edits.
- [ ] Generate alternative resolutions.
- [ ] Explain trade-offs.
- [ ] Propose updates to affected documents.
- [ ] Re-run regression checks.
- [ ] Summarize approved changes.

The book product remains the reference implementation for this agentic pattern.

## Phase 9 — Enterprise / knowledge infrastructure

Only after repeated commercial evidence:

- [ ] SSO / SAML.
- [ ] Advanced access controls.
- [ ] Security / compliance documentation.
- [ ] Retention and deletion controls.
- [ ] API / service accounts.
- [ ] Private deployment where justified.
- [ ] SLA / enterprise support.
- [ ] Knowledge QA API.

The long-term hypothesis is that the engine can become a **knowledge consistency layer** consumed by multiple applications, not merely a standalone documentation UI.

## Deferred / explicitly deprioritized

- [ ] Competing directly with generic AI writing assistants.
- [ ] Replacing Notion, Confluence, Articy, or other systems of record.
- [ ] Building a full enterprise knowledge-management suite before QA value is proven.
- [ ] Broad game-specific expansion unrelated to the core loop.
- [ ] Large-scale vector-memory infrastructure before a measured retrieval bottleneck exists.
- [ ] Enterprise infrastructure before product-market evidence.

## Existing technical assets to preserve

The current project already contains foundations that map naturally to this roadmap:

- explicit application use cases;
- replaceable LLM providers;
- approval gates;
- chapter versions and review decisions;
- canonical summaries for continuity;
- bounded retries;
- persistence and history;
- lore / character / outline workflows;
- validation and linting.

The strategy is to **prove the loop first, extract the reusable knowledge primitives second, and only then expand the market**.

## Decision gates

Every expansion must answer:

1. **Value:** does the loop solve a painful problem?
2. **Trust:** do users trust the canonical state and evidence?
3. **Frequency:** does the workflow recur often enough to support SaaS retention?
4. **Integration:** can it fit the existing source-of-truth workflow?
5. **Willingness to pay:** does the outcome justify payment independently of token consumption?

If a gate fails, revisit the problem/ICP before adding platform complexity.
