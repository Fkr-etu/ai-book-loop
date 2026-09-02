from __future__ import annotations

import re
from collections.abc import Iterable

from book_loop.domain.models import CanonicalFact


_TOKEN_RE = re.compile(r"[\wÀ-ÖØ-öø-ÿ]+", re.UNICODE)


class CanonicalRetriever:
    """Retrieve active Canon facts with deterministic lexical scoring."""

    def __init__(self, *, top_k: int = 10, min_score: int = 1) -> None:
        if top_k < 0:
            raise ValueError("top_k must be non-negative")
        if min_score < 0:
            raise ValueError("min_score must be non-negative")
        self.top_k = top_k
        self.min_score = min_score

    def retrieve(self, facts: Iterable[CanonicalFact], *, query: str) -> list[CanonicalFact]:
        query_tokens = self._tokens(query)
        if not query_tokens or self.top_k == 0:
            return []

        ranked: list[tuple[int, CanonicalFact]] = []
        for fact in facts:
            fact_tokens = self._tokens(
                " ".join((fact.statement, fact.subject, fact.predicate, fact.object))
            )
            score = len(query_tokens & fact_tokens)
            if score >= self.min_score:
                ranked.append((score, fact))

        ranked.sort(key=lambda item: (-item[0], item[1].id, item[1].version))
        return [fact for _, fact in ranked[: self.top_k]]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token.casefold() for token in _TOKEN_RE.findall(text)}
