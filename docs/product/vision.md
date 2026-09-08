# Product Vision

## Strategic direction

Book Loop starts with a deliberately focused product: an **agentic narrative consistency workflow for authors**, expressed first as a book-writing and review loop. The book is the first domain in which we prove the underlying engine.

The broader category is **narrative consistency**: helping creators maintain a trusted, evolving Canon while AI and humans propose new content and revisions.

The initial target is authors. Screenwriters and Game Masters are adjacent validation targets, not three separate launch products. Documentation/company knowledge QA remains a later expansion hypothesis.

## Mission

Build an AI workflow that helps creators **keep their universe coherent as it grows and changes**.

AI agents can draft, analyze, critique and propose. Book Loop preserves the approved state, checks changes against it, exposes conflicts and lets the creator decide what becomes canonical.

## Core customer promise

> **Keep your universe coherent, even as it grows and changes.**

For authors:

> **Write with AI without losing the thread of your story.**

## Initial product — Agentic Book Loop

```text
Intent
  ↓
Context / existing Canon
  ↓
Outline
  ↓
Draft / proposal
  ↓
AI review
  ↓
Continuity / quality validation
  ↓
Human review & approval
  ↓
Canonical state
  ↓
Next chapter / revision
```

AI agents may analyze, critique, propose and draft. They must not silently mutate canonical state. Human approval remains the authority.

The important product property is the **loop**, not a particular model or prompt.

## Why start with books?

The book domain forces the engine to handle long-lived state, characters, facts, relationships, events, timelines, constraints, versions, revisions and explicit approval. The current MVP implements the core book loop, including bounded generation/review/correction, immutable versions, review history, approval gates and evidence-backed Canon primitives.

The book is therefore the **commercial wedge and proving ground**.

## Canon is the trust boundary

"Memory" is not enough. The product distinguishes information that was proposed from information that has been approved.

```text
Proposal
   ↓
Evidence / review
   ↓
Human decision
   ↓
Canon
   ↓
Future checks and creation
```

Canonical rules:

- generated or inferred information is proposed until explicitly approved;
- canonical facts retain provenance;
- conflicts remain explicit until reviewed;
- review decisions are auditable;
- rejected/deferred/transient material is not canonical continuity memory;
- Canon is never silently mutated by an LLM.

## Competitive position

Book Loop should compete above the model layer and above simple storage.

> **Other tools help you create or store the universe. Book Loop helps you change it without silently breaking it.**

The differentiation hypothesis is the combination of persistent Canon, evidence/provenance, review-before-mutation, continuity checks, version-aware workflows and eventual change-impact analysis.

## Adjacent creator validation

### Screenwriters

Validate continuity across scenes, drafts, characters, timelines and revisions. Do not initially compete with professional screenplay editors on formatting or general collaboration.

### Game Masters

Validate campaign Canon across sessions: NPCs, factions, locations, events, relationships, player decisions and consequences. Do not initially compete with campaign-management tools as a static wiki.

Both segments require product evidence before dedicated vertical features are built.

## Business model hypothesis

The initial business is a **creator SaaS**. Customers pay for a reliable narrative workflow and continuity protection, not for a particular LLM or raw token volume.

The current working commercial grid is:

| Plan | Monthly | Annual | Role |
|---|---:|---:|---|
| Free | €0 | — | Product discovery |
| Creator | €19 | €190 | Serious individual creator |
| Pro | €39 | €390 | Intensive creator / multiple projects |

Capacity limits are part of the commercial model. The product does not promise unlimited AI inference.

These are working prices for the current implementation, not validated product-market fit or a permanent commercial commitment. A higher-capacity tier can be tested later only if real usage provides evidence for it.

## Product principles

- **Sell coherence, not AI.**
- **Sell control, not automation theater.**
- **The loop is first-class.**
- **Canon is the source of truth.**
- **AI agents assist; they do not own state.**
- **Continuity and correctness are first-class.**
- **Deterministic rules stay deterministic.**
- **Every change is auditable.**
- **Explainability beats magic.**
- **Do not compete on raw generation volume.**
- **Do not require a new system of record prematurely.**
- **Use LLMs where semantic reasoning adds measurable value.**

## What we are explicitly not building now

- a generic one-shot AI writing assistant;
- a "generate my whole book" button as the core product;
- a simple lore/story-bible database;
- a static campaign wiki;
- a generic screenplay editor;
- three separate vertical SaaS products at launch;
- enterprise knowledge-management infrastructure before the creator product is validated.

## Success criteria

### Book wedge

- authors complete real chapters with the loop;
- AI review catches useful continuity/quality issues;
- proposed changes are understandable and controllable;
- canonical state remains trustworthy;
- users return for repeated review/drafting cycles;
- users perceive a meaningful advantage over a generic LLM workflow;
- willingness to pay is demonstrated.

### Expansion

Only after the Book loop demonstrates repeated value:

1. test the same consistency problem with GMs;
2. test the same problem with screenwriters;
3. identify which primitives transfer without product bloat;
4. build dedicated workflows only where evidence warrants them.

Documentation/company knowledge QA remains a separate expansion path requiring its own ICP, design partners and buying evidence.
