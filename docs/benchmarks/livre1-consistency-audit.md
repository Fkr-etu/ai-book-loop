# Audit de cohérence — Livre I

## Objectif

Vérifier le comportement du détecteur de contradictions sur des assertions réellement présentes dans le corpus **Fkr-etu/M4ges — Livre I**, après l'introduction du contexte temporel.

Cette première passe est volontairement diagnostique : elle ne prétend pas mesurer une précision globale du détecteur. Les assertions sont une représentation factuelle compacte du manuscrit, comme pour le benchmark de retrieval, et non une extraction automatique complète par LLM.

## Périmètre

Six assertions de localisation, réparties sur les chapitres 1, 2, 4 et 8 :

| Personnage | Chapitre | Localisation |
| --- | ---: | --- |
| Elara | 1 | Val-D'Or |
| Elara | 4 | Port-Argent |
| Elara | 8 | Marches Orientales |
| Kael | 2 | Fer-Noir |
| Kael | 4 | Port-Argent |
| Kael | 8 | Marches Orientales |

Les six paires ayant le même sujet et le même prédicat mais des objets différents sont des **candidates structurelles**. Elles correspondent toutefois à des positions narratives différentes.

## Résultat

- Assertions analysées : **6**
- Paires candidates structurelles : **6**
- Paires entre positions narratives distinctes : **6**
- Contradictions détectées : **0**
- Évolutions narratives légitimes conservées comme non-conflictuelles : **6**

Le résultat est conforme à l'intention du modèle temporel : un changement d'état entre deux points de l'histoire ne doit pas devenir une alerte de contradiction.

## Lecture qualitative

### Elara

- chapitre 1 → Val-D'Or
- chapitre 4 → Port-Argent
- chapitre 8 → Marches Orientales

Ce sont trois états successifs du récit, pas trois affirmations incompatibles au même instant.

### Kael

- chapitre 2 → Fer-Noir
- chapitre 4 → Port-Argent
- chapitre 8 → Marches Orientales

Même constat : les six comparaisons sont structurellement proches, mais leur contexte temporel les rend compatibles.

## Limites

Cette passe ne permet pas encore de mesurer les faux positifs/faux négatifs sur l'ensemble du manuscrit :

1. elle n'est pas une extraction exhaustive des assertions du Livre I ;
2. elle ne contient pas de vérité terrain exhaustive permettant de classer toutes les alertes ;
3. elle ne couvre pas encore les contradictions réelles potentielles, les reformulations compatibles et le bruit à l'échelle des huit chapitres.

La prochaine étape est donc d'alimenter ce même audit avec le résultat réel de l'extraction d'assertions sur les huit chapitres, puis de qualifier les alertes produites avant de modifier les règles du détecteur.
