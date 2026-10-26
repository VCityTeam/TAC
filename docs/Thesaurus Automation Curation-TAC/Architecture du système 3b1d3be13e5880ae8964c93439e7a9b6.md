# Architecture du système

---

<aside>
📋

- **Plan**
</aside>

---

## Vue d'ensemble

Cette page présente le fonctionnement général de l'outil TAC : ce qu'il fait, de quoi il est composé et comment ses différentes briques s'articulent. Elle est volontairement synthétique. Le détail de chaque composant  choix techniques, implémentation, expérimentations est traité dans les sections suivantes.

### Principe général

---

TAC est un outil d'assistance à la construction de thésaurus. À partir d'un terme ou d'un concept fourni par l'utilisateur, le système s'appuie sur l'agent TAC, qui orchestre des modèles de langage, pour extraire les concepts pertinents, générer les relations qui les structurent, et produire un thésaurus exploitable au format SKOS. Il permet également d'aligner les thésaurus produits avec des thésaurus externes issus de bases de données de référence.

L'outil ne fonctionne pas de manière entièrement automatique : chaque résultat généré fait l'objet d'une double évaluation, combinant une **validation humaine** et le calcul de **métriques quantitatives**. L'utilisateur reste ainsi maître du contenu final, tandis que les métriques permettent de mesurer objectivement la qualité de la génération.

### Fonctionnalités

---

L'outil expose quatre fonctionnalités distinctes. Chacune correspond à un point d'entrée différent et peut être utilisée seule ou enchaînée aux autres.

| Fonctionnalité | Entrée | Sortie |
| --- | --- | --- |
| Extraction de concepts | Un terme | Les concepts associés |
| Génération de thésaurus | Un concept (saisi ou sélectionné) | Un thésaurus structurant les concepts |
| Alignement | Un thésaurus TAC + un thésaurus externe | Les correspondances entre les deux |
| Export normalisé | Un thésaurus | Le thésaurus au format SKOS |

**Extraction de concepts.** L'utilisateur fournit un terme ; le système identifie et retourne les concepts qui lui sont associés. C'est le point de départ le plus courant.

**Génération de thésaurus.** À partir d'un concept saisi librement ou sélectionné parmi les résultats de l'étape précédente le système construit un thésaurus organisant les concepts et les relations qui les lient.

**Alignement.** Le système met en correspondance un thésaurus produit par TAC avec un thésaurus externe issu d'une base de référence. Cette étape permet de situer le vocabulaire généré par rapport à des ressources existantes et reconnues.

**Export normalisé.** Un thésaurus est exporté au format SKOS, standard du W3C pour la représentation des vocabulaires structurés. Cette normalisation garantit que les résultats sont réutilisables en dehors de l'outil.

Chacune de ces sorties passe ensuite par le module d'évaluation.

### Composants

---

Le système repose sur quatre composants.

**Agent TAC** : Cœur du traitement. Un LLM orchestrateur analyse la requête de l'utilisateur, formulée en langage naturel, puis appelle l'outil spécialisé correspondant : génération de concepts, rattachement aux thésaurus, alignement et export SKOS. Ces outils s'appuient sur des ressources communes (bases vectorielles Qdrant, graphe de connaissances Neo4j, modèles Mistral 7B fine-tunés, API OpenTheso). C'est le composant qui porte l'essentiel de la valeur ajoutée du projet ; il est détaillé dans la page [Agent TAC ](Agent%20TAC%203b1d3be13e5880fe8c2dcd534f08eb3b.md).

**Base de données graphe** : Couche de persistance. Elle conserve les concepts et les thésaurus produits afin qu'ils puissent être réutilisés dans les étapes suivantes. Sa structure en graphe correspond naturellement à celle d'un thésaurus, où les concepts forment les nœuds et les relations les arêtes.

**Application web** : Point d'entrée de l'utilisateur. Elle permet de saisir ou de sélectionner les éléments à traiter, de lancer les traitements, puis de consulter, corriger et valider les résultats. Elle repose sur une interface utilisateur et une API qui assure la communication avec les autres composants.

**Module d'évaluation** : Il combine deux approches complémentaires : une validation humaine, où l'utilisateur accepte ou corrige les propositions du système, et le calcul de métriques quantitatives permettant de mesurer la qualité des résultats de manière reproductible.

---

### Schéma 1 — Architecture du système

