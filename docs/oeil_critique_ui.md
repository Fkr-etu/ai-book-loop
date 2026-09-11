# Œil critique — intégration dans le Studio

L’Œil critique apparaît dans la surface d’écriture uniquement après une pause de l’auteur. Il ne lance aucune requête LLM au chargement et ne force jamais l’ouverture de la conversation.

## Déclenchement

- Le délai démarre lorsque l’auteur entre dans l’éditeur.
- Après 8 secondes sans modification, une proposition discrète apparaît.
- Toute nouvelle saisie réinitialise le délai.
- « Pas maintenant » masque la proposition pour le chapitre courant.
- Une session démarrée n’est pas relancée automatiquement.

Le délai est volontairement heuristique : il ne prétend pas détecter sémantiquement un blocage. Il sert de signal léger au moment où l’auteur semble hésiter.

## Interaction

La proposition demande explicitement à l’auteur s’il veut un regard extérieur. Une fois acceptée, l’Œil critique s’affiche au-dessus du manuscrit et pose une seule question à la fois.

Les réponses restent en mémoire côté client pendant la session afin de conserver le contexte conversationnel. Elles ne sont pas transformées en faits ni en éléments du Canon.

## Coût

Le frontend ne pré-génère aucune question et n’appelle le LLM qu’après l’action explicite de l’auteur. Le backend conserve les garde-fous de coût : modèle dédié, historique borné et maximum de 8 tours.
