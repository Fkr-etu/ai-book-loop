from book_loop.application.services.hybrid_retrieval import HybridCanonicalRetriever
from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.application.services.retrieval_evaluation import RetrievalEvaluationCase, RetrievalEvaluator
from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact


def fact(fact_id: str, statement: str) -> CanonicalFact:
    return CanonicalFact(
        id=fact_id,
        book_id="book-1",
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject=fact_id,
        predicate="has fact",
        object=statement,
        decision_id=f"decision-{fact_id}",
        version=1,
    )


class BenchmarkProvider:
    vectors = {
        "protective charm": (1.0, 0.0, 0.0),
        "hidden heirloom": (0.0, 1.0, 0.0),
    }

    def embed(self, *, text: str) -> tuple[float, ...]:
        return self.vectors.get(text, (0.0, 0.0, 1.0))


class BenchmarkStore:
    entries = {
        "amulet": CanonicalFactEmbedding(fact_id="amulet", embedding=(1.0, 0.0, 0.0), model="benchmark"),
        "heirloom": CanonicalFactEmbedding(fact_id="heirloom", embedding=(0.0, 1.0, 0.0), model="benchmark"),
        "noise": CanonicalFactEmbedding(fact_id="noise", embedding=(0.0, 0.0, 1.0), model="benchmark"),
    }

    def list_canonical_fact_embeddings(self, *, fact_ids: list[str]) -> dict[str, CanonicalFactEmbedding]:
        return {fact_id: self.entries[fact_id] for fact_id in fact_ids if fact_id in self.entries}


def test_retrieval_benchmark_shows_semantic_gain_without_harming_hybrid() -> None:
    facts = [
        fact("amulet", "Mira carries a protective amulet"),
        fact("heirloom", "The old ring is a hidden family heirloom"),
        fact("noise", "The harbor bell rings at dawn"),
    ]
    cases = (
        RetrievalEvaluationCase(
            query="protective charm",
            relevant_fact_keys=frozenset({("amulet", 1)}),
        ),
        RetrievalEvaluationCase(
            query="hidden heirloom",
            relevant_fact_keys=frozenset({("heirloom", 1)}),
        ),
    )
    semantic = EmbeddingCanonicalRetriever(
        BenchmarkProvider(), embedding_store=BenchmarkStore(), embedding_model="benchmark", top_k=2
    )
    lexical = CanonicalRetriever(top_k=2)
    hybrid = HybridCanonicalRetriever(lexical, semantic, top_k=2)
    evaluator = RetrievalEvaluator(k=2)

    lexical_report = evaluator.evaluate(lexical, facts, cases)
    semantic_report = evaluator.evaluate(semantic, facts, cases)
    hybrid_report = evaluator.evaluate(hybrid, facts, cases)

    assert semantic_report.mean_reciprocal_rank > lexical_report.mean_reciprocal_rank
    assert semantic_report.mean_recall_at_k > lexical_report.mean_recall_at_k
    assert hybrid_report.mean_recall_at_k >= lexical_report.mean_recall_at_k
    assert hybrid_report.mean_reciprocal_rank >= lexical_report.mean_reciprocal_rank
