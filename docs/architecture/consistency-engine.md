# Corpus Consistency Engine

## Product intent

Book Loop protects the coherence of a long-lived book corpus. The system detects and explains possible contradictions; the author remains the decision-maker.

> **L'IA propose, l'auteur décide.**

The consistency engine is therefore a **detection and explanation layer**, not an autonomous truth engine. It may surface a conflict, but it must not silently choose which statement is true or mutate Canon.

## Current architecture

```text
                         UnifiedConsistencyEngine
                                  |
              +-------------------+----------------------+
              |          |                |              |
       Assertion       Timeline       Character        World
       detector        detector        detector        detector
              |          |                |              |
        DetectConflicts |                |              |
              |          +----------------+--------------+
              |                           |
              +---------------------------+
                          |
                  ConsistencyIssue

New chapter text
      |
      v
CanonDiagnosticChecker
      |
Assertion extraction + active Canon
      |
Assertion ↔ Canon
```

The unified engine currently combines persisted assertion conflicts with three deterministic narrative detectors. The existing chapter-validation path remains distinct: **do not implement a second Canon-vs-text detector.** If that capability is exposed through the unified engine later, adapt the existing `CanonDiagnosticChecker` behind the shared detector contract.

## Existing implementations

### `DetectConflicts`

Location: `book_loop/application/use_cases/detect_conflicts.py`

Responsibility: detect contradictions between persisted assertions in one book.

Current V1 rule: two non-rejected assertions conflict when they have the same normalized subject and predicate but different normalized objects.

### `AssertionConsistencyDetector`

Location: `book_loop/application/use_cases/assertion_consistency_detector.py`

Responsibility: adapt the existing persisted `DetectConflicts` behavior to the shared consistency-detector contract and project conflicts into `ConsistencyIssue` objects.

### `TimelineConsistencyDetector`

Location: `book_loop/application/use_cases/timeline_consistency_detector.py`

Responsibility: detect explicit impossible birth/death chronology.

Current rule:

- accepted/proposed/deferred assertions are considered;
- birth predicates include `birth`, `born`, `birth_date`, `date_of_birth`;
- death predicates include `death`, `died`, `death_date`, `date_of_death`;
- years are extracted conservatively from the assertion object;
- a finding is raised only when birth year is strictly later than death year.

This detector is intentionally narrow. It does not infer chronology from arbitrary prose or assume that two events are contradictory merely because they concern the same character.

### `CharacterContinuityDetector`

Location: `book_loop/application/use_cases/character_continuity_detector.py`

Responsibility: detect explicit mutually exclusive character states.

Current rule set is deliberately small: alive/dead and married/single. Both sides must carry an explicit affirmative value. This avoids treating historical or negated prose as a current state.

### `WorldContinuityDetector`

Location: `book_loop/application/use_cases/world_continuity_detector.py`

Responsibility: detect explicit positive/negative relations for the same subject and target.

Current rules cover relations such as `contains` vs `does_not_contain`, `has` vs `does_not_have`, and `located_in` vs `not_located_in`. The target is normalized before comparison, but no semantic equivalence is inferred.

### `CanonDiagnosticChecker`

Location: `book_loop/application/services/canon_validation.py`

Responsibility: compare assertions extracted from **new chapter text** with the book's active `CanonicalFact` records and emit `Diagnostic` objects for contradictions.

This checker remains the source of truth for the existing chapter-validation path. Future consistency-engine integration should compose or adapt it rather than copy its comparison logic.

### `UnifiedConsistencyEngine`

Location: `book_loop/application/use_cases/consistency_engine.py`

Responsibility: compose registered detectors and deduplicate their `ConsistencyIssue` results using stable issue IDs.

Detectors are read-only projections: the narrative detectors do not persist conflicts and do not mutate Canon.

### `AnalyzeConsistency`

Location: `book_loop/application/use_cases/analyze_consistency.py`

Responsibility: application entry point for consistency analysis. It runs the assertion detector plus the three narrative detectors through `UnifiedConsistencyEngine` and preserves the existing API contract.

`list_existing()` remains a read-only projection of persisted assertion conflicts.

## Identity, evidence and idempotency

Narrative detector findings use deterministic UUID5 identities derived from the book, detector rule, and assertion pair. Re-running a detector therefore returns the same issue ID for the same pair.

Every finding projects both assertion statements and their available evidence excerpts into the shared `ConsistencyIssue` contract. Missing evidence does not cause a detector to invent provenance.

Rejected assertions are ignored by the narrative detectors. No detector creates a new Canon fact, resolves a conflict, or changes assertion status.

## Precision-first strategy

The engine should optimize for **useful precision before broad recall**. A flood of weak consistency warnings is worse than a smaller set of evidence-backed issues.

The current progression is:

1. deterministic assertion conflicts;
2. deterministic narrative invariants with explicit predicates;
3. existing Canon-vs-new-text diagnostics integrated without duplication;
4. richer temporal and relationship constraints;
5. semantic/NLI/LLM-assisted detection where deterministic rules cannot express the relation;
6. incremental and asynchronous analysis when corpus size requires it.

LLM-assisted detection must expose evidence, confidence, and provenance and must remain a proposal. It must not become an implicit approval mechanism.

## Detector contract

A consistency detector should:

- accept a book identifier and inspect authoritative persisted state as needed;
- return the shared `ConsistencyIssue` contract;
- have one clearly defined detection responsibility;
- preserve provenance/evidence references;
- use stable identities;
- avoid mutating Canon;
- be independently testable;
- be composable by `UnifiedConsistencyEngine`.

The engine owns **composition and deduplication**. A detector owns **its detection rule**. Canon review owns **the truth/approval decision**.

## What the engine does not do

The consistency engine does not:

- decide which conflicting assertion is true;
- silently rewrite manuscript text;
- silently promote extracted knowledge to Canon;
- replace human review;
- treat embeddings or an LLM as the source of truth;
- duplicate existing validation rules merely to expose them through another surface.
