# Product Vision

## Strategic direction

AI Book Loop is evolving from an **AI writing assistant for authors** into a **Narrative Canon & Continuity Engine** for teams that create and maintain complex fictional universes.

The writing loop remains an important internal capability, but it is no longer the primary product proposition. The product's durable value is maintaining a trusted, versioned source of truth and detecting when new or edited content breaks that canon.

## Mission

Help narrative teams keep every character, event, relationship, location, rule, and piece of lore coherent as their universe grows.

> **We don't write your story. We protect your universe.**

## Initial ideal customer profile

The first commercial wedge is **small narrative game studios and narrative teams (roughly 5–30 people)** working on projects with substantial lore, dialogue, quests, characters, or timelines.

This segment is preferred over the broad author market because:

- continuity failures become expensive as content and team size increase;
- several people contribute to the same canon;
- AI-assisted content generation increases the volume of content that needs QA;
- a studio has a stronger willingness to pay than an individual author;
- the workflow naturally supports team, project, and eventually studio-level SaaS pricing.

Publishing teams and other IP-heavy narrative businesses are secondary expansion markets, not the initial target.

## Problem

Narrative teams currently maintain canon across documents, spreadsheets, wikis, writing tools, and people's memory. When something changes, it is difficult to answer:

- What does this change contradict?
- Which characters, events, documents, quests, or chapters are affected?
- What information does a character know at a given point in the timeline?
- Which content is authoritative?
- Who approved the latest canonical version?

Generic LLM writing tools can generate plausible text, but plausibility is not continuity. The product should own the **consistency and change-impact problem**, not compete primarily on text generation quality.

## Core product promise

Given an existing canon and new or modified content, the system should:

1. extract and structure canonical facts;
2. validate new content against those facts;
3. identify contradictions, uncertainty, and stale information;
4. explain the affected entities and dependencies;
5. let humans review and approve changes;
6. update the canonical state with a complete history.

## Killer interaction

> **"What breaks if I change this?"**

A user changes a fact, character attribute, event, relationship, or rule. The system shows the downstream content and canonical assertions that may become invalid.

This change-impact workflow is the central product wedge. Generation and rewriting are supporting capabilities that help resolve issues; they are not the product's reason to exist.

## Product model

```text
SOURCE MATERIAL
      ↓
   CANON DB
      ↓
┌─────┼─────────┐
↓     ↓         ↓
Lore  Characters Timeline
└─────┼─────────┘
      ↓
CONTENT INGESTION
      ↓
CONTINUITY ENGINE
      ↓
┌─────┼──────────────┐
↓     ↓              ↓
Errors  Changes      Risks
      ↓
 HUMAN REVIEW
      ↓
 APPROVED CANON
      ↓
 NEW / EDITED CONTENT
```

The existing chapter loop remains useful as an implementation pattern:

```text
Intent → Proposal → Validation → Review → Canonical state → Next change
```

It is generalized from chapter generation to **content lifecycle + canonical state management**.

## Product principles

- **Canon is the source of truth.** Generated content is not canonical until explicitly approved.
- **Continuity is first-class.** Characters, facts, relationships, events, and timelines are modeled as dependencies rather than merely embedded in prompts.
- **Deterministic rules stay deterministic.** Dates, constraints, state transitions, permissions, and other hard invariants should not depend solely on an LLM judgment.
- **LLMs assist; they do not own state.** Provider-specific intelligence remains replaceable infrastructure.
- **Every change is auditable.** Preserve versions, approvals, provenance, and review decisions.
- **Explainability beats magic.** A contradiction should identify the conflicting assertions and affected content.
- **Cost-consciousness matters.** Avoid unnecessary LLM calls and reserve model usage for extraction, semantic comparison, and ambiguous cases.
- **Human approval remains the authority.** The system recommends; the team decides.

## Business model hypothesis

The product should be sold as a B2B SaaS rather than primarily as a consumer author subscription.

Initial hypothesis:

- Team: approximately €99–199/month;
- Studio: approximately €499–999/month;
- Enterprise: custom pricing for SSO, security, API, dedicated infrastructure, and support.

These prices are hypotheses to validate through customer discovery, not commitments.

Usage should not be priced purely on LLM tokens. Pricing should primarily reflect projects, collaborators, canon capacity, continuity checks, integrations, and governance value.

## What we are explicitly not building

- another generic AI chapter/novel generator;
- a prompt library disguised as a SaaS;
- a product whose moat is a proprietary writing prompt;
- a broad enterprise knowledge-management platform before the narrative use case is validated.

## Success criteria for the pivot

The pivot is validated only if prospective narrative teams repeatedly demonstrate that continuity/change-impact is a painful problem and at least some are willing to pay for a solution.

Before substantial platform expansion, validate:

1. at least 10 customer discovery interviews with the target ICP;
2. at least 3 teams willing to test with real project material;
3. at least 1 paid pilot or equivalent strong buying signal;
4. a measurable reduction in time spent finding or resolving continuity issues.