Ce schéma présente **la structure** du système : les composants existants, leur contenu et les échanges entre eux. Il ne représente pas les données qui circulent, mais uniquement les liens de communication.

![architecture_systeme_agent_tac.svg](Architecture%20du%20syst%C3%A8me/architecture_systeme_agent_tac.svg)

**Comment le lire.** L'utilisateur interagit uniquement avec l'interface web. Celle-ci transmet ses demandes à l'API, qui joue le rôle de chef d'orchestre : elle transmet les demandes de traitement à l'agent TAC, sollicite le module d'évaluation pour la validation, et accède directement à la base graphe pour consulter les résultats déjà produits. L'agent TAC choisit l'outil adapté à la demande et enregistre ses résultats dans la base graphe. Les thésaurus externes n'entrent en jeu que pour l'outil 3 (alignement). Les outils 3 et 4, en pointillés, sont encore à implémenter.

### Schéma 2 — Chaîne de traitement

Ce schéma présente **le parcours des données** : ce qui entre dans le système, comment cela se transforme et ce qui en sort. C'est le complément du schéma précédent, qui montrait la structure sans les données.

![chaine_traitement_agent_tac.svg](Architecture%20du%20syst%C3%A8me/chaine_traitement_agent_tac.svg)

**Comment le lire.** La chaîne complète part d'un terme et aboutit à un thésaurus normalisé. Chaque transformation est réalisée par l'un des quatre outils de l'agent TAC. Elle n'est cependant pas obligatoire dans son intégralité : l'utilisateur peut entrer directement au niveau d'un concept pour générer un thésaurus, ou au niveau d'un thésaurus existant pour l'aligner ou l'exporter. Les deux dernières étapes alignement et export sont indépendantes l'une de l'autre et s'appliquent toutes deux à un thésaurus.

À chaque sortie intermédiaire (concepts, thésaurus, correspondances), le module d'évaluation intervient pour valider et mesurer la qualité du résultat avant de poursuivre.

---

### Schéma 3 — Boucle de validation humaine

Aucun résultat produit par l'agent TAC n'est intégré au pipeline sans avoir été examiné par un spécialiste. Ce schéma décrit le mécanisme de validation, identique quel que soit le type d'objet traité.

On note **α** l'objet en cours de traitement, avec α ∈ {terme, concept, thésaurus, alignement, SKOS}. Cette notation permet de décrire une seule fois une boucle qui s'applique de la même manière aux quatre fonctionnalités de l'outil.

![boucle_validation_agent_tac.svg](Architecture%20du%20syst%C3%A8me/boucle_validation_agent_tac.svg)

### Déroulement

**1. Traitement.** L'agent TAC traite l'objet α en appelant l'outil adapté, et produit un résultat.

**2. Validation humaine.** Le résultat est soumis à un spécialiste, qui l'examine et se prononce.

**3a. En cas de validation.** L'objet devient un « α validé » et poursuit son parcours dans le pipeline. Il peut alors servir d'entrée à l'étape suivante.

**3b. En cas de rejet.** Le traitement ne repart pas de zéro : la correction porte sur le pipeline lui-même. Le prompt ou les paramètres du traitement sont ajustés, puis le traitement est relancé sur le même objet α. Le motif du rejet et le numéro d'itération sont conservés.

Ce fonctionnement fait de TAC un système à **supervision humaine** plutôt qu'un système entièrement automatique. L'agent propose, le spécialiste décide, et chaque rejet devient une information exploitable pour améliorer le pipeline.

### Traçabilité

Chaque passage dans la boucle est journalisé, sur deux plans :

| Côté | Informations conservées |
| --- | --- |
| Traitement par l'agent TAC | `model_id`, `prompt_id`, numéro d'itération |
| Validation | `user_id`, horodatage, numéro d'itération |
| Rejet | Motif, numéro d'itération |

Cette traçabilité répond à trois besoins. Elle permet d'abord de **reproduire** un résultat, en sachant exactement quel modèle et quel prompt l'ont produit. Elle permet ensuite d'**analyser les échecs**, en croisant les motifs de rejet avec les configurations utilisées. Elle fournit enfin la matière nécessaire à l'**évaluation quantitative** du système : taux de validation au premier essai, nombre moyen d'itérations avant acceptation, évolution de ces indicateurs selon le modèle ou le prompt employé.