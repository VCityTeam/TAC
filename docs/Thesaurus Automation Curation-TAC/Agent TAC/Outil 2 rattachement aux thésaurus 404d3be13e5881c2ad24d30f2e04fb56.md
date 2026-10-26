# Outil 2 : rattachement aux thésaurus

## Rôle de l'outil

À partir d'un concept, l'outil propose le thésaurus auquel il doit être rattaché.

**Statut** : développé.

## Fonctionnement

L'outil utilise la base vectorielle de thésaurus (Qdrant) et la relation « appartient à » du graphe de connaissances (Neo4j) pour construire le contexte. Le prompt construit par le RAG hybride est affiché à l'utilisateur pour validation, puis envoyé au modèle Mistral 7B fine-tuné pour les thésaurus. Le thésaurus proposé est validé par l'utilisateur avant l'enregistrement dans OpenTheso.

## Pages liées

- Approches et évaluation : [***Fine-tuning vs RAG hybride : comparaison et approches combinées***](../Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche%20402d3be13e588084975ec6c4cbee7ca9.md)
- Fine-tuning : [Fine-tuning](../Fine-tuning%203d4d3be13e58816eb546f3c810998ef4.md)
- RAG hybride : [RAG hybride ](../RAG%20hybride%203ebd3be13e58809aa015d3e717ebe9c9.md)
- Graphe de connaissances : [Base de données graphe](../Base%20de%20donn%C3%A9es%20graphe%203b1d3be13e588034b924cdd63f4d7fa5.md)