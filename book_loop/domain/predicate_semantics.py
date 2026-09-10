from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PredicateKind(StrEnum):
    """Semantic role of a predicate for narrative consistency checks."""

    UNKNOWN = "unknown"
    STATIC = "static"
    ATTRIBUTE = "attribute"
    LOCATION = "location"
    POSSESSION = "possession"
    STATUS = "status"
    RELATION = "relation"
    ACTION = "action"
    EVENT = "event"
    CAPABILITY = "capability"
    QUANTITY = "quantity"
    ROLE = "role"


class PredicateExclusivity(StrEnum):
    """How multiple values of a predicate should be interpreted."""

    UNKNOWN = "unknown"
    EXCLUSIVE = "exclusive"
    TEMPORAL = "temporal"
    MULTI_VALUED = "multi_valued"


@dataclass(frozen=True, slots=True)
class PredicateSemantics:
    """Deterministic metadata used by consistency rules."""

    kind: PredicateKind
    exclusivity: PredicateExclusivity
    supports_evolution: bool = False


class PredicateSemanticsRegistry:
    """Small explicit V1 registry with a conservative unknown default."""

    _SEMANTICS: dict[str, PredicateSemantics] = {
        "age": PredicateSemantics(PredicateKind.QUANTITY, PredicateExclusivity.TEMPORAL, True),
        "lives_in": PredicateSemantics(PredicateKind.LOCATION, PredicateExclusivity.TEMPORAL, True),
        "located_in": PredicateSemantics(PredicateKind.LOCATION, PredicateExclusivity.TEMPORAL, True),
        "occupation": PredicateSemantics(PredicateKind.ROLE, PredicateExclusivity.TEMPORAL, True),
        "alive_status": PredicateSemantics(PredicateKind.STATUS, PredicateExclusivity.TEMPORAL, True),
        "owns": PredicateSemantics(PredicateKind.POSSESSION, PredicateExclusivity.MULTI_VALUED, True),
        "belongs_to": PredicateSemantics(PredicateKind.RELATION, PredicateExclusivity.TEMPORAL, True),
        "parent_of": PredicateSemantics(PredicateKind.RELATION, PredicateExclusivity.MULTI_VALUED),
        "spouse_of": PredicateSemantics(PredicateKind.RELATION, PredicateExclusivity.TEMPORAL, True),
        "created_by": PredicateSemantics(PredicateKind.RELATION, PredicateExclusivity.EXCLUSIVE),
        "is": PredicateSemantics(PredicateKind.ATTRIBUTE, PredicateExclusivity.MULTI_VALUED),
    }

    def get(self, predicate: str) -> PredicateSemantics:
        return self._SEMANTICS.get(
            predicate.strip().casefold(),
            PredicateSemantics(PredicateKind.UNKNOWN, PredicateExclusivity.UNKNOWN),
        )
