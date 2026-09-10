from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field, model_validator


class NarrativeEvent(BaseModel):
    """A story event that may explain one or more state transitions."""

    id: str
    event_type: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    story_position: int = Field(ge=0)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class StateTransition(BaseModel):
    """A deterministic change from one narrative state value to another."""

    id: str
    entity: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    from_value: str | None = None
    to_value: str = Field(min_length=1)
    event_id: str
    story_position: int = Field(ge=0)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_transition(self) -> "StateTransition":
        if self.from_value is not None and self.from_value == self.to_value:
            raise ValueError("A state transition must change the state value")
        return self


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """The state of one entity after a given story position."""

    story_position: int
    values: dict[str, str]


@dataclass(slots=True)
class EntityNarrativeState:
    """Ordered state history for one entity; events explain how values changed."""

    entity: str
    _current: dict[str, str] = field(default_factory=dict)
    _history: list[StateTransition] = field(default_factory=list)

    def apply(self, transition: StateTransition) -> None:
        if transition.entity != self.entity:
            raise ValueError("Transition entity does not match state entity")
        if self._history and transition.story_position < self._history[-1].story_position:
            raise ValueError("State transitions must be applied in story order")
        current = self._current.get(transition.predicate)
        if transition.from_value is not None and current != transition.from_value:
            raise ValueError(
                f"Transition expects {transition.predicate}={transition.from_value!r}, "
                f"but current value is {current!r}"
            )
        self._current[transition.predicate] = transition.to_value
        self._history.append(transition)

    def current_value(self, predicate: str) -> str | None:
        return self._current.get(predicate)

    def snapshot(self, story_position: int | None = None) -> StateSnapshot:
        position = story_position
        if position is None:
            position = self._history[-1].story_position if self._history else 0
        values: dict[str, str] = {}
        for transition in self._history:
            if transition.story_position > position:
                break
            values[transition.predicate] = transition.to_value
        return StateSnapshot(story_position=position, values=values)

    @property
    def history(self) -> tuple[StateTransition, ...]:
        return tuple(self._history)


class NarrativeStateTracker:
    """Build dynamic entity state from explicitly extracted events and transitions."""

    def __init__(self) -> None:
        self._states: dict[str, EntityNarrativeState] = {}
        self._events: dict[str, NarrativeEvent] = {}

    def add_event(self, event: NarrativeEvent) -> None:
        if event.id in self._events:
            raise ValueError(f"Event already exists: {event.id}")
        self._events[event.id] = event

    def apply_transition(self, transition: StateTransition) -> None:
        event = self._events.get(transition.event_id)
        if event is None:
            raise ValueError(f"Unknown event: {transition.event_id}")
        if event.subject != transition.entity:
            raise ValueError("Transition entity must match its event subject")
        if event.story_position != transition.story_position:
            raise ValueError("Transition and event must share the story position")
        state = self._states.setdefault(
            transition.entity, EntityNarrativeState(entity=transition.entity)
        )
        state.apply(transition)

    def state_for(self, entity: str) -> EntityNarrativeState | None:
        return self._states.get(entity)

    def event(self, event_id: str) -> NarrativeEvent:
        return self._events[event_id]
