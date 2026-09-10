# Audit de cohérence du Livre I sur corpus réel

Le script `scripts/audit_livre1_consistency.py` permet d'exécuter le détecteur de cohérence sur les huit chapitres réels du Livre I.

## Pourquoi cet audit est opt-in

L'audit utilise une clé Gemini pour extraire les assertions source-grounded. Le corpus est désormais versionné directement dans `tests/fixtures/livre1/` afin que l'exécution ne dépende ni du dépôt privé M4ges ni d'un téléchargement externe.

Il ne doit pas être exécuté dans la CI standard et ne contient aucun secret ni clé API dans le dépôt.

## Exécution locale

Le script attend par défaut le corpus versionné dans :

```text
tests/fixtures/livre1/
```

On peut utiliser un autre emplacement avec `LIVRE1_CORPUS_ROOT` :

```bash
GEMINI_API_KEY="..." \
LIVRE1_CORPUS_ROOT="/chemin/vers/livre1" \
python scripts/audit_livre1_consistency.py
```

Le modèle LLM peut être changé avec `LLM_MODEL` :

```bash
GEMINI_API_KEY="..." LLM_MODEL="gemini-3.5-flash" python scripts/audit_livre1_consistency.py
```

Le script réutilise le chemin d'ingestion réel (`IngestDocument` + `LLMAssertionExtractor`) puis exécute `DetectConflicts` avec un contexte temporel dérivé du numéro de chapitre.

## Qualification et benchmark

Le benchmark distingue volontairement quatre situations :

- **contradiction** : les deux assertions ne peuvent pas être vraies ensemble dans le même état narratif ;
- **évolution narrative légitime** : la valeur change avec le temps ;
- **reformulation compatible** : les deux assertions décrivent le même fait ;
- **bruit / mauvais rapprochement** : les assertions ne constituent pas une paire pertinente.

Le jeu synthétique de non-régression se trouve dans `tests/test_consistency_benchmark.py`. Il couvre maintenant aussi les prédicats sémantiques introduits par #224, notamment la possession multi-valuée.

Pour le corpus réel, les alertes doivent être annotées avant de modifier davantage le moteur. **Aucune qualification des 13 alertes observées lors du premier audit Gemini n'est inventée dans le dépôt** : les annotations doivent provenir de l'examen des assertions et de leurs preuves.

Les métriques `precision`, `recall` et `fpr` sont calculées par `scripts/consistency_benchmark.py`. La vérité terrain attendue est une mappe d'identifiants de candidats vers `GoldLabel`; elle doit être dérivée du snapshot d'alertes réellement observé.

Cette séparation permet de mesurer une nouvelle version du détecteur contre le même jeu annoté, plutôt que de juger son amélioration uniquement sur le nombre d'alertes produites.
