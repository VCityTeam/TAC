# Agent TAC

---

## 1. Introduction

L'agent TAC est le point d'entrée du projet TAC (Thésaurus Automatisé par Curation). Il permet à un documentaliste ou à un spécialiste du patrimoine de travailler sur ses thésaurus en langage naturel : créer un nouveau concept, le rattacher au bon thésaurus, aligner un thésaurus avec des référentiels externes ou l'exporter au format SKOS.

L'agent repose sur un LLM qui joue le rôle d'orchestrateur. Il ne répond pas directement à la requête : il l'analyse, détermine la tâche demandée, puis appelle l'outil spécialisé correspondant. Chaque outil s'appuie sur des ressources communes (bases vectorielles, graphe de connaissances, modèles fine-tunés et API OpenTheso) et renvoie son résultat à l'agent, qui le présente à l'utilisateur.

L'agent est conçu pour travailler avec l'utilisateur et non à sa place. Le contexte construit pour chaque requête, comme les concepts proches ou les thésaurus candidats, est affiché avant d'être envoyé au modèle, et chaque résultat est validé par l'utilisateur avant d'être enregistré dans OpenTheso. Cette validation humaine dans la boucle (human-in-the-loop) garantit la qualité des thésaurus produits.

## 2. Architecture de l'agent TAC

Le schéma suivant présente l'architecture générale de l'agent : l'utilisateur, l'agent TAC, ses quatre outils, les ressources qu'ils utilisent et la validation humaine.

![agent_tac_architecture.svg](Agent%20TAC/agent_tac_architecture.svg)

L'utilisateur envoie une requête en langage naturel. L'agent TAC l'analyse, choisit l'outil adapté, puis sélectionne la base vectorielle, les relations du graphe et le modèle à utiliser. Le résultat est présenté à l'utilisateur, qui le valide avant son enregistrement.

### 2.1. Les quatre outils

- **Outil 1 : génération de concepts** (développé). À partir d'un terme, l'outil propose un concept SKOS complet : `prefLabel`, `altLabel`, définition, `broader` et `narrower`. Page de l'outil : [Outil 1 : génération de concepts](Agent%20TAC/Outil%201%20g%C3%A9n%C3%A9ration%20de%20concepts%20404d3be13e5881fd8ffde445b248d24d.md)
- **Outil 2 : rattachement aux thésaurus** (développé). À partir d'un concept, l'outil propose le thésaurus auquel il doit être rattaché. Page de l'outil : [Outil 2 : rattachement aux thésaurus](Agent%20TAC/Outil%202%20rattachement%20aux%20th%C3%A9saurus%20404d3be13e5881c2ad24d30f2e04fb56.md)
- **Outil 3 : alignement des thésaurus** (à implémenter). L'outil reliera les thésaurus construits avec le LLM aux thésaurus et référentiels externes. Page de l'outil : [Outil 3 : alignement des thésaurus](Agent%20TAC/Outil%203%20alignement%20des%20th%C3%A9saurus%20404d3be13e5881c68043f81d62a978d7.md)
- **Outil 4 : export au format SKOS** (à implémenter). L'outil exportera le thésaurus validé au format SKOS (RDF), pour qu'il puisse être réutilisé par d'autres applications. Page de l'outil : [Outil 4 : export au format SKOS](Agent%20TAC/Outil%204%20export%20au%20format%20SKOS%20404d3be13e588180b19cf1c322212216.md)

Les approches utilisées par les outils 1 et 2 et leur évaluation sont présentées dans la page [***Fine-tuning vs RAG hybride : comparaison et approches combinées***](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche%20402d3be13e588084975ec6c4cbee7ca9.md).

### 2.2. Les ressources utilisées par les outils

- **Qdrant** : bases vectorielles de concepts et de thésaurus, pour retrouver les éléments les plus proches d'une requête.
- **Neo4j** : graphe de connaissances qui stocke les relations entre concepts (`broader`, `narrower`) et l'appartenance des concepts aux thésaurus ([Base de données graphe](Base%20de%20donn%C3%A9es%20graphe%203b1d3be13e588034b924cdd63f4d7fa5.md)).
- **Modèles fine-tunés** : un modèle Mistral 7B spécialisé pour la génération de concepts et un autre pour le rattachement aux thésaurus.
- **API OpenTheso** : lecture des thésaurus existants et enregistrement des résultats validés.

### 2.3. Validation humaine

À chaque étape importante, l'agent laisse la décision à l'utilisateur. Le contexte construit par l'agent est affiché et peut être corrigé avant la génération, puis le résultat est présenté et doit être validé avant d'être enregistré dans OpenTheso. Aucun concept ni aucun rattachement n'entre dans un thésaurus sans avoir été vérifié par un spécialiste.

[Outil 1 : génération de concepts](Agent%20TAC/Outil%201%20g%C3%A9n%C3%A9ration%20de%20concepts%20404d3be13e5881fd8ffde445b248d24d.md)

[Outil 2 : rattachement aux thésaurus](Agent%20TAC/Outil%202%20rattachement%20aux%20th%C3%A9saurus%20404d3be13e5881c2ad24d30f2e04fb56.md)

[Outil 3 : alignement des thésaurus](Agent%20TAC/Outil%203%20alignement%20des%20th%C3%A9saurus%20404d3be13e5881c68043f81d62a978d7.md)

[Outil 4 : export au format SKOS](Agent%20TAC/Outil%204%20export%20au%20format%20SKOS%20404d3be13e588180b19cf1c322212216.md)