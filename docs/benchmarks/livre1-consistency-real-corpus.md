# Audit de cohérence du Livre I sur corpus réel

Le script `scripts/audit_livre1_consistency.py` permet d'exécuter le détecteur de cohérence sur les huit chapitres réels du Livre I.

## Pourquoi cet audit est opt-in

L'audit utilise deux ressources externes :

1. les chapitres publics du dépôt `Fkr-etu/M4ges` ;
2. Gemini pour extraire les assertions source-grounded.

Il ne doit donc pas être exécuté dans la CI standard et ne contient aucun secret ni clé API.

## Exécution

```bash
GEMINI_API_KEY="..." python scripts/audit_livre1_consistency.py
```

Le modèle LLM peut être changé avec `LLM_MODEL` :

```bash
GEMINI_API_KEY="..." LLM_MODEL="gemini-2.5-flash" python scripts/audit_livre1_consistency.py
```

Le script réutilise le chemin d'ingestion réel (`IngestDocument` + `LLMAssertionExtractor`) puis exécute `DetectConflicts` avec un contexte temporel dérivé du numéro de chapitre.

## Ce que mesure le rapport

Pour chaque chapitre :

- nombre de chunks ;
- nombre d'assertions réellement extraites ;
- nombre d'alertes de contradiction produites sur l'ensemble du corpus.

Chaque alerte expose :

- les deux assertions ;
- leur chapitre / story point ;
- leur sujet, prédicat et objet ;
- leur confiance d'extraction.

## Qualification

Le résultat n'est pas une précision/recall automatique : le Livre I ne fournit pas de jeu de vérité terrain annoté.

Chaque alerte doit être classée manuellement en :

- vraie contradiction ;
- évolution narrative légitime ;
- reformulation compatible ;
- bruit / mauvais rapprochement.

Cette qualification est volontairement séparée de l'extraction. Elle évite d'introduire des attentes artificielles dans le benchmark et permet de décider ensuite si une nouvelle règle de détection est réellement nécessaire.
