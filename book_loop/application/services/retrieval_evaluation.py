from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import CanonicalKnowledgeRetriever


@dataclass(frozen=True)
class RetrievalEvaluationCase:
    query: str
    relevant_fact_keys: frozenset[tuple[str, int]]


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    precision_at_k: float
    recall_at_k: float
    hit_at_k: bool
    mean_reciprocal_rank: float


@dataclass(frozen=True)
class RetrievalEvaluationReport:
    cases: tuple[RetrievalEvaluationResult, ...]
    mean_precision_at_k: float
    mean_recall_at_k: float
    hit_rate_at_k: float
    mean_reciprocal_rank: float


class RetrievalEvaluator:
    """Evaluate any Canon retriever against a reproducible relevance set."""

    def __init__(self, *, k: int = 5) -> None:
        if k <= 0:
            raise ValueError("k must be positive")
        self.k = k

    def evaluate_case(
        self,
        retriever: CanonicalKnowledgeRetriever,
        facts: Iterable[CanonicalFact],
        case: RetrievalEvaluationCase,
    ) -> RetrievalEvaluationResult:
        candidates = list(facts)
        ranked = retriever.retrieve(candidates, query=case.query)[: self.k]
        relevant = case.relevant_fact_keys
        retrieved_keys = [(fact.id, fact.version) for fact in ranked]
        relevant_retrieved = sum(key in relevant for key in retrieved_keys)

        precision = relevant_retrieved / len(ranked) if ranked else 0.0
        recall = relevant_retrieved / len(relevant) if relevant else 0.0
        reciprocal_rank = 0.0
        for rank, key in enumerate(retrieved_keys, start=1):
            if key in relevant:
                reciprocal_rank = 1.0 / rank
                break

        return RetrievalEvaluationResult(
            precision_at_k=precision,
            recall_at_k=recall,
            hit_at_k=bool(relevant_retrieved),
            mean_reciprocal_rank=reciprocal_rank,
        )

    def evaluate(
        self,
        retriever: CanonicalKnowledgeRetriever,
        facts: Iterable[CanonicalFact],
        cases: Sequence[RetrievalEvaluationCase],
    ) -> RetrievalEvaluationReport:
        if not cases:
            raise ValueError("cases must not be empty")

        results = tuple(self.evaluate_case(retriever, facts, case) for case in cases)
        count = len(results)
        return RetrievalEvaluationReport(
            cases=results,
            mean_precision_at_k=sum(r.precision_at_k for r in results) / count,
            mean_recall_at_k=sum(r.recall_at_k for r in results) / count,
            hit_rate_at_k=sum(r.hit_at_k for r in results) / count,
            mean_reciprocal_rank=sum(r.mean_reciprocal_rank for r in results) / count,
        )
