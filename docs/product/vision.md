# Product Vision

## Strategic direction

Book Loop starts with a deliberately focused product: an **agentic narrative consistency workflow for authors**, expressed first as a book-writing and review loop. The book is the first concrete domain in which we prove the underlying engine.

The broader product category is **narrative consistency**: helping creators maintain a trusted, evolving Canon while AI and humans propose new content and revisions.

The initial target is authors. The same underlying primitives can later serve **screenwriters** and **Game Masters (GM) running tabletop RPG campaigns**, because all three manage long-lived narrative universes whose facts, relationships, events and constraints evolve over time.

The strategic progression is intentional:

```text
AUTHOR / BOOK WEDGE
Review → propose → validate → approve → canonical state
                    ↓
          generalized narrative model
              ↙              ↘
      SCREENWRITING          RPG / GM
```

A later, separately validated opportunity remains documentation / company knowledge QA. That is an expansion hypothesis, not the current product positioning.

## Mission

Build an AI workflow that helps creators **keep their universe coherent as it grows and changes**.

AI agents can draft, analyze, critique and propose. Book Loop preserves the approved state, checks changes against it, exposes conflicts and lets the creator decide what becomes canonical.

## Core customer promise

> **Keep your universe coherent, even as it grows and changes.**

For authors:

> **Write with AI without losing the thread of your story.**

For screenwriters:

> **Evolve your script without breaking continuity.**

For Game Masters:

> **Run an evolving campaign without losing the memory of your world.**

These are expressions of one product promise, not three separate products.

## The problem

Generative AI is good at producing plausible local content. The difficult problem appears after repeated creation and revision.

A long-lived narrative accumulates characters, facts, relationships, locations, events, timelines, rules, constraints, versions and decisions. New content can contradict earlier content without the creator noticing.

A generic chat can generate. A wiki or story bible can store. **Book Loop is intended to check change against trusted state before that change silently becomes truth.**

## Initial product — Agentic Book Loop

The product helps an author or small writing project move through a controlled loop:

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

The book domain forces the engine to solve the hard version of the problem:

- long context and evolving state;
- characters, facts, relationships, events and timelines;
- continuity across many chapters;
- explicit author intent and constraints;
- iterative generation rather than one-shot prompting;
- human approval of proposed changes;
- a canonical state that evolves over time.

The current MVP already implements the core book loop, including bounded generation/review/correction, immutable versions, review history, approval gates and evidence-backed Canon primitives.

The book is therefore the **commercial wedge and proving ground**, not a disposable prototype or a marketing pretext.

## The underlying narrative abstraction

The reusable abstraction is a trusted, evidence-backed state of an evolving narrative universe.

A useful canonical model includes:

- entities: characters, locations, factions, concepts and other narrative objects;
- claims/facts;
- relationships;
- events and temporal assertions;
- rules and constraints;
- source content;
- versions;
- provenance;
- confidence;
- review decisions;
- dependencies between claims and content.

For a book, an assertion may be:

> Sarah learns the truth in chapter 18.

For an RPG campaign, it may be:

> The Ashen Court controls the northern pass after session 12.

For a screenplay, it may be:

> The protagonist has not yet met the detective before scene 47.

The domain differs; the underlying problem is the same: **a claim whose validity can affect other content**.

## Canon is the trust boundary

"Memory" is not enough. The product must distinguish information that was proposed from information that has been approved.

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

This distinction is central to user trust and is a core product differentiator.

## Competitive position

Book Loop should compete **above the model layer** and **above simple storage**.

AI writing assistants compete on generation, ideation and writing assistance. Worldbuilding/campaign tools compete on structured storage of universes. Professional writing tools compete on authoring, formatting and collaboration.

Book Loop's intended distinction is:

> **Other tools help you create or store the universe. Book Loop helps you change it without silently breaking it.**

The moat hypothesis is therefore the combination of persistent Canon, evidence/provenance, review-before-mutation, continuity checks, version-aware workflows and eventual change-impact analysis.

## Screenwriting and RPG expansion

The next potential adjacent segments are deliberately chosen because they share the same narrative state problem.

### Screenwriters

Focus on continuity across scenes, drafts, characters, timelines and revisions. Do not initially compete with professional screenplay editors on formatting or general collaboration.

### Game Masters

Focus on campaign Canon across sessions: NPCs, factions, locations, events, relationships, player decisions and consequences. Do not initially compete with campaign-management tools as a static wiki.

Both segments require product evidence before dedicated vertical features are built.

## Later opportunity — Knowledge QA

A separate long-term opportunity remains documentation and company knowledge QA. It reuses the broader claim/dependency/approval engine but should not drive the current creator product positioning.

```text
Existing docs / knowledge sources
                    ↓
              knowledge engine
                    ↓
       claims / dependencies / state
                    ↓
          review & regression QA
```

The transition should happen only after the narrative product has demonstrated repeated value and the same consistency problem is validated in a new market.

## Business model hypothesis

The initial business is a **creator SaaS**. Customers pay for a reliable narrative workflow and continuity protection, not for a particular LLM or raw token volume.

The customer-facing commercial abstraction should remain understandable:

- active books / projects / campaigns;
- workflow capacity;
- continuity/review capacity;
- later, collaboration and professional capabilities.

Internal token and model usage can still be metered for cost control, but tokens should not be the product's primary value proposition.

Pricing is deliberately a hypothesis. The current working structure is Free → Creator/Pro → later higher-capacity tier, with approximate €12 / €24 / €49 anchors to validate rather than promises to publish.

## Product principles

- **Sell coherence, not AI.**
- **Sell control, not automation theater.**
- **The loop is first-class.** Review, propose, validate, approve and update state are core primitives.
- **Canon is the source of truth.** Generated or inferred content is not canonical until approved.
- **AI agents assist; they do not own state.**
- **Continuity and correctness are first-class.** Model dependencies rather than relying only on prompt context.
- **Deterministic rules stay deterministic.**
- **Every change is auditable.** Preserve versions, provenance and review decisions.
- **Explainability beats magic.** A finding should expose its supporting claims and affected content.
- **Do not compete on raw generation volume.**
- **Do not require a new system of record prematurely.** Integrate with existing creative workflows where useful.
- **Cost-consciousness matters.** Use LLMs where semantic reasoning adds value; avoid unnecessary calls.

## What we are explicitly not building

- a generic one-shot AI writing assistant;
- a "generate my whole book" button as the core product;
- a simple lore / story-bible database;
- a static campaign wiki;
- a generic screenplay editor;
- a product whose moat is a proprietary prompt;
- three separate vertical SaaS products at launch;
- enterprise knowledge-management infrastructure before the creator product is validated.

## Success criteria

### Book wedge

- authors complete real chapters with the agentic loop;
- AI review catches useful continuity/quality issues;
- proposed changes are understandable and controllable;
- canonical state remains trustworthy;
- users return for repeated review/drafting cycles;
- users perceive a meaningful advantage over a generic LLM workflow;
- willingness to pay is demonstrated.

### Adjacent creator validation

Only after the book loop demonstrates repeated value:

1. test the same consistency problem with GMs;
2. test the same problem with screenwriters;
3. identify which primitives transfer without product bloat;
4. build dedicated workflows only where user evidence warrants them.

### Long-term expansion

Documentation / company knowledge QA remains a separate expansion path. It requires its own ICP, design partners and buying evidence before implementation becomes a priority.
