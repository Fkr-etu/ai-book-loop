from __future__ import annotations

from collections.abc import Iterable

from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import CanonicalKnowledgeRetriever


class HybridCanonicalRetriever:
    """Fuse lexical and semantic Canon rankings with deterministic RRF."""

    def __init__(
        self,
        lexical_retriever: CanonicalKnowledgeRetriever,
        semantic_retriever: CanonicalKnowledgeRetriever,
        *,
        top_k: int = 10,
        rrf_k: int = 60,
    ) -> None:
        if top_k < 0:
            raise ValueError("top_k must be non-negative")
        if rrf_k < 0:
            raise ValueError("rrf_k must be non-negative")
        self.lexical_retriever = lexical_retriever
        self.semantic_retriever = semantic_retriever
        self.top_k = top_k
        self.rrf_k = rrf_k

    def retrieve(self, facts: Iterable[CanonicalFact], *, query: str) -> list[CanonicalFact]:
        if self.top_k == 0 or not query.strip():
            return []

        candidates = list(facts)
        if not candidates:
            return []

        lexical = self.lexical_retriever.retrieve(candidates, query=query)
        semantic = self.semantic_retriever.retrieve(candidates, query=query)

        by_key = {(fact.id, fact.version): fact for fact in candidates}
        scores: dict[tuple[str, int], float] = {}

        for rank, fact in enumerate(lexical, start=1):
            key = (fact.id, fact.version)
            if key in by_key:
                scores[key] = scores.get(key, 0.0) + 1.0 / (self.rrf_k + rank)

        for rank, fact in enumerate(semantic, start=1):
            key = (fact.id, fact.version)
            if key in by_key:
                scores[key] = scores.get(key, 0.0) + 1.0 / (self.rrf_k + rank)

        ranked = [(score, by_key[key]) for key, score in scores.items()]
        ranked.sort(key=lambda item: (-item[0], item[1].id, item[1].version))
        return [fact for _, fact in ranked[: self.top_k]]
