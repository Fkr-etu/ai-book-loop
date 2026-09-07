from __future__ import annotations

import re
import unicodedata


class RuleBasedPredicateNormalizer:
    """Deterministic predicate normalizer with a small, explicit V1 vocabulary.

    The normalized value is domain-neutral (e.g. ``lives_in`` rather than a
    book-specific concept) so downstream consistency detectors can operate on
    claims independently of the source language.
    """

    _VOCABULARY: dict[str, dict[str, str]] = {
        "fr": {
            "age": "age",
            "a pour age": "age",
            "a l age": "age",
            "est age de": "age",
            "est âgé de": "age",
            "habite": "lives_in",
            "vit": "lives_in",
            "réside": "lives_in",
            "reside": "lives_in",
            "demeure": "lives_in",
            "est mort": "alive_status",
            "est morte": "alive_status",
            "est vivant": "alive_status",
            "est vivante": "alive_status",
            "métier": "occupation",
            "metier": "occupation",
            "profession": "occupation",
            "travaille comme": "occupation",
            "est": "is",
            "est un": "is",
            "est une": "is",
            "père de": "parent_of",
            "pere de": "parent_of",
            "mère de": "parent_of",
            "mere de": "parent_of",
            "parent de": "parent_of",
            "époux de": "spouse_of",
            "epoux de": "spouse_of",
            "épouse de": "spouse_of",
            "epouse de": "spouse_of",
            "marié à": "spouse_of",
            "marie a": "spouse_of",
            "mariée à": "spouse_of",
            "mariee a": "spouse_of",
            "situé à": "located_in",
            "situe a": "located_in",
            "se trouve à": "located_in",
            "se trouve a": "located_in",
            "créé par": "created_by",
            "cree par": "created_by",
            "appartient à": "belongs_to",
            "appartient a": "belongs_to",
        },
        "en": {
            "age": "age",
            "is aged": "age",
            "is age": "age",
            "lives in": "lives_in",
            "resides in": "lives_in",
            "resides at": "lives_in",
            "occupation": "occupation",
            "profession": "occupation",
            "works as": "occupation",
            "is dead": "alive_status",
            "is alive": "alive_status",
            "is": "is",
            "is a": "is",
            "is an": "is",
            "parent of": "parent_of",
            "father of": "parent_of",
            "mother of": "parent_of",
            "spouse of": "spouse_of",
            "married to": "spouse_of",
            "located in": "located_in",
            "located at": "located_in",
            "created by": "created_by",
            "belongs to": "belongs_to",
        },
    }

    def normalize(self, *, predicate: str, language: str = "fr") -> str:
        normalized_language = language.lower().split("-")[0].split("_")[0]
        value = self._normalize_text(predicate)
        if not value:
            raise ValueError("Predicate must not be empty")

        vocabulary = self._VOCABULARY.get(normalized_language, {})
        if value in vocabulary:
            return vocabulary[value]

        # Unknown predicates remain deterministic and language-neutral in shape.
        # We deliberately do not invent semantics that are not in the controlled
        # vocabulary; future language packs can add mappings safely.
        return re.sub(r"[^a-z0-9]+", "_", value).strip("_")

    @staticmethod
    def _normalize_text(value: str) -> str:
        ascii_value = "".join(
            char
            for char in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(char)
        )
        return re.sub(r"\s+", " ", ascii_value.strip().lower())
