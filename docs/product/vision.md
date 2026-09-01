# Product Vision

## Strategic direction

AI Book Loop is evolving from an **AI writing assistant for authors** into a **Narrative Content QA & Canon Engine** for teams that create and maintain complex fictional content.

The writing loop remains an important internal capability, but it is no longer the primary product proposition. The durable value is reducing the cost of narrative/content inconsistencies by maintaining a trusted, versioned source of truth and detecting when new or edited content breaks that source of truth.

The competitive analysis reinforces this distinction: writing assistants, worldbuilding databases, narrative authoring tools, and branching engines already cover generation, organization, and production. The product should therefore not attempt to replace them. It should become the **QA layer that can inspect content produced in those tools**.

## Mission

Help narrative teams ship coherent content without manually checking every character, event, relationship, rule, timeline, and dependency after every change.

> **We don't write your story. We test whether your story still holds together.**

## Initial ideal customer profile

The first ICP hypothesis is **small-to-mid-sized narrative game teams (roughly 5–50 people)** that already have meaningful content and an existing production workflow.

Strong signals include:

- multiple writers/designers contribute to the same project;
- substantial dialogue, quests, lore, characters, or timelines already exist;
- the team uses one or more source systems such as Articy, Notion, Git, documents, spreadsheets, or custom tools;
- content changes frequently;
- localization, voice, implementation, or QA amplifies the cost of late narrative changes;
- AI-assisted production is increasing content volume;
- the team has experienced painful regressions or inconsistencies.

The important ICP qualifier is **not team size alone**. It is evidence that content inconsistency is a recurring operational cost.

Publishing teams and other IP-heavy narrative organizations remain secondary expansion markets.

## Problem

Narrative teams already have tools to write, organize, branch, and store content. The missing layer is often knowing whether the project is still internally consistent after content changes.

Typical questions are:

- What does this change contradict?
- Which characters, events, documents, quests, or dialogue lines are affected?
- Does this character know this information yet?
- Did a timeline change invalidate another event?
- Which content is stale after this canonical change?
- Which source is authoritative?
- Can we catch this before it reaches QA, localization, recording, or a build?

Generic LLM writing tools can generate plausible text, but plausibility is not continuity. Existing narrative databases can store a canon, but storage alone does not prove that downstream content still agrees with it.

The product therefore owns **narrative/content QA and change-impact analysis**, with the Canon Engine as its underlying source-of-truth model.

## Core product promise

Given an existing canon and new or modified content, the system should:

1. ingest content from the team's existing workflow;
2. extract and structure canonical facts and dependencies;
3. validate new content against approved assertions;
4. identify contradictions, stale information, structural risks, and uncertainty;
5. explain each finding with evidence and affected dependencies;
6. let humans review and approve changes;
7. maintain the canonical state and audit history.

## Killer interaction

> **"What breaks if I change this?"**

A user changes a fact, character attribute, event, relationship, or rule. The system shows the downstream content and canonical assertions that may become invalid.

A second core interaction is:

> **"Check this new content against my canon."**

These workflows turn the Canon Engine into a QA system rather than another authoring database.

## Product model

```text
EXISTING SOURCES
Articy / Git / Docs / Wiki / JSON / etc.
              ↓
        CANON ENGINE
              ↓
   ENTITIES + ASSERTIONS
              ↓
       CONTENT INGESTION
              ↓
       NARRATIVE QA ENGINE
              ↓
┌─────────────┼──────────────┐
↓             ↓              ↓
Contradictions  Risks       Impact
└─────────────┼──────────────┘
              ↓
        HUMAN REVIEW
              ↓
       APPROVED CANON
              ↓
        NEW CONTENT
```

The existing chapter loop remains useful as an implementation pattern:

```text
Proposal → Validation → Review → Canonical state → Next change
```

It is generalized from chapter generation to **content lifecycle + QA + canonical state management**.

## Competitive position

The product should explicitly avoid competing head-on with:

- AI writing assistants that optimize for prose generation;
- worldbuilding/story-bible products that optimize for organization;
- narrative authoring tools that optimize for branching and engine export.

The wedge is **cross-source narrative QA**: inspect content created elsewhere, compare it to the approved canon, identify evidence-backed inconsistencies, and calculate change impact.

This positioning matters because established tools already cover large parts of canon storage and narrative production. The product must complement those systems before it attempts to replace any of them.

## Product principles

- **Canon is the source of truth.** Generated or imported content is not canonical until explicitly approved.
- **QA is first-class.** The product is valuable because it detects problems, not because it stores more lore.
- **Continuity is evidence-backed.** Findings should identify the conflicting assertions, source material, and affected dependencies.
- **Deterministic rules stay deterministic.** Dates, constraints, state transitions, permissions, identifiers, and other hard invariants should not depend solely on an LLM judgment.
- **LLMs assist; they do not own state.** Provider-specific intelligence remains replaceable infrastructure.
- **Every change is auditable.** Preserve versions, approvals, provenance, and review decisions.
- **Explainability beats magic.** A useful finding is actionable and traceable.
- **Integrate before replacing.** Customers should not need to migrate their narrative stack to obtain value.
- **Cost-consciousness matters.** Avoid unnecessary LLM calls and reserve model usage for extraction, semantic comparison, and ambiguous cases.
- **Human approval remains the authority.** The system recommends; the team decides.

## Business model hypothesis

The product should be sold as a B2B SaaS focused on **risk reduction and QA**, rather than primarily as a consumer author subscription.

Initial pricing hypotheses:

- Team: approximately €99–299/month;
- Studio: approximately €499–1,499/month;
- Enterprise: custom pricing for SSO, security, API, dedicated infrastructure, and support.

These prices are hypotheses to validate through customer discovery, not commitments.

Pricing should not be based primarily on LLM tokens. Value-based dimensions should be tested first: projects, collaborators, canon capacity, content checks, integrations, CI usage, and governance.

## What we are explicitly not building

- another generic AI chapter/novel generator;
- another worldbuilding database;
- another branching dialogue editor;
- a prompt library disguised as a SaaS;
- a product whose moat is a proprietary writing prompt;
- a broad enterprise knowledge-management platform before the narrative use case is validated.

## Success criteria for the pivot

The pivot is validated only if target teams demonstrate that narrative/content inconsistencies are frequent and costly enough to justify a recurring QA product.

Before substantial platform expansion, validate:

1. at least 10 customer discovery interviews with teams matching the ICP;
2. at least 3 teams willing to test with real project material;
3. at least 1 paid pilot or equivalent strong buying signal;
4. a measurable reduction in time spent finding or resolving narrative regressions;
5. evidence that the product can integrate with existing tools without requiring migration.

## Critical falsification question

> **Do narrative inconsistencies cost enough, happen often enough, and occur early enough in the workflow that a team will pay €100–1,500/month to catch them?**

If the answer is no, the product should not expand into a larger platform. Revisit the ICP, problem severity, or adjacent QA use case instead.
