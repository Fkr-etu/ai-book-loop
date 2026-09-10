import pytest
from pydantic import ValidationError

from book_loop.domain.epistemic import (
    AssertionEpistemic,
    AuthorityLevel,
    EpistemicStatus,
    should_defer_conflict,
)


def test_canonical_assertion_requires_canonical_authority() -> None:
    with pytest.raises(ValidationError):
        AssertionEpistemic(
            status=EpistemicStatus.CANONICAL,
            authority=AuthorityLevel.SOURCE,
        )


def test_canonical_vs_canonical_remains_a_hard_candidate() -> None:
    canonical = AssertionEpistemic(
        status=EpistemicStatus.CANONICAL,
        authority=AuthorityLevel.CANONICAL,
    )
    other = AssertionEpistemic(
        status=EpistemicStatus.CANONICAL,
        authority=AuthorityLevel.CANONICAL,
    )

    assert should_defer_conflict(canonical, other) is False


@pytest.mark.parametrize(
    "status",
    [EpistemicStatus.BELIEVED, EpistemicStatus.HYPOTHESIS, EpistemicStatus.UNCERTAIN],
)
def test_weak_epistemic_states_are_deferred(status: EpistemicStatus) -> None:
    weak = AssertionEpistemic(status=status, authority=AuthorityLevel.CHARACTER)
    canonical = AssertionEpistemic(
        status=EpistemicStatus.CANONICAL,
        authority=AuthorityLevel.CANONICAL,
    )

    assert should_defer_conflict(weak, canonical) is True


def test_lower_authority_claim_is_deferred_when_stronger_claim_is_more_reliable() -> None:
    canonical = AssertionEpistemic(
        status=EpistemicStatus.CANONICAL,
        authority=AuthorityLevel.CANONICAL,
        reliability=0.95,
    )
    report = AssertionEpistemic(
        status=EpistemicStatus.REPORTED,
        authority=AuthorityLevel.SOURCE,
        reliability=0.80,
    )

    assert should_defer_conflict(canonical, report) is True


def test_authority_alone_does_not_hide_a_more_reliable_lower_authority_claim() -> None:
    narrator = AssertionEpistemic(
        status=EpistemicStatus.REPORTED,
        authority=AuthorityLevel.NARRATOR,
        reliability=0.70,
    )
    source = AssertionEpistemic(
        status=EpistemicStatus.REPORTED,
        authority=AuthorityLevel.SOURCE,
        reliability=0.95,
    )

    assert should_defer_conflict(narrator, source) is False
