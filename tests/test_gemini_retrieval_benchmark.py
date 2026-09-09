from __future__ import annotations

import os

import pytest

from book_loop.application.services.hybrid_retrieval import HybridCanonicalRetriever
from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.application.services.retrieval_evaluation import (
    RetrievalEvaluationCase,
    RetrievalEvaluator,
)
from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact
from book_loop.infrastructure.embeddings.gemini import GeminiEmbeddingProvider
from tests.test_retrieval_benchmark import CORPUS, QUERIES, fact


pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Set GEMINI_API_KEY to run the opt-in Gemini quality benchmark",
)


class GeminiBenchmarkStore:
    def __init__(self, provider: GeminiEmbeddingProvider) -> None:
        self.entries: dict[str, CanonicalFactEmbedding] = {}
        self.provider = provider

    def list_canonical_fact_embeddings(
        self, *, fact_ids: list[str]
    ) -> dict[str, CanonicalFactEmbedding]:
        return {fact_id: self.entries[fact_id] for fact_id in fact_ids if fact_id in self.entries}

    def index(self, facts: list[CanonicalFact]) -> None:
        for item in facts:
            embedding = self.provider.embed(text=item.statement)
            self.entries[item.id] = CanonicalFactEmbedding(
                fact_id=item.id,
                embedding=tuple(embedding),
                model=self.provider.model,
            )


def test_gemini_retrieval_quality_benchmark() -> None:
    """Measure real Gemini semantic quality without making it a CI gate.

    This benchmark uses the same source-grounded corpus and labels as the
    deterministic regression test, but replaces hand-labelled vectors with real
    Gemini embeddings. Run it manually with GEMINI_API_KEY set. The printed metrics
    are evidence for a retrieval-quality decision, not a pass/fail product requirement.
    """
    model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    provider = GeminiEmbeddingProvider(
        api_key=os.environ["GEMINI_API_KEY"],
        model=model,
    )
    facts = [
        fact(chapter, index, statement)
        for index, (chapter, statement, _) in enumerate(CORPUS)
    ]
    cases = tuple(
        RetrievalEvaluationCase(
            query=query,
            relevant_fact_keys=frozenset({(facts[index].id, 1)}),
        )
        for query, index, _ in QUERIES
    )

    store = GeminiBenchmarkStore(provider)
    store.index(facts)
    semantic = EmbeddingCanonicalRetriever(
        provider,
        embedding_store=store,
        embedding_model=model,
        top_k=5,
    )
    lexical = CanonicalRetriever(top_k=5)
    hybrid = HybridCanonicalRetriever(lexical, semantic, top_k=5)
    evaluator = RetrievalEvaluator(k=5)

    lexical_report = evaluator.evaluate(lexical, facts, cases)
    semantic_report = evaluator.evaluate(semantic, facts, cases)
    hybrid_report = evaluator.evaluate(hybrid, facts, cases)

    print("\nGemini retrieval benchmark")
    print(f"model={model}")
    for name, report in (
        ("lexical", lexical_report),
        ("semantic", semantic_report),
        ("hybrid", hybrid_report),
    ):
        print(
            f"{name}: precision@5={report.mean_precision_at_k:.3f} "
            f"recall@5={report.mean_recall_at_k:.3f} "
            f"hit@5={report.hit_rate_at_k:.3f} "
            f"mrr={report.mean_reciprocal_rank:.3f}"
        )

    for report in (semantic_report, hybrid_report):
        assert 0.0 <= report.mean_precision_at_k <= 1.0
        assert 0.0 <= report.mean_recall_at_k <= 1.0
        assert 0.0 <= report.hit_rate_at_k <= 1.0
        assert 0.0 <= report.mean_reciprocal_rank <= 1.0
