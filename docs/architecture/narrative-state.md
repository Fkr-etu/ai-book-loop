# État narratif dynamique

Le moteur de cohérence ne doit pas considérer toutes les assertions comme des valeurs statiques. Certaines assertions décrivent un état qui peut évoluer, et cette évolution doit pouvoir être expliquée par un événement.

## V1

`book_loop/domain/narrative_state.py` introduit trois niveaux explicites :

- `NarrativeEvent` : événement situé dans le récit, avec sujet, position et preuves ;
- `StateTransition` : changement d'une valeur d'état, relié à l'événement qui l'explique ;
- `EntityNarrativeState` / `NarrativeStateTracker` : reconstruction déterministe de l'état courant et de son historique.

Exemple :

```text
Kael
  located_in = Unité de Recherche 403
       |
       | event: escape_403
       v
  located_in = Bas-Fonds
```

Chaque transition conserve sa provenance (`evidence_ids`), sa confiance et sa position narrative. Le tracker refuse les transitions non ordonnées, les événements inconnus et les transitions dont la valeur précédente ne correspond pas à l'état courant.

## Limites volontaires

Cette première étape ne :

- déduit pas automatiquement les événements depuis le texte ;
- ne remplace pas les assertions existantes ;
- ne modifie pas encore `DetectConflicts` ;
- n'introduit pas un graphe de propriétés temporel complet ;
- ne délègue aucune décision de cohérence au LLM.

Les événements et transitions constituent donc une représentation intermédiaire, testable et déterministe. Les prochaines étapes pourront brancher l'extraction, la temporalité fine et l'adjudication sur cette base sans réécrire le moteur de cohérence.
