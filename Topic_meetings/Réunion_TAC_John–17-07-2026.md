# Compte-rendu de réunion — Benchmark Neo4j / ArangoDB & évaluation du RAG

**Participants :** Rida, John

## 1. Benchmark Neo4j et ArangoDB

Lors de cette réunion avec John, j'ai présenté le benchmark comparant Neo4j et ArangoDB. Pour ce benchmark, j'ai retenu comme critère principal le stockage des données : les données ont été stockées simultanément dans les deux bases, puis j'ai mesuré le temps d'exécution correspondant.

### Demandes de John

À l'issue de la présentation, John a demandé les compléments suivants :

- Ajouter les requêtes utilisées pour les cas Q1, Q2 et Q3.
- Détailler le mécanisme de stockage des données pour les deux langages : Cypher (Neo4j) et AQL (ArangoDB), afin de comprendre les différences entre les deux approches.
- Montrer comment afficher la taille des données (data size) pour Neo4j et pour ArangoDB, sur les deux bases.

## 2. Évaluation du RAG

La seconde partie porte sur l'évaluation du RAG (Retrieval-Augmented Generation). Nous disposons pour l'instant d'une première version reposant sur des paramètres simples. J'ai volontairement choisi des paramètres simples car je n'avais pas accès au serveur.

Pour cette évaluation, j'ai sélectionné 29 termes de manière arbitraire, sans certitude sur le fait qu'ils existent déjà dans la base vectorielle ; l'objectif était uniquement de réaliser une évaluation manuelle. Par exemple, j'ai attribué un score de 5/5, chaque point étant associé à une propriété du concept. Chaque concept contient 5 caractéristiques (définition, broader, etc.). L'évaluation a été réalisée à l'aide de modèles de type ChatGPT, simplement pour observer le comportement de cette première version du RAG.

### Pistes de discussion sur l'évaluation du RAG

- Soumettre un même terme au modèle LLM, sachant que ce terme existe déjà dans la base vectorielle, et vérifier que le modèle renvoie bien la même réponse.
- Construire un scénario de test à partir d'un ensemble de termes : sélectionner un terme, récupérer l'altLabel le plus proche, fournir cet altLabel au système, et vérifier qu'il produit le même résultat que pour le terme d'origine.

## 3. Évaluation du fine-tuning

Nous disposons d'un ensemble de 3 606 concepts. La démarche consiste à répartir les données en 70 % pour le fine-tuning et 30 % pour le test, afin de calculer les métriques d'évaluation (recall, etc.).

Exemple de test envisagé : soumettre au modèle LLM une question du type « donne-moi un broader de ce terme », et vérifier que le résultat renvoyé correspond bien à un broader effectivement associé à ce terme.

## 4. Points transverses à discuter

- Clarifier pourquoi nous utilisons à la fois le RAG et le fine-tuning : rôle et complémentarité des deux approches.
- Aborder l'alignement entre les concepts au sein d'une même base vectorielle : par exemple, poser une question demandant l'alignement d'un concept avec un autre.
