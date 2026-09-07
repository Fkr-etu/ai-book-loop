from book_loop.domain.consistency import ConsistencyIssue


def test_consistency_issue_exposes_confidence_rule_and_metadata() -> None:
    issue = ConsistencyIssue(
        id="issue-1",
        category="timeline",
        severity="error",
        status="open",
        message="Chronology conflict",
        left_assertion_id="a1",
        right_assertion_id="a2",
        left_statement="Marie born 1985",
        right_statement="Marie died 1972",
        confidence=0.87,
        rule_id="TIMELINE_BIRTH_AFTER_DEATH",
        metadata={"detector": "timeline"},
    )

    assert issue.confidence == 0.87
    assert issue.rule_id == "TIMELINE_BIRTH_AFTER_DEATH"
    assert issue.metadata == {"detector": "timeline"}
