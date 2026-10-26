# Outil 1 : génération de concepts

## Rôle de l'outil

À partir d'un terme fourni par l'utilisateur, l'outil propose un concept SKOS complet : `prefLabel`, `altLabel`, définition, `broader` et `narrower`.

**Statut** : développé.

## Fonctionnement

L'outil utilise la base vectorielle de concepts (Qdrant) et le graphe de connaissances (Neo4j) pour retrouver les concepts les plus proches et leurs relations. Le RAG hybride construit ensuite le prompt, qui est affiché à l'utilisateur pour validation, puis envoyé au modèle Mistral 7B fine-tuné en brique 5. Le concept proposé est validé par l'utilisateur avant son enregistrement dans OpenTheso.

## Pages liées

- Approches et évaluation : [***Fine-tuning vs RAG hybride : comparaison et approches combinées***](../Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche%20402d3be13e588084975ec6c4cbee7ca9.md)
- Fine-tuning : [Fine-tuning](../Fine-tuning%203d4d3be13e58816eb546f3c810998ef4.md)
- RAG hybride : [RAG hybride ](../RAG%20hybride%203ebd3be13e58809aa015d3e717ebe9c9.md)
- Graphe de connaissances : [Base de données graphe](../Base%20de%20donn%C3%A9es%20graphe%203b1d3be13e588034b924cdd63f4d7fa5.md)