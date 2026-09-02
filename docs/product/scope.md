# Scope

This scope keeps the **agentic book loop** as the first product. The goal is to make the loop excellent and commercially useful before generalizing its underlying knowledge/continuity logic to company documentation.

## Phase 1 — Agentic book loop (first product)

- Create a book project.
- Capture author intent and project constraints.
- Build and approve an outline.
- Maintain characters, lore, relationships, timeline, and other canonical context.
- Draft chapters through bounded AI proposals.
- Run AI review / critique on proposed or edited chapters.
- Run continuity and quality validation against canonical state.
- Present findings with supporting evidence.
- Let the author approve, reject, or request a revision.
- Update canonical state only after approval.
- Preserve chapter versions, review decisions, and canonical history.
- Repeat the loop for the next chapter or revision.

### Core loop

```text
Intent
  ↓
Context / research
  ↓
Outline
  ↓
Draft
  ↓
AI review
  ↓
Validation
  ↓
Human approval
  ↓
Canonical state
  ↓
Next iteration
```

The agent should be able to operate repeatedly inside this loop, but bounded workflows and explicit approval gates remain mandatory.

## Phase 2 — Generalized canon / knowledge engine

Extract reusable domain primitives from the book workflow:

- canonical entities;
- claims / facts;
- relationships;
- events and temporal assertions;
- rules / constraints;
- source documents;
- versions;
- provenance;
- confidence;
- review decisions;
- dependencies between claims and content.

The abstraction must support both book concepts and future business documentation concepts without forcing the book UI to become generic prematurely.

## Phase 3 — Change impact and regression analysis

- `What breaks if I change this?` impact analysis.
- Detect stale claims and content.
- Identify downstream documents affected by a changed claim.
- Timeline / temporal consistency checks.
- Entity state and knowledge checks.
- Compare proposed content against the approved knowledge state.
- Produce evidence-backed regression reports.

For books, this means continuity across chapters. For documentation, it can mean identifying outdated product/API/support information after a change.

## Phase 4 — Documentation / company knowledge pilot

Only after the book loop has demonstrated repeated value:

- Import documentation corpora.
- Extract canonical claims from technical/product/internal documentation.
- Check new or edited documentation against approved knowledge.
- Detect contradictions and stale references.
- Review and approve canonical updates.
- Measure avoided or reduced documentation regressions.

Initial target: software / B2B SaaS companies with frequently changing documentation and multiple contributors.

## Phase 5 — Existing-stack integrations

The documentation product should sit above existing systems rather than require migration.

Prioritize according to design-partner demand:

- Git repositories;
- Markdown / JSON / CSV;
- Notion / Confluence or equivalent wiki sources;
- Google Docs / document sources;
- help-center / support content;
- API and webhooks;
- CI checks on documentation changes.

## Phase 6 — Knowledge QA SaaS

- Multi-user projects.
- Roles and permissions.
- Review queues.
- Issue assignment.
- Comments and decisions.
- Notifications.
- Knowledge-health metrics.
- Audit logs.
- Change requests.
- Scheduled or event-driven regression checks.

Potential commercial proposition:

> **Documentation QA: check every meaningful content change against the company's current knowledge state.**

## Phase 7 — Assisted resolution

The same agentic loop used for books becomes a general resolution workflow:

```text
Issue
  ↓
Agent analysis
  ↓
Proposed fix
  ↓
Validation
  ↓
Human review
  ↓
Approved change
  ↓
Canonical state
```

Capabilities may include:

- suggest minimal edits;
- generate alternative resolutions;
- explain trade-offs;
- update affected content proposals;
- re-run regression checks;
- summarize the approved change.

## Explicitly out of scope for now

- Generic AI writing assistant without a review/validation loop.
- Replacing established authoring or documentation systems.
- Building a complete Notion/Confluence competitor.
- Broad enterprise knowledge management before documentation QA is validated.
- Large transmedia/game-specific feature expansion before the core loop proves value.
- Enterprise infrastructure before commercial evidence exists.

## Product validation gates

### Book gate

Before broadening the product:

- real users complete repeated book-review/drafting cycles;
- users report that agentic review catches useful issues;
- approval gates prevent unwanted canonical mutations;
- canonical context remains trustworthy as the manuscript grows;
- users return because the loop is materially better than a one-shot LLM workflow.

### Documentation gate

Before broadening into company knowledge:

- interview at least 10 documentation-heavy teams;
- identify recurring, costly documentation regressions;
- onboard at least 3 design partners with real corpora;
- obtain at least 1 paid pilot or equivalent buying signal;
- measure time saved or regressions avoided.
