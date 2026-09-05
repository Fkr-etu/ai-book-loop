# Product Positioning & Business Model

## Purpose

This document is the product and commercial source of truth for the current Book Loop positioning. It translates the existing product vision, MVP scope, roadmap and competitive research into a clear market hypothesis.

It is a hypothesis to validate with users, not a claim that product-market fit or pricing has already been proven.

## Executive positioning

**Book Loop is a narrative consistency engine for creators who build complex, evolving universes.**

The first product is an author-focused writing workspace. The same underlying engine can later serve screenwriters and Game Masters (GM) running tabletop role-playing campaigns.

The product promise is not simply that AI can generate text. It is that the creator can use AI **without losing control of what is true in the universe**.

### Core promise

> **Keep your universe coherent, even as it grows and changes.**

### Product explanation

> Book Loop remembers the approved state of your story or universe, checks new proposals against it, surfaces contradictions and quality issues, and asks you to decide what becomes canon.

### Author-facing message

> **Write with AI without losing the thread of your story.**

### Screenwriter-facing message

> **Evolve your script without breaking continuity.**

### GM-facing message

> **Run an evolving campaign without losing the memory of your world.**

## The problem

Generative AI makes it easy to produce an isolated scene, chapter, NPC, dialogue or plot idea. The difficult problem appears after repeated use.

As a narrative universe grows, creators accumulate:

- characters and their evolving states;
- facts and rules;
- relationships;
- locations;
- events and timelines;
- constraints and intentions;
- versions and revisions;
- decisions made during the story or campaign.

A generic chat session can produce plausible text while silently drifting from established facts. A document, wiki or story bible can store information without actively checking every change against it.

The opportunity is the gap between **generation** and **continuity control**.

## The product thesis

Book Loop treats narrative creation as a controlled stateful loop:

```text
Creator intent
      ↓
Context / existing Canon
      ↓
Proposal or new content
      ↓
Validation + review
      ↓
Findings / conflicts / suggested corrections
      ↓
Human decision
      ↓
Approved Canon
      ↓
Next creation / revision
```

AI agents propose and critique. The Canon records what has actually been approved. The loop is the product; the LLM is an interchangeable capability inside it.

This matches the existing product architecture: immutable versions, structured reviews, provenance, approval gates and evidence-backed canonical facts are already core MVP concepts.

## Why the Canon matters

"Memory" is too weak a description of the product.

A memory system can retrieve information. A Canon establishes a trusted state.

Book Loop distinguishes:

- **proposal** — generated or inferred information that may be useful but is not yet authoritative;
- **evidence** — the source supporting an assertion;
- **conflict** — incompatible assertions that require a decision;
- **review decision** — the human/application decision about proposed knowledge;
- **Canonical fact** — approved knowledge that subsequent workflows are allowed to rely on.

This boundary is central to trust. An LLM must not silently rewrite the creator's universe.

## Target customers

### Primary wedge — authors of fiction

**Ideal profile:** an author writing a novel or series who wants substantial AI assistance but cares deeply about continuity, character consistency and control over the final work.

Typical pain:

- long projects exceed the practical memory of ad-hoc chats;
- revisions introduce contradictions;
- story-bible information becomes stale;
- it is hard to know whether a new chapter conflicts with earlier material;
- the author wants AI assistance without delegating authorship.

Why start here:

- the current MVP is explicitly a book workflow;
- the chapter loop is already implemented end-to-end at the application level;
- the value can be demonstrated on a concrete artifact: a book;
- the existing product vision treats books as the proving ground for the engine.

### Secondary wedge — Game Masters / tabletop RPG creators

**Ideal profile:** a GM running a persistent campaign with enough world state, NPCs, factions and player decisions that manual continuity becomes burdensome.

Typical pain:

- campaign facts accumulate across sessions;
- player decisions change the world;
- NPC relationships and faction states evolve;
- old notes become difficult to reconcile;
- improvisation can contradict established campaign facts.

The opportunity is not to replace campaign-management tools. It is to add a **consistency and change-review layer** over the evolving campaign Canon.

