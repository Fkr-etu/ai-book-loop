from __future__ import annotations

from book_loop.application.services.hybrid_retrieval import HybridCanonicalRetriever
from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.application.services.retrieval_evaluation import RetrievalEvaluationCase, RetrievalEvaluator
from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact


# Source-grounded deterministic corpus extracted from Fkr-etu/M4ges Livre I.
# Only compact factual representations are stored here, not the manuscript prose.
# Hand-labelled vectors validate retrieval plumbing and fusion, not Gemini quality.
CORPUS = (
    ("c01", "Elara garde le Cœur de Borael dans le Grand Reliquaire de Val-D'Or", "relic"),
    ("c01", "La Cuirasse de Nacre d'Elara est forgée dans un alliage de métal et de résidus de Souffle", "armor"),
    ("c01", "Givre-Âme est la rapière d'Elara", "elara-weapon"),
    ("c01", "Lyra porte l'arme Éclat de Foi", "lyra-weapon"),
    ("c01", "La Purification doit ouvrir toutes les vannes de la Flèche Blanche", "purification"),
    ("c01", "Elara vole le Cœur de Borael et fuit la Flèche Blanche", "escape"),
    ("c01", "La jambe gauche d'Elara se pétrifie après son contact avec le Cœur", "petrification"),
    ("c01", "Le Talisman des Soupirs ralentit la progression de la pétrification d'Elara", "talisman"),
    ("c02", "Kael travaille dans les Forges de Fer-Noir du Consortium de Fer", "fer-noir"),
    ("c02", "La mère de Kael souffre de la Maladie du Froid", "mother"),
    ("c02", "Kael détourne le Noyau Thermique du Secteur 402 pour charger une Cellule de Stase Portative", "sabotage"),
    ("c02", "Le sabotage de Kael plonge le secteur 402 dans un froid immédiat", "consequence"),
    ("c02", "La Lentille de Résonance révèle que le Gisement Originel est délibérément siphonné", "siphoning"),
    ("c02", "Vestra ordonne la capture de Kael avec autorisation de force létale", "vestra"),
    ("c02", "Kael emporte la Lentille de Résonance dans les Bas-Fonds", "lens"),
    ("c02", "Kael quitte Fer-Noir avec la Cellule de Stase chargée pour sa mère", "exile"),
    ("c03", "Elara et Kael se rencontrent dans la plaine de scories", "meeting"),
    ("c03", "Kael utilise une Surchargeuse à Pistons comme arme", "kael-weapon"),
    ("c03", "Elara combat avec Givre-Âme malgré sa jambe de cristal", "injury"),
    ("c03", "Un Écho Prédateur de quatre mètres attaque Elara et Kael", "predator"),
    ("c03", "Kael fragilise les pattes de l'Écho avec une décharge thermique", "alliance"),
    ("c03", "Elara détruit le noyau de l'Écho Prédateur avec Givre-Âme", "finisher"),
    ("c03", "Elara et Kael décident de marcher ensemble vers Port-Argent", "port-argent"),
    ("c03", "Elara et Kael reconnaissent qu'ils ne se font pas confiance", "trust"),
)

