# Œil critique narratif

L'Œil critique est le sparring-partner narratif de Book Loop. Il intervient après le setup du livre pour challenger les choix de l'auteur au lieu de construire automatiquement une spécification narrative.

## Contrat

Chaque tour retourne une réponse structurée :

```json
{
  "reply": "...",
  "question": "...",
  "done": false
}
```

- `reply` : le challenge ou l'observation adressée à l'auteur.
- `question` : une seule question qui pousse l'auteur à approfondir ; `null` lorsque la session est terminée.
- `done` : indique que l'Œil critique estime que la session peut s'arrêter.

L'application impose également une limite dure de 8 tours.

## Personnalités

La personnalité est stockée avec le livre et injectée dans le system prompt :

- `challenger` — direct et exigeant.
- `editor` — analytique et précis.
- `devils_advocate` — recherche les contre-exemples.
- `demanding_kind` — chaleureux dans la forme, exigeant sur le fond.

La personnalité décrit une stratégie de confrontation narrative ; elle ne change pas le contrat de données.

## Coût et contexte

Le Grill utilise un modèle dédié configurable par `GRILL_LLM_MODEL`. Le modèle peut donc rester peu coûteux même si `LLM_MODEL` est configuré pour des tâches plus exigeantes.

Pour éviter l'explosion du contexte :

- seules les 12 dernières messages sont envoyés au modèle ;
- chaque message est limité à 2 000 caractères ;
- le contexte du livre est limité à 6 000 caractères ;
- la génération est limitée à 500 tokens.

L'historique n'est pas persisté par le backend dans le MVP : le client renvoie les messages nécessaires à chaque tour. Cela permet de conserver un modèle de données minimal et de ne pas transformer la conversation en état canonique.

## Architecture

Le cas d'usage `Grill` dépend uniquement du protocole `LLMProvider`. Gemini est sélectionné dans le composition root avec le modèle `GRILL_LLM_MODEL`. L'API est exposée sous `POST /api/books/{book_id}/grill`.

L'Œil critique ne modifie jamais `BookState`, le Canon, les assertions ou les documents. Les réponses de la conversation restent des propositions de réflexion de l'auteur jusqu'à une éventuelle action explicite ultérieure.

## Hors périmètre MVP

- CreativeSpec générée automatiquement.
- Résumé de session.
- Extraction de faits canoniques.
- Mémoire conversationnelle persistée.
- Routage intelligent entre plusieurs modèles.
