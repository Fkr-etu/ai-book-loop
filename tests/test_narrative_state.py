import pytest
from pydantic import ValidationError

from book_loop.domain.narrative_state import (
    EntityNarrativeState,
    NarrativeEvent,
    NarrativeStateTracker,
    StateTransition,
)


def event(*, event_id: str = "escape", position: int = 4) -> NarrativeEvent:
    return NarrativeEvent(
        id=event_id,
        event_type="escape",
        subject="Kael",
        story_position=position,
        evidence_ids=["evidence-1"],
    )


def transition(
    *,
    transition_id: str = "location-1",
    from_value: str | None = None,
    to_value: str = "Bas-Fonds",
    event_id: str = "escape",
    position: int = 4,
) -> StateTransition:
    return StateTransition(
        id=transition_id,
        entity="Kael",
        predicate="located_in",
        from_value=from_value,
        to_value=to_value,
        event_id=event_id,
        story_position=position,
        evidence_ids=["evidence-1"],
    )


def test_tracker_reconstructs_dynamic_location_after_event() -> None:
    tracker = NarrativeStateTracker()
    tracker.add_event(event())

    tracker.apply_transition(
        StateTransition(
            id="location-0",
            entity="Kael",
            predicate="located_in",
            to_value="Unité de Recherche 403",
            event_id="escape",
            story_position=4,
        )
    )
    tracker.apply_transition(transition(from_value="Unité de Recherche 403"))

    state = tracker.state_for("Kael")
    assert state is not None
    assert state.current_value("located_in") == "Bas-Fonds"
    assert state.snapshot(4).values["located_in"] == "Bas-Fonds"
    assert [item.to_value for item in state.history] == [
        "Unité de Recherche 403",
        "Bas-Fonds",
    ]


def test_transition_requires_matching_event() -> None:
    tracker = NarrativeStateTracker()
    tracker.add_event(event())

    with pytest.raises(ValueError, match="Transition entity"):
        tracker.apply_transition(
            transition().model_copy(update={"entity": "Elara"})
        )


def test_transition_requires_known_event() -> None:
    tracker = NarrativeStateTracker()

    with pytest.raises(ValueError, match="Unknown event"):
        tracker.apply_transition(transition())


def test_transition_requires_story_order() -> None:
    state = EntityNarrativeState(entity="Kael")
    state.apply(transition(transition_id="later", position=5))

    with pytest.raises(ValueError, match="story order"):
        state.apply(transition(transition_id="earlier", position=3))


def test_transition_from_value_is_checked() -> None:
    state = EntityNarrativeState(entity="Kael")
    state.apply(transition(transition_id="initial", position=1, to_value="A"))

    with pytest.raises(ValueError, match="expects located_in='B'"):
        state.apply(
            transition(
                transition_id="invalid",
                position=2,
                from_value="B",
                to_value="C",
            )
        )


def test_transition_cannot_be_a_noop() -> None:
    with pytest.raises(ValidationError):
        transition(from_value="Bas-Fonds", to_value="Bas-Fonds")
