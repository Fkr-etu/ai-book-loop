# Consistency issue contract

`ConsistencyIssue` is the shared author-facing projection emitted by corpus consistency detectors.

Each issue carries:

- a stable deterministic identifier;
- category, severity and lifecycle status;
- the two assertion identifiers and their statements;
- available evidence excerpts;
- detector confidence in `[0, 1]`;
- an optional stable rule identifier;
- optional detector metadata;
- an optional resolution assertion.

Confidence describes the detector's confidence in the finding, not which assertion is true. A consistency issue is always a proposal for author review.
