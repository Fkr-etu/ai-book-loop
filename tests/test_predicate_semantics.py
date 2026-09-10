from __future__ import annotations

from book_loop.domain.predicate_semantics import (
    PredicateExclusivity,
    PredicateKind,
    PredicateSemanticsRegistry,
)


def test_registry_classifies_dynamic_location() -> None:
    semantics = PredicateSemanticsRegistry().get("located_in")

    assert semantics.kind is PredicateKind.LOCATION
    assert semantics.exclusivity is PredicateExclusivity.TEMPORAL
    assert semantics.supports_evolution is True


def test_registry_classifies_possession_as_multi_valued() -> None:
    semantics = PredicateSemanticsRegistry().get("owns")

    assert semantics.kind is PredicateKind.POSSESSION
    assert semantics.exclusivity is PredicateExclusivity.MULTI_VALUED
    assert semantics.supports_evolution is True


def test_unknown_predicates_are_conservative() -> None:
    semantics = PredicateSemanticsRegistry().get("predicate_not_yet_registered")

    assert semantics.kind is PredicateKind.UNKNOWN
    assert semantics.exclusivity is PredicateExclusivity.UNKNOWN
    assert semantics.supports_evolution is False