This is a strong adjacent market because the same primitives naturally represent characters, locations, factions, events, relationships and temporal changes.

### Secondary wedge — screenwriters

**Ideal profile:** a screenwriter or small creative team managing a screenplay, series or evolving story universe where continuity across scenes, drafts and revisions matters.

Typical pain:

- revisions create continuity regressions;
- multiple versions make the current state ambiguous;
- character and timeline changes propagate across scenes;
- collaboration increases the cost of keeping the story state aligned.

Book Loop should not initially compete with professional screenwriting editors on formatting, screenplay editing or collaboration. Its differentiation is the **continuity layer**.

## Segment strategy

The three segments share one underlying problem but should not be marketed as three separate products at launch.

```text
                 Narrative Consistency
                         Engine
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
       Authors         Screenwriters          GMs
          │                 │                 │
       Book Canon       Script Canon      Campaign Canon
```

**Commercial sequence:**

1. Prove value with authors and the Book MVP.
2. Test the same Canon/change-review primitives with GMs.
3. Test screenwriter workflows without becoming a general screenplay editor.
4. Generalize only where repeated user evidence shows that the same engine solves the same problem.

## Competitive landscape

The market is fragmented into several categories.

### AI writing assistants

Examples include Sudowrite, NovelAI, Novelcrafter and Squibler.

Their strengths include generation, ideation, long-form writing workflows, project context, planning and writing assistance. Novelcrafter is particularly relevant because it already combines a writing workspace, Codex, planning, review and access to multiple AI providers.

**Implication:** Book Loop cannot differentiate merely by saying "AI writing", "project memory", "story bible" or "multiple models".

### Worldbuilding / campaign management

Examples include World Anvil, Kanka and Campfire.

Their strengths include structured worldbuilding, characters, locations, relationships, timelines, campaign management and encyclopedic storage.

**Implication:** Book Loop should not compete by becoming a better static wiki. The differentiator is checking the **effect of new content and changes on the existing Canon**.

### Professional writing / screenplay tools

Examples include Arc Studio and other established editors.

Their strengths include authoring, formatting, collaboration, revision workflows and professional output formats.

**Implication:** Book Loop should complement these tools before attempting to replace them. The long-term integration opportunity is a consistency layer over existing sources of truth.

## Differentiation

The key distinction is:

> **Other tools help you create or store the universe. Book Loop helps you change it without silently breaking it.**

The defensible product capabilities are therefore:

1. **Persistent Canon** — approved knowledge is distinct from transient AI output.
2. **Evidence and provenance** — users can understand why a fact is considered canonical.
3. **Review before mutation** — proposed changes do not silently become truth.
4. **Continuity checks** — new content is reviewed against the known state.
5. **Version-aware workflow** — revisions remain auditable rather than overwriting history.
6. **Change impact** — the future product should answer "what becomes wrong if I change this?".
7. **Provider independence** — the product value sits above the LLM vendor.

## What we are not selling

Do not lead with:

- "the best AI writer";
- "generate a complete book with one click";
- "an infinite story bible";
- "the most powerful LLM";
- "a collection of agents";
- raw token volume;
- a replacement for Notion, World Anvil, Kanka, Arc Studio or professional authoring tools.

Those may be implementation details or supporting capabilities. They are not the core customer outcome.

## Messaging hierarchy

### Level 1 — outcome

> **Keep your universe coherent, even as it grows and changes.**

### Level 2 — mechanism

> Book Loop checks new writing and revisions against your approved Canon, surfaces contradictions and quality issues, and lets you decide what becomes canonical.

### Level 3 — workflow

> Intent → plan → write → review → correct → approve → update Canon → continue.

### Level 4 — technical proof

- structured Canon;
- provenance;
- evidence-backed assertions;
- immutable versions;
- deterministic validation where possible;
- bounded AI review and correction;
- explicit approval gates.

Marketing should move from Level 1 to Level 4, not start at Level 4.

## Business model hypothesis

The initial business should be a **creator SaaS**, not an enterprise knowledge platform.

The customer pays for a reliable narrative workflow and continuity protection, not for access to a particular model or raw tokens.

### Commercial unit

