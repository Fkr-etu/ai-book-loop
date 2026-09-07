# Glossary

## Author intent

The author's theme, inspiration, idea, lore, and explicit constraints that generation must preserve.

## Canonical

Information accepted as authoritative for continuity. Rejected or transient generated material is not canonical.

## Canon

The project's approved source of truth for validated knowledge. Canon is a domain concept, not a prompt or an LLM memory.

## Canonical context

The focused context assembled from authoritative book information and prior accepted material for a generation step.

## Canonical fact

An approved assertion that has entered Canon and can be used as authoritative continuity context.

## Draft

Generated chapter content that has not yet become accepted/canonical content.

## Source document

Persisted source material from which assertions and evidence can be derived.

## Document chunk

A bounded portion of a source document used for extraction, evidence, and provenance.

## Assertion

A proposed structured claim extracted from source material. An assertion is not canonical merely because it was generated or extracted.

## Evidence

Source-level support and provenance for an assertion, including enough location/context information to explain where the claim came from.

## Conflict

A persisted incompatibility between assertions under the current deterministic interpretation. A conflict identifies competing claims; it does not decide which claim is true.

## Consistency issue

An author-facing representation of a consistency problem. It may be projected from a persisted conflict or, in future, from another detector. It is not itself an approval decision.

## Diagnostic

A validation result produced while checking content. Canon contradictions can be represented as diagnostics during chapter validation.

## Review decision

An explicit decision about proposed knowledge, such as acceptance, rejection, or deferral. Decisions that affect Canon must be persisted and auditable.

## Use case

An explicit application-level business action, such as `GenerateOutline`, `GenerateChapter`, or `AnalyzeConsistency`.

## Detector

A focused consistency capability that identifies one class of potential inconsistency and returns the shared consistency-issue contract. A detector does not approve Canon.

## Consistency engine

The orchestration layer that composes consistency detectors and deduplicates their author-facing issues. `UnifiedConsistencyEngine` is the current implementation.

## Agent

A focused capability that interacts with an LLM, such as writing, reviewing, or summarizing. An agent is not itself a business use case and cannot approve Canon.

## Workflow

The orchestration of multiple steps needed to complete a generation process, particularly the chapter write/review/retry loop.

## Provider

An implementation of the LLM capability used by the application. Gemini is the MVP provider but is intentionally replaceable.

## Provenance

The information needed to trace a claim or decision back to its source and supporting evidence.

## Idempotency

The property that repeating the same logical operation does not create duplicate or divergent durable state. Chapter runs and consistency analysis rely on stable identities and persisted invariants.

## ADR

Architecture Decision Record: a short, immutable historical record of a significant architecture decision and its consequences.
