# Consistency issue contract

`ConsistencyIssue` is the shared author-facing projection emitted by corpus consistency detectors.

Each issue carries a stable identity, category, severity, status, both assertion references and statements, available evidence, detector confidence, an optional rule identifier, optional metadata, and an optional resolution assertion.

Confidence describes confidence in the finding, not which assertion is true. Every issue remains a proposal for author review.