Prefer understandable product units such as:

- active projects / books / campaigns;
- workflow capacity;
- continuity/review capacity;
- later, collaboration and professional capabilities.

Internally, usage can still be metered by model tokens and workflow steps for cost control. Those infrastructure units should not be the primary customer-facing abstraction.

### Launch structure hypothesis

Keep the public offer simple while the product is being validated:

**Free**

- enough access to experience the complete loop;
- one project;
- bounded AI workflow usage;
- no promise of unlimited generation.

**Pro / Creator**

- full Book Loop workflow;
- meaningful monthly workflow allowance;
- continuity and Canon features;
- version/review history;
- enough capacity to complete real writing work.

A higher tier should be introduced only after observed usage shows that heavy creators need more capacity or professional features.

### Pricing hypothesis

The current pricing hypothesis remains:

- Free: €0;
- Creator: approximately €12/month;
- Pro: approximately €24/month;
- Power/Studio: approximately €49/month, only after usage evidence;
- early paid beta: potentially €19/month for the Pro experience.

These are **not launch prices** and must not be represented as final commercial commitments until billing and willingness-to-pay are validated.

The existing €24 anchor is reasonable as a hypothesis because it sits inside the established range of serious AI-assisted writing subscriptions without attempting to win on commodity price. It should be tested, not assumed.

## Unit economics principles

LLM inference is an important cost, but it should not define the product's value proposition.

A single completed chapter may involve:

```text
Writer
  ↓
Validation
  ↓
Reviewer
  ↓
Correction / retry
  ↓
Summary
  ↓
Canonical extraction
```

Therefore internal cost models must account for workflow multiplication, retries, context growth and model routing.

Commercial guardrails:

- use bounded usage internally even when the UX feels simple;
- do not promise unlimited premium-model inference;
- route deterministic and low-value tasks to inexpensive models where quality permits;
- reserve stronger models for tasks where quality creates measurable value;
- target healthy gross margin on normal paid usage;
- use real usage data before committing to hard limits.

## What must be validated before final pricing

Pricing is not validated by competitor comparison alone.

We need evidence on:

1. whether the continuity problem is painful enough to pay to solve;
2. whether the Canon/review loop creates a clear advantage over generic LLM workflows;
3. whether authors return for repeated chapters/revisions;
4. whether GMs experience the same value in campaigns;
5. which usage unit feels natural to customers;
6. willingness to pay at €12 / €19 / €24 / €49 price points;
7. how often users hit workflow limits;
8. actual LLM and infrastructure cost per active customer;
9. retention after a real project is underway.

## Product validation sequence

### Stage 1 — prove the promise

A new user must quickly understand:

> "This protects the coherence of my universe while I use AI to create it."

### Stage 2 — prove the loop

The user should be able to:

1. define intent;
2. establish context;
3. generate a proposal;
4. receive useful review findings;
5. approve/reject changes;
6. see the approved state carried forward.

### Stage 3 — prove repeated value

The strongest evidence is not a successful first chapter. It is repeated use across chapters, revisions or sessions where the Canon prevents real errors or saves meaningful work.

### Stage 4 — test adjacent creators

Once the author workflow is trusted, test the same engine with:

- campaign continuity for GMs;
- screenplay/series continuity for screenwriters.

Do not create dedicated vertical features until the underlying problem is demonstrated.

## Strategic product boundary

The current MVP should remain focused on the Book loop. Generalization should happen in the engine and data model, not by adding unrelated vertical features prematurely.

The long-term abstraction is:

> **A trusted, evidence-backed state of an evolving narrative universe, plus a workflow that reviews proposed changes before they become truth.**

Books, scripts and RPG campaigns are different presentations of that same problem.

## Decision principles

- **Sell coherence, not AI.**
- **Sell control, not automation theater.**
- **Canon is the product trust boundary.**
- **The loop is more valuable than any individual agent.**
- **Do not compete on model quality alone.**
- **Do not compete on raw generation volume.**
- **Do not turn the MVP into three vertical products.**
- **Do not finalize pricing before real customer evidence.**
- **Use the Book workflow to prove the engine before broad expansion.**
