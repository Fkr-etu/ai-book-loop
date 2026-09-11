# Œil critique — intégration dans le Studio

L’Œil critique est proposé **dans la surface d’écriture**, et non comme une fonctionnalité séparée. L’objectif est de l’introduire uniquement lorsque l’auteur semble avoir besoin d’un regard extérieur.

## Déclenchement

- Le Studio n’affiche pas la proposition au chargement.
- Le minuteur démarre lorsque l’auteur entre dans l’éditeur.
- Après 8 secondes sans modification, une proposition discrète apparaît au-dessus du manuscrit.
- Toute nouvelle saisie réinitialise ce délai.
- « Pas maintenant » masque la proposition pour le chapitre courant.
- Une fois la session démarrée ou fermée après une réponse, elle n’est pas relancée automatiquement pour ce chapitre.

Le délai est un heuristique UX, pas une détection sémantique d’un blocage. Il évite d’ajouter une popup intrusive tout en intervenant pendant une pause suffisamment longue pour être significative.

## Interaction

La proposition demande explicitement la permission de faire intervenir l’Œil critique. Elle ne lance donc jamais une requête LLM sans action de l’auteur.

La conversation s’affiche au même endroit que l’écriture :

1. l’Œil critique formule son observation ;
2. il pose une seule question ;
3. l’auteur répond ;
4. la réponse repart au LLM avec l’historique de la session ;
5. le cycle continue jusqu’à la fin de session.

Les réponses ne sont pas persistées comme faits, ni ajoutées au Canon.

## Coût et garde-fous

Le frontend utilise l’endpoint dédié déjà limité côté application : modèle peu coûteux, historique borné et maximum de 8 tours. Le frontend ne pré-génère pas de questions et ne fait aucune requête avant que l’auteur n’accepte la proposition.

## Personnalité

Le livre expose `grillPersonality`. L’interface affiche cette personnalité dans l’en-tête de la conversation, tandis que le comportement réel reste déterminé par le prompt système côté application.

La sélection visuelle des personnalités dans le setup reste une tranche UI distincte ; la valeur par défaut est `challenger` lorsque le livre n’en fournit pas.