QUERIES = (
    ("la relique gardée dans le sanctuaire de Val-D'Or", 0, "relic"),
    ("l'armure nacrée portée par Elara", 1, "armor"),
    ("l'épée personnelle d'Elara", 2, "elara-weapon"),
    ("l'arme lumineuse de Lyra", 3, "lyra-weapon"),
    ("ce qui doit être déclenché lors de la Purification", 4, "purification"),
    ("comment Elara s'enfuit avec la relique", 5, "escape"),
    ("ce qui arrive à la jambe d'Elara après avoir saisi le Cœur", 6, "petrification"),
    ("l'amulette qui freine le mal qui gagne Elara", 7, "talisman"),
    ("la cité industrielle d'où vient Kael", 8, "fer-noir"),
    ("la maladie dont souffre la mère de Kael", 9, "mother"),
    ("l'appareil que Kael charge en détournant le noyau", 10, "sabotage"),
    ("les conséquences du sabotage du secteur 402", 11, "consequence"),
    ("la découverte faite grâce à la Lentille sur l'origine de la pénurie", 12, "siphoning"),
    ("qui lance la traque de Kael", 13, "vestra"),
    ("le cristal qui permet d'analyser les flux du Souffle", 14, "lens"),
    ("ce que Kael emporte en quittant Fer-Noir pour aider sa mère", 15, "exile"),
    ("où Elara rencontre l'ingénieur de Fer-Noir", 16, "meeting"),
    ("l'arme mécanique fixée au bras de Kael", 17, "kael-weapon"),
    ("l'état de la jambe d'Elara pendant leur confrontation", 18, "injury"),
    ("le monstre géant qui surgit dans les scories", 19, "predator"),
    ("comment Kael aide Elara contre le monstre", 20, "alliance"),
    ("qui porte le coup final à l'Écho", 21, "finisher"),
    ("leur prochaine destination commune", 22, "port-argent"),
    ("ce qu'ils pensent de leur confiance mutuelle", 23, "trust"),
)

GROUPS = tuple(dict.fromkeys(group for _, _, group in CORPUS))
GROUP_VECTORS = {
    group: tuple(float(index == group_index) for index in range(len(GROUPS)))
    for group_index, group in enumerate(GROUPS)
}


def fact(chapter: str, index: int, statement: str) -> CanonicalFact:
    fact_id = f"livre1-{chapter}-{index}"
    return CanonicalFact(
        id=fact_id,
        book_id="livre-1",
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject=fact_id,
        predicate="est un fait",
        object=statement,
        decision_id=f"decision-{fact_id}",
        version=1,
    )


class BenchmarkProvider:
    query_vectors = {query: GROUP_VECTORS[group] for query, _, group in QUERIES}

    def embed(self, *, text: str) -> tuple[float, ...]:
        return self.query_vectors.get(text, (0.0,) * len(GROUPS))


class BenchmarkStore:
    entries = {
        f"livre1-{chapter}-{index}": CanonicalFactEmbedding(
            fact_id=f"livre1-{chapter}-{index}",
            embedding=GROUP_VECTORS[group],
            model="benchmark",
        )
        for index, (chapter, _, group) in enumerate(CORPUS)
    }

    def list_canonical_fact_embeddings(self, *, fact_ids: list[str]) -> dict[str, CanonicalFactEmbedding]:
        return {fact_id: self.entries[fact_id] for fact_id in fact_ids if fact_id in self.entries}


def test_retrieval_pipeline_regression_on_livre_1_corpus() -> None:
    facts = [fact(chapter, index, statement) for index, (chapter, statement, _) in enumerate(CORPUS)]
    cases = tuple(
        RetrievalEvaluationCase(
            query=query,
            relevant_fact_keys=frozenset({(facts[index].id, 1)}),
        )
        for query, index, _ in QUERIES
    )

    semantic = EmbeddingCanonicalRetriever(
        BenchmarkProvider(),
        embedding_store=BenchmarkStore(),
        embedding_model="benchmark",
        top_k=5,
    )
    lexical = CanonicalRetriever(top_k=5)
    hybrid = HybridCanonicalRetriever(lexical, semantic, top_k=5)
    evaluator = RetrievalEvaluator(k=5)

    lexical_report = evaluator.evaluate(lexical, facts, cases)
    semantic_report = evaluator.evaluate(semantic, facts, cases)
    hybrid_report = evaluator.evaluate(hybrid, facts, cases)

    assert semantic_report.mean_recall_at_k > lexical_report.mean_recall_at_k
    assert semantic_report.mean_reciprocal_rank > lexical_report.mean_reciprocal_rank
    assert semantic_report.hit_rate_at_k >= lexical_report.hit_rate_at_k
    assert hybrid_report.mean_recall_at_k >= lexical_report.mean_recall_at_k
    assert hybrid_report.hit_rate_at_k >= lexical_report.hit_rate_at_k
    assert hybrid_report.mean_reciprocal_rank >= lexical_report.mean_reciprocal_rank
