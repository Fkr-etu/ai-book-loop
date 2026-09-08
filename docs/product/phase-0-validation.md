# Phase 0 — Book wedge validation

## Purpose

Phase 0 is product validation, not another engineering milestone. The existing E2E suite demonstrates that the core loop can execute; it does not establish that real authors find the loop useful, trustworthy, repeatable, differentiated, or worth paying for.

The objective is to validate the complete author workflow on real projects and capture evidence for the Phase 0 decision gates.

## Validation loop

Use the product with real authors on a real or representative writing project:

1. Capture intent, theme, author idea, lore, constraints and tone.
2. Generate and review the outline.
3. Approve the outline as the author.
4. Generate a chapter proposal.
5. Inspect validation and AI review findings.
6. Accept/reject/revise according to the author decision.
7. Review proposed Canon changes and explicitly approve them.
8. Start the next chapter/revision from the resulting canonical state.
9. Repeat enough times to expose continuity value rather than first-run novelty.

## Evidence to collect

### 1. Intent and constraints

Questions:

- Did the author feel accurately represented by the initial brief?
- Which constraints were essential and which were unnecessary?
- Did the author trust the system to preserve those constraints?

Signal: the author can explain what Book Loop understood without reconstructing the brief manually.

### 2. Outline → draft

Questions:

- Was the proposed outline useful enough to approve or revise?
- Did chapter generation follow the approved intent?
- How much manual correction was required before the result was usable?

Signal: the author chooses the Book Loop flow over starting from a blank generic LLM prompt for the same task.

### 3. AI review / critique

Questions:

- Which findings were genuinely useful?
- Which findings were false positives or obvious?
- Did evidence/context make the finding understandable and actionable?
- Would the author have caught the issue without Book Loop?

Signal: at least one review finding changes an author decision or saves meaningful manual checking effort.

### 4. Continuity against Canon

Questions:

- Did the system catch a continuity issue that matters to the author?
- Did the author understand why the finding was raised?
- Did provenance/evidence make the Canon trustworthy?

Signal: the author treats Canon findings as a useful continuity safety net rather than generic AI commentary.

### 5. Human approval gates

Questions:

- Were approval points clear?
- Did the author understand what would become canonical and what would remain a proposal?
- Did any UI state make the author fear that AI had silently changed Canon?

Signal: the author can predict the consequence of Approve / Reject / Revise actions without assistance.

### 6. Canon update after approval

Questions:

- Did the approved Canon state reflect the author's decision?
- Was version/history/provenance understandable?
- Did the updated state materially help the next chapter or revision?

Signal: the author uses the updated Canon as an active part of the next writing step.

### 7. Complete Studio loop

The session is considered complete only when the author can move through:

`brief → outline → approval → chapter → review → decision → Canon → next chapter/revision`

without developer intervention or manual API/database manipulation.

### 8. Repeated use

Target: at least 3 meaningful author sessions per project, with multiple chapters or revisions where applicable.

Record:

- sessions completed;
- chapters/revisions processed;
- time spent per loop;
- manual workarounds;
- return intent;
- where the author abandons or bypasses the workflow.

### 9. Generic LLM + notes comparison

For the same author task, ask the author to compare Book Loop with their current workflow (for example, a generic LLM plus notes/documents).

Do not lead the participant toward a positive answer. Capture:

- what Book Loop does better;
- what the generic workflow does better;
- what Book Loop makes harder;
- which continuity risks remain unsolved;
- whether the persistent Canon/review loop is worth the extra workflow overhead.

### 10. Willingness to pay

Do not treat compliments or stated interest as payment validation.

Test progressively stronger signals:

1. "Would you use this again?"
2. "Would you replace part of your current workflow with it?"
3. "Would you pay for this today?"
4. Present a concrete plan/price hypothesis and ask for a commitment.
5. Where feasible, seek an actual paid pilot or pre-order signal.

## Participant protocol

Prefer authors who already manage a multi-chapter project and experience continuity/revision pain. Avoid selecting only technically sophisticated users who are unusually tolerant of unfinished UX.

For each participant, record a short structured debrief:

- project type and maturity;
- current workflow;
- primary continuity pain;
- Book Loop tasks completed;
- strongest observed value;
- strongest friction;
- trust issues;
- unexpected/manual workarounds;
- comparison with current tools;
- return intent;
- willingness-to-pay signal.

## Phase 0 decision matrix

| Gate | Evidence required | Status |
| --- | --- | --- |
| Intent / constraints | Author completes brief and confirms fidelity | Pending |
| Outline → draft | Author completes approved outline and chapter flow | Pending |
| AI review usefulness | At least one consequential/useful finding per relevant project | Pending |
| Continuity / Canon | Author trusts evidence-backed continuity findings | Pending |
| Human approval | Author understands and uses approval boundaries | Pending |
| Canon update | Approved decisions are visible and useful downstream | Pending |
| Studio E2E | Full loop completed without developer intervention | Pending |
| Repeated use | Multiple sessions/chapters or revisions | Pending |
| Generic LLM comparison | Clear differentiated advantage identified | Pending |
| Willingness to pay | Concrete commitment signal | Pending |

## What does not count as Phase 0 evidence

- Unit/integration/E2E tests passing by themselves.
- A successful demo by the developer.
- Feature completeness.
- Positive feedback without observed usage.
- "I would probably pay" without a concrete commitment.
- Building more Canon primitives before the current loop is validated.

## Exit criterion

Phase 0 exits only when real authors repeatedly use the Book Loop, trust its findings and Canon behavior, and perceive a meaningful advantage over their existing workflow.

Until that evidence exists, prioritize fixing observed friction and validating the existing Book loop over starting Phase 2/3 expansion.