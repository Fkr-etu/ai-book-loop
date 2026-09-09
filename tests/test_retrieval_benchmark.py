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
    ("c04", "Myra sauve Elara et Kael après leur affrontement avec l'Écho", "myra-rescue"),
    ("c04", "Myra est une mercenaire rencontrée sur la route de Port-Argent", "myra"),
    ("c04", "Myra conduit Elara et Kael jusqu'à Port-Argent", "arrival"),
    ("c04", "Elara et Kael acceptent l'aide de Myra malgré leur méfiance", "reluctant-help"),
    ("c05", "Le Marché aux Esprits vend des fragments de conscience de Djinns captifs", "spirit-market"),
    ("c05", "La Rose des Vents sert de refuge aux voyageurs à Port-Argent", "rose-des-vents"),
    ("c05", "Kael ressent de la culpabilité après le détournement du Secteur 402", "guilt"),
    ("c05", "Le trio enquête sur les trafics liés aux Djinns au Marché aux Esprits", "investigation"),
    ("c06", "Un Goliath-V attaque les protagonistes à proximité de Port-Argent", "goliath"),
    ("c06", "Valerius poursuit Elara en tant que son ancien mentor", "valerius"),
    ("c06", "Myra, Elara et Kael prennent la route vers le Cœur de Verre", "glass-heart"),
    ("c06", "Elara reconnaît Valerius comme son mentor avant leur fuite", "mentor"),
    ("c07", "L'Arbitre veut monétiser l'extinction des Djinns", "arbitre"),
    ("c07", "Un siphon sous le Palais de Verre extrait les ressources du Gisement", "palace-siphon"),
    ("c07", "Myra refuse de tuer Elara et Kael malgré la pression de l'Arbitre", "refusal"),
    ("c07", "Le trio découvre les installations du Palais de Verre", "discovery"),
    ("c08", "Kael découvre que l'Arbitre extrait des fréquences de mémoire du Gisement pour prolonger sa vie", "memory-frequencies"),
    ("c08", "Quatre Clés de Djinn sont nécessaires pour ouvrir le portail vers la Source", "four-keys"),
    ("c08", "Elara, Kael et Myra s'échappent du Palais de Verre", "escape-palace"),
    ("c08", "Le trio part vers l'est à la recherche du Gardien", "guardian"),
    ("c08", "Kael comprend que le Gisement est exploité pour prolonger une vie humaine", "understanding"),
    ("c08", "Les trois compagnons poursuivent leur route ensemble après leur fuite", "companions"),
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
    ("qui secourt Elara et Kael après le combat", 24, "myra-rescue"),
    ("le métier de Myra", 25, "myra"),
    ("dans quelle ville Myra les conduit", 26, "arrival"),
    ("pourquoi Elara et Kael acceptent l'aide de Myra", 27, "reluctant-help"),
    ("ce que vend le Marché aux Esprits", 28, "spirit-market"),
    ("le lieu qui sert de refuge à Port-Argent", 29, "rose-des-vents"),
    ("le sentiment de Kael après le Secteur 402", 30, "guilt"),
    ("ce que le trio enquête au Marché aux Esprits", 31, "investigation"),
    ("la créature qui attaque près de Port-Argent", 32, "goliath"),
    ("qui poursuit Elara depuis son passé", 33, "valerius"),
    ("vers quel lieu le trio se dirige après Port-Argent", 34, "glass-heart"),
    ("la relation passée entre Elara et Valerius", 35, "mentor"),
    ("ce que l'Arbitre veut faire de l'extinction des Djinns", 36, "arbitre"),
    ("où se trouve le siphon qui exploite le Gisement", 37, "palace-siphon"),
    ("pourquoi Myra refuse de tuer les deux fugitifs", 38, "refusal"),
    ("ce que découvre le trio au Palais de Verre", 39, "discovery"),
    ("ce que l'Arbitre extrait pour prolonger sa vie", 40, "memory-frequencies"),
    ("combien de Clés de Djinn ouvrent le portail", 41, "four-keys"),
    ("comment le trio quitte le Palais de Verre", 42, "escape-palace"),
    ("dans quelle direction ils partent après leur fuite", 43, "guardian"),
    ("ce que Kael comprend sur l'exploitation du Gisement", 44, "understanding"),
    ("ce que font les trois compagnons après leur fuite", 45, "companions"),
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


def test_retrieval_pipeline_regression_on_full_livre_1_corpus() -> None:
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
