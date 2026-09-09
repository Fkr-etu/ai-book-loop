from __future__ import annotations

from book_loop.application.services.hybrid_retrieval import HybridCanonicalRetriever
from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.application.services.retrieval_evaluation import (
    RetrievalEvaluationCase,
    RetrievalEvaluator,
)
from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact


# A deterministic, hand-labelled corpus keeps the benchmark reproducible in CI while
# exercising the same retrieval path used by the application. The corpus deliberately
# contains several books and distractors with overlapping vocabulary.
CORPUS = (
    ("fantasy", "1", "Maëlle porte une amulette protectrice héritée de sa mère", "protection"),
    ("fantasy", "2", "Le vieux pont de pierre cache une entrée vers les catacombes", "passage"),
    ("fantasy", "3", "Le conseil interdit les sortilèges de feu dans la cité", "magic"),
    ("fantasy", "4", "Un corbeau blanc avertit Maëlle avant chaque danger", "omen"),
    ("fantasy", "5", "Le prince conserve une carte secrète des frontières du royaume", "map"),
    ("fantasy", "6", "La forge royale produit des lames en acier noir", "weapon"),
    ("fantasy", "7", "La rivière souterraine alimente les jardins du palais", "water"),
    ("fantasy", "8", "Une ancienne cloche sonne lorsque la lune atteint son zénith", "signal"),
    ("fantasy", "9", "Maëlle refuse de révéler le nom véritable du sorcier", "identity"),
    ("fantasy", "10", "Les gardes patrouillent autour de la porte nord chaque nuit", "guard"),
    ("fantasy", "11", "Le manuscrit décrit un rituel capable de briser une malédiction", "curse"),
    ("fantasy", "12", "Le village célèbre la récolte autour d'un grand feu", "festival"),
    ("thriller", "1", "Nora dissimule la clé USB dans la doublure de son manteau", "evidence"),
    ("thriller", "2", "La caméra du parking cesse d'enregistrer à vingt-trois heures", "surveillance"),
    ("thriller", "3", "Un témoin affirme avoir vu une berline noire devant l'entrepôt", "witness"),
    ("thriller", "4", "Le laboratoire conserve les échantillons dans une chambre froide", "laboratory"),
    ("thriller", "5", "Nora reçoit un message anonyme lui ordonnant de fuir la ville", "threat"),
    ("thriller", "6", "Le commissaire garde les dossiers de l'enquête dans un coffre", "investigation"),
    ("thriller", "7", "Le téléphone jetable sonne une seule fois avant de disparaître", "phone"),
    ("thriller", "8", "Le tunnel ferroviaire possède une sortie condamnée depuis dix ans", "tunnel"),
    ("thriller", "9", "Un badge falsifié permet d'entrer dans la zone sécurisée", "access"),
    ("thriller", "10", "La voiture de Nora porte une rayure profonde sur l'aile arrière", "vehicle"),
    ("thriller", "11", "Le rapport financier révèle des virements vers une société écran", "money"),
    ("thriller", "12", "Un journaliste conserve une copie de la preuve originale", "archive"),
    ("romance", "1", "Élise garde la lettre de Julien dans la poche de son manteau", "letter"),
    ("romance", "2", "Julien joue du piano chaque dimanche dans le petit café", "music"),
    ("romance", "3", "Le couple se retrouve près du phare après chaque dispute", "meeting"),
    ("romance", "4", "Élise rêve d'ouvrir une librairie au bord de la mer", "dream"),
    ("romance", "5", "La vieille maison familiale doit être vendue avant l'hiver", "house"),
    ("romance", "6", "Julien déteste les voyages en avion mais adore les trains", "travel"),
    ("romance", "7", "Une photo de leur premier été est accrochée au salon", "memory"),
    ("romance", "8", "Élise rencontre la sœur de Julien lors d'un dîner improvisé", "family"),
    ("romance", "9", "Le café ferme exceptionnellement pendant les travaux de la rue", "cafe"),
    ("romance", "10", "Julien promet de revenir avant la première neige", "promise"),
    ("romance", "11", "Élise cache ses billets de train dans un vieux roman", "ticket"),
    ("romance", "12", "Le phare reste allumé malgré la tempête qui approche", "lighthouse"),
)

