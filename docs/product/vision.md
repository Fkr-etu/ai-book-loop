# Product Vision

## Strategic direction

AI Book Loop starts with a deliberately focused product: an **agentic AI loop for reviewing, improving, and drafting a book**. The book workflow is not a disposable prototype or a temporary marketing story. It is the first concrete domain in which we will prove the underlying engine.

The strategic opportunity is to generalize that engine beyond books into **documentation and company knowledge QA**: a system that understands a corpus as a set of claims, dependencies, versions, and approvals, then reviews new or changed content against that knowledge.

The progression is intentional:

```text
AGENTIC BOOK LOOP
Review → propose → validate → approve → canonical state
                    ↓
            generalized knowledge model
                    ↓
DOCUMENTATION / COMPANY KNOWLEDGE QA
Ingest → extract claims → detect regressions → review → approve
```

The book is the **wedge and proving ground**. The underlying business logic is the long-term platform opportunity.

## Mission

Build an AI agentic workflow that can reason over a long-lived body of content, review changes against its canonical state, propose improvements, and keep the approved knowledge coherent over time.

The first manifestation is book creation. Later manifestations include product documentation, technical documentation, internal company knowledge, and other high-value documentation workflows.

## Why start with books?

The book domain is valuable because it forces the system to solve the hard version of the problem:

- long context and evolving state;
- characters, facts, relationships, events, and timelines;
- continuity across many documents/chapters;
- explicit author intent and quality review;
- iterative generation rather than one-shot prompting;
- human approval of proposed changes;
- a canonical state that evolves over time.

These constraints are not incidental. They are the training ground for the generalized engine.

The initial product should therefore **keep the book-writing loop as a first-class experience**, rather than prematurely hiding it behind an abstract documentation product.

## Initial product — Agentic Book Loop

The product helps an author or small writing team move through a controlled loop:

```text
Intent
  ↓
Research / context
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

AI agents may analyze, critique, propose, and draft. They must not silently mutate canonical state. Human approval remains the authority.

The important product property is the **loop**, not a particular model or prompt.

## The underlying abstraction

The engine should progressively separate content from the invariants that make it coherent.

A useful canonical model includes:

- entities: characters, products, teams, locations, concepts;
- claims/facts;
- relationships;
- events and temporal assertions;
- rules and constraints;
- source documents;
- versions;
- provenance;
- confidence;
- review decisions;
- dependencies between claims and content.

For a book, an assertion may be:

> Sarah learns the truth in chapter 18.

For a company, an assertion may be:

> API v3 requires OAuth 2.0.

The engine should eventually be able to treat both as the same underlying primitive: **a claim whose validity can affect other content**.

## Long-term product direction — Knowledge QA

Once the book loop is reliable, extend the same logic to documentation and company knowledge.

The product should sit above existing systems rather than requiring migration:

```text
Notion / Confluence / Git / Docs / Wiki / PDFs
                    ↓
              KNOWLEDGE ENGINE
                    ↓
       claims / dependencies / canon
                    ↓
            REVIEW & REGRESSION QA
                    ↓
        contradictions / stale content
              / change impact
                    ↓
              human approval
```

The commercial proposition becomes **Documentation QA / Knowledge Consistency**, with the book workflow as the first validated use case.

A future killer interaction is:

> **"What becomes wrong if I change this?"**

and, for continuous workflows:

> **"Check this new content against the current knowledge state."**

## Business model hypothesis

The first product can validate willingness to pay in the author / small-team market while the larger opportunity is B2B documentation and knowledge QA.

The business should progressively move toward SaaS pricing based on value delivered by the knowledge workflow rather than raw model tokens.

Potential expansion:

1. Book / writing subscription for the initial product.
2. Team plans for collaborative book projects.
3. Documentation QA for software companies.
4. Company knowledge QA across multiple sources.
5. API / infrastructure for knowledge consistency checks.

Pricing remains a hypothesis to validate with customers; do not optimize for enterprise pricing before product evidence exists.

## Product principles

- **The loop is first-class.** Review, propose, validate, approve, and update state are core product primitives.
- **Canon is the source of truth.** Generated or inferred content is not canonical until approved.
- **AI agents assist; they do not own state.** Agents can reason and propose changes within bounded workflows.
- **Continuity and correctness are first-class.** Model dependencies rather than relying only on prompt context.
- **Deterministic rules stay deterministic.** Dates, permissions, state transitions, and hard constraints should not depend solely on LLM judgment.
- **Every change is auditable.** Preserve versions, provenance, and review decisions.
- **Explainability beats magic.** A finding should expose its supporting claims and affected content.
- **Existing systems remain sources.** The future documentation product should integrate before it asks customers to migrate.
- **Cost-consciousness matters.** Use LLMs where semantic reasoning adds value; avoid unnecessary calls.

## What we are explicitly not building

- a generic one-shot AI writing assistant;
- a simple lore / story-bible database;
- a generic documentation editor competing with Notion or Confluence;
- a broad enterprise knowledge-management suite before the underlying engine is validated;
- a product whose moat is a proprietary prompt.

## Success criteria for the strategic transition

The first milestone is not to prove the entire company-knowledge vision. It is to prove the loop in the book domain.

### Book wedge

- authors complete real chapters with the agentic loop;
- AI review catches useful continuity/quality issues;
- proposed changes are understandable and controllable;
- canonical state remains trustworthy;
- users return for repeated review/drafting cycles.

### Expansion validation

Only after the book loop demonstrates repeated value should we test adjacent documentation workflows:

1. identify a documentation corpus with similar change/consistency pain;
2. reuse the canonical claim/dependency model;
3. prove that the same review loop catches costly regressions;
4. secure design partners and a paid pilot;
5. expand integrations and team governance only after evidence.
