## Compte rendu : point d'avancement du projet

### Objet de la réunion

Ce point d'avancement m'a servi à présenter les résultats de la génération de concepts pour toutes les briques de prompt (brique 0, 1, 2, 3, 4 et ALL). Je les ai évalués de trois façons :

- la similarité cosinus ;
- la précision, le rappel et le F1 classiques (méthode **crisp**) ;
- la méthode **soft** de l'article de Fränti et al. (2023).

### Présentation de l'article

La réunion a commencé par une présentation rapide de l'article et de sa méthodologie. L'article compare deux approches :

- **Crisp** : la méthode habituelle pour calculer P, R et F1. Deux termes se correspondent seulement s'ils sont strictement identiques.
- **Soft** : une méthode fondée sur la cardinalité souple. Elle pondère la relation entre les termes de référence et les termes prédits, ce qui permet de tenir compte de correspondances proches mais pas identiques.

### Présentation des résultats

J'ai ensuite présenté le fine-tuning des trois modèles (Llama, Mistral et Qwen) pour chaque brique, avec l'évaluation par similarité, crisp et soft.

L'article travaille sur des listes de termes. C'est pourquoi j'ai retenu les attributs qui sont des listes : `altLabel`, `broader` et `narrower`.

Pour illustrer, j'ai pris deux exemples réels du jeu de données : les concepts `matrix` et `sampling theory`.

Dans la comparaison, c'est **Mistral avec la brique 4** qui donne les meilleures valeurs, en similarité comme en crisp et en soft.

### Retours de John

John a demandé des exemples liés au patrimoine. Je vais donc parcourir le fichier de prédictions pour choisir des concepts adaptés, puis les présenter une fois que John les aura validés.

### Prochaines étapes

- La partie génération de concepts est terminée.
- Je vais faire la même évaluation pour le cas du thésaurus, dont le fine-tuning est en cours.
- Je vais finir la méthode GraphRAG et comparer ses résultats à ceux du fine-tuning.