QUERIES = (
    ("un talisman qui protège Maëlle", "fantasy", "1", "protection"),
    ("un passage dissimulé sous la ville", "fantasy", "2", "passage"),
    ("une interdiction concernant la magie", "fantasy", "3", "magic"),
    ("l'oiseau qui annonce les ennuis", "fantasy", "4", "omen"),
    ("le plan secret des limites du royaume", "fantasy", "5", "map"),
    ("la preuve cachée par Nora", "thriller", "1", "evidence"),
    ("le dispositif qui surveillait le parking", "thriller", "2", "surveillance"),
    ("la personne qui a aperçu la voiture", "thriller", "3", "witness"),
    ("le lieu où sont stockés les prélèvements", "thriller", "4", "laboratory"),
    ("le message qui menace Nora", "thriller", "5", "threat"),
    ("l'endroit où le commissaire cache les documents", "thriller", "6", "investigation"),
    ("la déclaration qui engage Julien à revenir", "romance", "10", "promise"),
    ("le souvenir photographique de leurs débuts", "romance", "7", "memory"),
    ("le rêve professionnel d'Élise", "romance", "4", "dream"),
    ("le lieu où ils se retrouvent après une querelle", "romance", "3", "meeting"),
    ("le document affectueux conservé par Élise", "romance", "1", "letter"),
    ("le moyen de transport préféré de Julien", "romance", "6", "travel"),
    ("le bâtiment qui continue à guider les bateaux", "romance", "12", "lighthouse"),
)

GROUP_VECTORS = {
    "protection": (1.0, 0.0, 0.0, 0.0, 0.0),
    "passage": (0.0, 1.0, 0.0, 0.0, 0.0),
    "magic": (0.0, 0.0, 1.0, 0.0, 0.0),
    "omen": (0.0, 0.0, 0.0, 1.0, 0.0),
    "map": (0.0, 0.0, 0.0, 0.0, 1.0),
    "evidence": (1.0, 1.0, 0.0, 0.0, 0.0),
    "surveillance": (1.0, 0.0, 1.0, 0.0, 0.0),
    "witness": (1.0, 0.0, 0.0, 1.0, 0.0),
    "laboratory": (1.0, 0.0, 0.0, 0.0, 1.0),
    "threat": (0.0, 1.0, 1.0, 0.0, 0.0),
    "investigation": (0.0, 1.0, 0.0, 1.0, 0.0),
    "promise": (0.0, 0.0, 1.0, 1.0, 0.0),
    "memory": (0.0, 0.0, 1.0, 0.0, 1.0),
    "dream": (0.0, 1.0, 1.0, 0.0, 1.0),
    "meeting": (0.0, 1.0, 0.0, 1.0, 1.0),
    "letter": (1.0, 1.0, 1.0, 0.0, 0.0),
    "travel": (1.0, 1.0, 0.0, 0.0, 1.0),
    "lighthouse": (1.0, 0.0, 1.0, 1.0, 1.0),
}


def fact(book_id: str, number: str, statement: str) -> CanonicalFact:
    fact_id = f"{book_id}-{number}"
    return CanonicalFact(
        id=fact_id,
        book_id=book_id,
        assertion_id=f"assertion-{fact_id}",
        statement=statement,
        subject=fact_id,
        predicate="est un fait",
        object=statement,
        decision_id=f"decision-{fact_id}",
        version=1,
    )


class BenchmarkProvider:
    query_vectors = {query: GROUP_VECTORS[group] for query, _, _, group in QUERIES}

    def embed(self, *, text: str) -> tuple[float, ...]:
        if text in self.query_vectors:
            return self.query_vectors[text]
        return GROUP_VECTORS.get(text, (0.0, 0.0, 0.0, 0.0, 0.0))


class BenchmarkStore:
    entries = {
        f"{book_id}-{number}": CanonicalFactEmbedding(
            fact_id=f"{book_id}-{number}",
            embedding=GROUP_VECTORS[group],
            model="benchmark",
        )
        for book_id, number, _, group in CORPUS
    }

    def list_canonical_fact_embeddings(
        self, *, fact_ids: list[str]
    ) -> dict[str, CanonicalFactEmbedding]:
        return {fact_id: self.entries[fact_id] for fact_id in fact_ids if fact_id in self.entries}


def test_retrieval_benchmark_on_multi_book_corpus() -> None:
    facts = [fact(book_id, number, statement) for book_id, number, statement, _ in CORPUS]
    cases = tuple(
        RetrievalEvaluationCase(
            query=query,
            relevant_fact_keys=frozenset({(f"{book_id}-{number}", 1)}),
        )
        for query, book_id, number, _ in QUERIES
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

    # The benchmark is intentionally diagnostic: semantic retrieval should add value
    # on paraphrased queries, while hybrid retrieval must not regress the lexical baseline.
    assert semantic_report.mean_recall_at_k > lexical_report.mean_recall_at_k
    assert semantic_report.mean_reciprocal_rank > lexical_report.mean_reciprocal_rank
    assert semantic_report.hit_rate_at_k >= lexical_report.hit_rate_at_k
    assert hybrid_report.mean_recall_at_k >= lexical_report.mean_recall_at_k
    assert hybrid_report.hit_rate_at_k >= lexical_report.hit_rate_at_k
    assert hybrid_report.mean_reciprocal_rank >= lexical_report.mean_reciprocal_rank
