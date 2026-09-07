from __future__ import annotations

import pytest

from book_loop.infrastructure.nlp.predicate_normalizer import RuleBasedPredicateNormalizer


@pytest.fixture
def normalizer() -> RuleBasedPredicateNormalizer:
    return RuleBasedPredicateNormalizer()


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        ("habite", "lives_in"),
        ("réside", "lives_in"),
        ("profession", "occupation"),
        ("métier", "occupation"),
        ("père de", "parent_of"),
        ("mère de", "parent_of"),
        ("époux de", "spouse_of"),
        ("situé à", "located_in"),
        ("créé par", "created_by"),
        ("appartient à", "belongs_to"),
    ],
)
def test_normalizes_french_predicates(normalizer: RuleBasedPredicateNormalizer, predicate: str, expected: str) -> None:
    assert normalizer.normalize(predicate=predicate, language="fr") == expected


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        ("lives in", "lives_in"),
        ("resides in", "lives_in"),
        ("occupation", "occupation"),
        ("father of", "parent_of"),
        ("married to", "spouse_of"),
        ("located in", "located_in"),
        ("created by", "created_by"),
    ],
)
def test_normalizes_english_predicates(normalizer: RuleBasedPredicateNormalizer, predicate: str, expected: str) -> None:
    assert normalizer.normalize(predicate=predicate, language="en") == expected


def test_normalization_is_case_and_whitespace_insensitive(normalizer: RuleBasedPredicateNormalizer) -> None:
    assert normalizer.normalize(predicate="  RÉSIDE   ", language="fr") == "lives_in"


def test_unknown_predicate_is_stable_and_does_not_invent_semantics(normalizer: RuleBasedPredicateNormalizer) -> None:
    assert normalizer.normalize(predicate="has favorite color", language="fr") == "has_favorite_color"


def test_empty_predicate_is_rejected(normalizer: RuleBasedPredicateNormalizer) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        normalizer.normalize(predicate="   ", language="fr")


def test_language_region_codes_are_supported(normalizer: RuleBasedPredicateNormalizer) -> None:
    assert normalizer.normalize(predicate="lives in", language="en-US") == "lives_in"
    assert normalizer.normalize(predicate="habite", language="fr-FR") == "lives_in"
