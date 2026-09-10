from __future__ import annotations

import pytest
from pydantic import ValidationError

from book_loop.domain.temporal import TemporalRelation, TemporalScope, TemporalScopeKind


def scope(start: int, end: int | None = None) -> TemporalScope:
    return TemporalScope(
        kind=TemporalScopeKind.STORY_POINT,
        position=start,
        end_position=end,
    )


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (scope(1), scope(2), TemporalRelation.BEFORE),
        (scope(1, 2), scope(2, 4), TemporalRelation.MEETS),
        (scope(1, 3), scope(2, 4), TemporalRelation.OVERLAPS),
        (scope(2), scope(1, 4), TemporalRelation.DURING),
        (scope(1, 4), scope(2), TemporalRelation.CONTAINS),
        (scope(2, 4), scope(2, 4), TemporalRelation.SIMULTANEOUS),
        (scope(4), scope(1, 3), TemporalRelation.AFTER),
    ],
)
def test_temporal_relation_is_deterministic(
    left: TemporalScope,
    right: TemporalScope,
    expected: TemporalRelation,
) -> None:
    assert left.relation_to(right) is expected


def test_relation_is_directional() -> None:
    assert scope(1).relation_to(scope(2)) is TemporalRelation.BEFORE
    assert scope(2).relation_to(scope(1)) is TemporalRelation.AFTER


def test_timeless_scope_has_no_ordered_relation() -> None:
    assert TemporalScope().relation_to(scope(2)) is None
    assert TemporalScope().overlaps(scope(2)) is True


def test_story_scope_requires_a_position() -> None:
    with pytest.raises(ValidationError):
        TemporalScope(kind=TemporalScopeKind.STORY_POINT)


def test_timeless_scope_cannot_define_positions() -> None:
    with pytest.raises(ValidationError):
        TemporalScope(position=2)


def test_interval_end_cannot_precede_start() -> None:
    with pytest.raises(ValidationError):
        scope(4, 2)
