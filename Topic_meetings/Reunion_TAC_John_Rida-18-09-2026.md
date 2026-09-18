# Compte rendu de réunion

**Date :** 18 septembre 2026

**Objet :** Évaluation du fine-tuning (brique 0 et brique ALL) et choix de la méthodologie d'évaluation

## Contexte

La réunion était initialement programmée la semaine dernière, mais elle a été reportée à
cette semaine en raison d'une opération de maintenance sur le serveur de Versailles.

## Contenu présenté

Nous avons présenté deux volets :

1. L'évaluation de base réalisée sur le thésaurus.
2. L'évaluation des sorties du fine-tuning pour la brique 0 et la brique ALL,
   mesurée par similarité.

Pour ce second volet, nous avons montré le tableau de statistiques descriptives
des scores de similarité, la distribution de ces scores, ainsi que des exemples
de concepts générés.

## Remarques de John et actions à mener

### 1. Harmoniser la taille du jeu de test

Les deux configurations ne sont pas comparables en l'état : la brique 0 est évaluée
sur 541 exemples, la brique ALL sur 360. Cette différence vient de la suppression
des doublons effectuée pour la brique ALL.

**Action :** réévaluer les deux configurations sur le même jeu de 360 exemples dédoublonnés.

### 2. Utiliser les mêmes exemples dans les deux briques

Pour les trois modèles (Llama, Mistral, Qwen), les deux concepts illustrés en brique 0
ne sont pas ceux retenus en brique ALL, et les attributs mis en avant diffèrent également.
La comparaison entre les deux configurations en devient difficile à lire.

**Action :** reprendre les mêmes concepts et les mêmes attributs dans les deux briques.

## Limite de l'évaluation par similarité

Les résultats de similarité sont globalement bons, mais la similarité seule reste une
métrique d'évaluation faible. Nous allons donc adopter une autre approche, décrite dans
un article de référence que nous avons discuté en séance, exemples à l'appui.

Le point qui reste à clarifier dans cet article est l'absence de relation directe entre
les termes. Une relecture approfondie est prévue pour vérifier si un élément nous a échappé.

## Méthode envisagée avant la lecture de l'article

Avant d'étudier cet article, une méthode avait été développée pour dériver des métriques
à partir des scores de similarité :

1. Définir un seuil de similarité au-delà duquel deux termes A et B sont considérés
   comme équivalents.
2. Construire à partir de ce seuil une table de correspondances positives et négatives.

Cette méthode permet de déterminer les vrais positifs et les faux positifs :

- si `sim(A, B) >= seuil` alors `TP = 1` et `FP = 0` ;
- si `sim(A, B) < seuil` alors `TP = 0` et `FP = 1`.

Elle ne permet en revanche pas de calculer les vrais négatifs ni les faux négatifs,
faute de vérité terrain. L'idée d'utiliser un LLM pour produire cette vérité terrain a
été évoquée, mais elle pose un problème de circularité : le même type de modèle servirait
à la fois à la génération et à la vérification.

## Décision

Nous retenons la méthodologie de l'article, qui a l'avantage d'être définie par des
spécialistes du domaine et validée pour ce type d'évaluation.
