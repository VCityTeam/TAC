# Compte rendu : point d'avancement avec John

**Date :** 28 août 2026
**Participants :** Rida, John
**Périodicité :** premier point depuis un mois, l'intervalle s'explique par la période de vacances

---

## 1. Contexte

Le projet a bien avancé pendant cette période. Ce point avait pour objectif de présenter à John l'état des deux approches explorées et de discuter des résultats d'évaluation obtenus.

---

## 2. Ce qui a été présenté

Les deux approches ont été exposées, ainsi que leur protocole d'évaluation respectif :

| Approche | Principe | État |
| --- | --- | --- |
| **RAG** | Recherche dans une base vectorielle et un graphe de connaissance, puis génération à partir du contexte récupéré | Évaluation en cours |
| **Fine-tuning** | Affinage par instruction sur des paires question / réponse construites à partir du corpus | Évaluation terminée sur trois modèles |

Pour l'approche fine-tuning, trois modèles ont été affinés et évalués : **Llama**, **Mistral** et **Qwen**.

---

## 3. Discussion : la pertinence des métriques

### 3.1 Le constat

Les résultats obtenus avec la précision, le rappel et le F1 sont faibles : la meilleure valeur observée se situe autour de **0,25**.

### 3.2 L'explication proposée

Ces scores ne reflètent pas fidèlement la qualité réelle des sorties. La comparaison est faite en **correspondance exacte de chaîne**, caractère par caractère. Or un modèle de langue produit fréquemment un synonyme ou une variante lexicale qui est sémantiquement correct, mais que la métrique compte comme une erreur.

**Exemple du mécanisme :** si le terme attendu est « justice de paix » et que le modèle produit « justices de paix », la réponse est comptée comme fausse alors qu'elle est acceptable pour un documentaliste.

### 3.3 L'ajout des agrégations micro et macro

Pour affiner la lecture, deux modes d'agrégation ont été introduits :

| Agrégation | Méthode de calcul | Ce qui pèse dans le résultat |
| --- | --- | --- |
| **Macro** | Calculer P, R et F1 pour chaque concept séparément, puis faire la moyenne de ces scores | Chaque concept compte pour un, quel que soit le nombre de termes qu'il a produits |
| **Micro** | Additionner l'ensemble des TP, FP et FN du jeu de test, puis calculer P, R et F1 une seule fois | Chaque terme compte pour un, donc un concept qui produit beaucoup de termes pèse davantage |

L'écart entre les deux est informatif : lorsque la micro est nettement plus basse que la macro, ce sont les concepts produisant beaucoup de termes qui se trompent le plus.

### 3.4 La position de John

John n'a pas validé cette partie en l'état. Sa demande : **appuyer le choix des métriques sur des références bibliographiques**, puisque les deux agrégations sont rapportées conjointement et que cette pratique doit être justifiée plutôt que décidée par convenance.

---

## 4. Décision principale : refaire l'annotation des données

### 4.1 La méthode actuelle

Le jeu d'entraînement du fine-tuning a été construit en formulation directe, une seule tournure par tâche :

```
Question : Donne-moi le concept complet correspondant à ce terme.
Réponse  : [concept complet généré à partir du corpus]
```

### 4.2 La limite relevée

Une formulation unique et invariante n'entraîne le modèle qu'à une seule manière de recevoir la demande. En situation réelle, la question sera posée autrement, et le modèle risque de moins bien la comprendre.

### 4.3 La proposition de John

Introduire des **patrons de formulation** (patterns) pour diversifier les questions du jeu d'entraînement. La logique est la même que celle du prompt engineering : mieux la question est structurée et variée, mieux le modèle apprend à identifier ce qui lui est demandé.

### 4.4 Répartition envisagée

| Type d'annotation | Part visée | Objectif |
| --- | --- | --- |
| Formulation directe | 30 % | Conserver le cas simple déjà maîtrisé |
| Formulation par patrons | 50 % | Apprendre au modèle à reconnaître des tournures variées |
| Autres formulations | 20 % | Cas dégradés, reformulations, langues mêlées |

*Répartition indicative, à arrêter définitivement avant de relancer la génération du jeu de données.*

---

## 5. Prochaines étapes

| Priorité | Action | Échéance |
| --- | --- | --- |
| 1 | Terminer l'évaluation de l'approche RAG | Semaine prochaine |
| 2 | Rechercher les références justifiant le choix des métriques micro et macro | À planifier |
| 3 | Refaire l'annotation du jeu d'entraînement avec des patrons de formulation | Après validation de la répartition |

---

## 6. Points à retenir

- Les scores faibles ne signifient pas nécessairement que l'approche échoue : la métrique elle-même est trop stricte pour du texte généré.
- La justification bibliographique des métriques est un préalable, pas une formalité : c'est ce qui rendra les résultats défendables.
- La qualité du jeu d'entraînement, et notamment la variété des formulations, est identifiée comme le principal levier d'amélioration du fine-tuning.
