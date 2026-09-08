# Product Positioning & Business Model

## Purpose

This document is the current product and commercial positioning for Book Loop. It defines the market hypothesis; it is not evidence of product-market fit or validated willingness to pay.

## Executive positioning

**Book Loop is a narrative consistency engine for creators who build complex, evolving universes.**

The current product is an author-focused book-writing workspace. The same underlying engine may later serve screenwriters and Game Masters, but those segments are validation targets, not launch products.

### Core promise

> **Keep your universe coherent, even as it grows and changes.**

### Author-facing message

> **Write with AI without losing the thread of your story.**

Book Loop remembers the approved state of the story, checks proposals and revisions against it, surfaces contradictions and quality issues, and keeps human approval at the boundary of what becomes Canon.

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
Findings / conflicts / corrections
      ↓
Human decision
      ↓
Approved Canon
      ↓
Next creation / revision
```

The loop is the product. The LLM is an interchangeable capability inside it.

## Why the Canon matters

A memory system retrieves information; a Canon establishes a trusted approved state.

Book Loop distinguishes:

- **proposal** — information that is not yet authoritative;
- **evidence** — the source supporting an assertion;
- **conflict** — incompatible assertions requiring a decision;
- **review decision** — the decision about proposed knowledge;
- **Canonical fact** — approved knowledge that subsequent workflows may rely on.

An LLM must not silently rewrite the creator's universe.

## Target customers

### Primary wedge — authors of fiction

The current MVP is explicitly a book workflow. The target user is an author who wants substantial AI assistance while retaining control over continuity, revisions and the final work.

The first validation questions are whether the loop saves meaningful continuity work, whether users return for multiple chapters/revisions, and whether the advantage over a generic LLM plus notes is strong enough to pay for.

### Secondary validation — Game Masters

Test campaign continuity only after the Book wedge demonstrates repeated value. Dedicated GM UX requires evidence that the same consistency problem is frequent, painful and valuable.

### Secondary validation — screenwriters

Test continuity across scenes, drafts, characters and timelines only after the Book wedge is validated. Do not initially compete with professional screenplay editors on formatting or collaboration.

## Differentiation

> **Other tools help you create or store the universe. Book Loop helps you change it without silently breaking it.**

The differentiation hypothesis is the combination of:

1. persistent Canon;
2. evidence and provenance;
3. review before mutation;
4. continuity checks;
5. version-aware workflow;
6. change-impact analysis as a future capability;
7. provider-independent product logic.

Do not lead with generic claims such as "best AI writer", raw generation volume, infinite story memory, agent count or access to a particular model.

## Current commercial model

The implemented commercial grid is the working launch hypothesis and should be kept consistent across product documentation:

| Plan | Monthly | Annual | Role |
|---|---:|---:|---|
| Free | €0 | — | Product discovery |
| Creator | €19 | €190 | Serious individual creator |
| Pro | €39 | €390 | Intensive creator / multiple projects |

Capacity limits are part of the product model. The offer does not promise unlimited AI inference.

These prices are the **current working prices**, not evidence that willingness to pay has been validated. Pricing can change after measured usage, retention and paid-user research.

There is currently no public Studio tier in the implemented commercial model. A higher-capacity tier is a future experiment, not a current plan.

## What must be validated

1. Is continuity painful enough to pay to solve?
2. Does the Canon/review loop outperform a generic LLM plus existing notes/tools?
3. Do authors return for repeated chapters and revisions?
4. Which usage/capacity boundary is understandable to customers?
5. Does willingness to pay support the €19 / €39 working grid?
6. What are actual LLM costs per completed workflow and per paying creator?
7. What retention and upgrade behavior emerges from real projects?

## Decision principles

- **Sell coherence, not AI.**
- **Sell control, not automation theater.**
- **Canon is the product trust boundary.**
- **The loop matters more than any individual agent.**
- **Do not finalize pricing from competitor comparison alone.**
- **Prove the Book workflow before broadening into adjacent verticals.**
