# Autorité et état épistémique

Le moteur de cohérence ne doit pas traiter toute proposition comme un fait objectif.
Une même information peut être canonique, rapportée par une source, crue par un personnage,
hypothétique ou explicitement incertaine.

## Modèle

`AssertionEpistemic` porte trois dimensions indépendantes :

- `status` : `CANONICAL`, `REPORTED`, `BELIEVED`, `HYPOTHESIS` ou `UNCERTAIN` ;
- `authority` : `CANONICAL`, `NARRATOR`, `SOURCE`, `CHARACTER` ou `INFERRED` ;
- `reliability` : score entre 0 et 1 représentant la fiabilité estimée de la source.

L'autorité est ordonnée pour permettre une comparaison déterministe :

`INFERRED < CHARACTER < SOURCE < NARRATOR < CANONICAL`.

Une assertion `CANONICAL` doit obligatoirement porter l'autorité `CANONICAL`.

## Effet sur la cohérence

Le moteur distingue désormais deux situations :

1. **Contradiction candidate** : deux affirmations de force comparable peuvent être
   incompatibles et restent transmises au moteur de conflit.
2. **Désaccord épistémique** : une croyance, hypothèse ou information incertaine ne
   doit pas être transformée automatiquement en contradiction avec un fait plus fort.
   La paire reçoit `EPISTEMIC_DEFERRED` et devra être arbitrée avec son contexte.

Une différence d'autorité est également différée lorsque l'affirmation la plus autoritaire
est au moins aussi fiable que l'affirmation plus faible. Une affirmation de moindre autorité
mais de fiabilité supérieure n'est pas masquée automatiquement : elle reste candidate à
l'adjudication.

## Compatibilité et limites

Le modèle est introduit sans modifier la représentation persistée de `Assertion`.
`AssertionEpistemicStore` est donc un port optionnel et rétrocompatible : en son absence,
le comportement existant reste inchangé.

Cette étape ne choisit pas quelle assertion est vraie et n'appelle pas de LLM. Elle prépare
le terrain pour une future adjudication fondée sur un mini-graphe déterministe, avec preuve,
autorité, temporalité et état épistémique explicitement fournis au modèle.

La prochaine étape pourra persister ces métadonnées et définir un contrat d'adjudication
strict (`CONTRADICTION`, `EVOLUTION`, `AMBIGU`) sans redonner au LLM la responsabilité de
reconstruire tout le contexte narratif.
