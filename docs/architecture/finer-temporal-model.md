# Modèle temporel narratif fin

Le moteur de cohérence doit pouvoir distinguer une évolution narrative d'une contradiction sans réduire le temps à un simple numéro de chapitre.

## Modèle

`TemporalScope` conserve le contrat existant :

- `TIMELESS` représente une affirmation sans portée temporelle explicite ;
- `STORY_POINT` représente un point narratif avec `position`.

Un `STORY_POINT` peut maintenant préciser `end_position` pour représenter un intervalle inclusif. Quand `end_position` est absent, le scope reste un point unique.

La comparaison déterministe expose les relations suivantes :

- `BEFORE` : le scope gauche précède le droit ;
- `AFTER` : le scope gauche suit le droit ;
- `DURING` : le premier est contenu dans le second ;
- `CONTAINS` : le premier contient le second ;
- `OVERLAPS` : les intervalles se recouvrent sans relation de contenance ;
- `SIMULTANEOUS` : les deux scopes sont identiques.

Les positions sont discrètes et les intervalles sont inclusifs : deux intervalles qui partagent une position se recouvrent. Cela évite d'introduire une sémantique artificielle de frontière avant que le moteur ne dispose d'un temps plus fin que le rang narratif.

Un scope `TIMELESS` n'est pas ordonnable : `relation_to()` retourne `None`. `overlaps()` conserve toutefois le comportement historique et considère qu'un scope intemporel peut recouvrir un scope narratif, afin de ne pas transformer silencieusement les anciennes détections.

## Compatibilité

Aucun appelant existant n'a besoin de connaître les intervalles. `position` reste le champ canonique pour les scopes déjà persistés et les points narratifs existants restent valides.

Cette PR ne modifie volontairement pas la logique de `DetectConflicts`. La prochaine étape pourra utiliser les relations temporelles pour décider explicitement si deux assertions sont simultanées, successives ou réellement concurrentes.

## Limites

Ce modèle ne prétend pas encore représenter les événements, les croyances ou l'autorité des sources. Ces dimensions restent séparées afin de garder chaque étape testable et explicable.
