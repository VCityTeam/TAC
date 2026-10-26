# Application web

---

<aside>
📋

- **Plan**
</aside>

---

## Introduction

L'application web constitue le point d'entrée de l'utilisateur dans l'outil TAC. Elle permet de saisir ou de sélectionner les éléments à traiter, de déclencher les traitements de l'agent TAC, puis de consulter, corriger et valider les résultats obtenus.

Cette page décrit sa conception en partant des données manipulées, pour remonter progressivement vers l'organisation générale du code, les outils employés et une démonstration du résultat.

---

## Tableaux CRUD

Cette section recense les entités gérées par l'application et, pour chacune, les opérations disponibles. CRUD désigne les quatre opérations fondamentales : *Create* (créer), *Read* (consulter), *Update* (modifier) et *Delete* (supprimer).

### Acteurs

Chaque opération est déclenchée par l'un des trois acteurs suivants.

| Acteur | Description |
| --- | --- |
| **Utilisateur** | Action manuelle réalisée depuis l'interface web |
| **Agent TAC** | Génération automatique par l'agent TAC, qui appelle l'outil adapté |
| **Agent TAC via MCP** | Génération automatique par l'agent TAC s'appuyant sur une ressource externe, appelée via le protocole MCP |

### Entités gérées

| Entité | Nature |
| --- | --- |
| **Terme** | Mot unique |
| **Liste de termes** | Liste ou échantillon de termes |
| **Concept** | Terme structuré |
| **Thésaurus** | Conteneur de concepts et de relations |
| **Alignement** | Lien vers une ressource externe |
| **Export** | Sortie normalisée au format SKOS / Opentheso |

### Tableau CRUD

| Entité | C — Create | R — Read | U — Update | D — Delete |
| --- | --- | --- | --- | --- |
| **Terme** | Utilisateur : saisir un terme | Utilisateur : consulter | Utilisateur : corriger | Utilisateur : supprimer |
| **Liste de termes** | Utilisateur : importer une liste, puis sélectionner | Utilisateur : consulter la liste ou la sélection | Utilisateur : modifier la liste ou certains termes | Utilisateur : supprimer la liste ou certains termes |
| **Concept** | Agent TAC : génération automatique
Utilisateur : saisir un concept | Utilisateur : consulter | Utilisateur : corriger, valider
Agent TAC : régénérer après rejet | Utilisateur : rejeter |
| **Thésaurus** | Agent TAC : génération automatique | Utilisateur : consulter | Utilisateur : valider, corriger
Agent TAC : régénérer après rejet | Utilisateur : supprimer |
| **Alignement** | Agent TAC via MCP : génération automatique | Utilisateur : consulter | Utilisateur : corriger le type de lien
Agent TAC : recalculer l'alignement | Utilisateur : supprimer |
| **Export** | Agent TAC : génération automatique | Utilisateur : télécharger | Utilisateur : corriger
Agent TAC : relancer la génération | Utilisateur : supprimer |

Trois enseignements se dégagent de cette répartition.

**La création est majoritairement automatique.** Seuls le terme et la liste de termes sont créés par l'utilisateur : ce sont les points d'entrée du système. Tout le reste concepts, thésaurus, alignements, exports est généré par l'agent TAC. L'utilisateur fournit la matière première, le système produit la structure.

**La lecture est exclusivement humaine.** Aucune consultation n'est automatisée : la lecture existe pour permettre à l'utilisateur d'examiner ce que le système a produit.

**La modification est partagée.** C'est le seul cas où les deux acteurs interviennent sur la même opération. L'utilisateur corrige ponctuellement un résultat, tandis que l'agent TAC peut le régénérer entièrement lorsque la correction porte sur le prompt ou les paramètres du traitement. Ces deux voies correspondent aux deux issues de la boucle de validation décrite dans la vue d'ensemble : une correction locale du résultat, ou une correction du pipeline suivie d'une nouvelle génération.

La suppression, enfin, reste toujours à la main de l'utilisateur le système ne détruit jamais de données de lui-même.

---

## Architecture de l'API

L'API assure la communication entre l'interface utilisateur, l'agent TAC et la base de données graphe. Elle centralise la logique d'accès aux données et garantit que toutes les opérations passent par un point unique et contrôlé.

### Style et conventions

Cette section énonce les règles générales suivies par l'ensemble de l'API, afin que le lecteur puisse comprendre la logique des routes sans avoir à les parcourir une par une.

| Élément | Choix retenu |
| --- | --- |
| Style architectural | REST |
| Format des données | JSON |
| Nommage des routes | Noms au pluriel, en minuscules |
| Correspondance CRUD | `POST` créer · `GET` consulter · `PATCH` modifier · `DELETE` supprimer |
| Identification | Identifiant unique passé dans l'URL : `/ressource/{id}` |

### Points d'accès

Les routes suivent la correspondance classique entre opérations CRUD et méthodes HTTP : `POST` pour la création, `GET` pour la consultation, `PATCH` pour la modification partielle et `DELETE` pour la suppression.

**Terme**

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/terme` | Créer un terme |
| `GET` | `/terme/{id}` | Consulter un terme |
| `PATCH` | `/terme/{id}` | Modifier un terme |
| `DELETE` | `/terme/{id}` | Supprimer un terme |

**Liste de termes**

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/termes` | Importer une liste de termes |
| `GET` | `/termes` | Consulter la liste ou une sélection |
| `PATCH` | `/termes/{id}` | Modifier la liste ou certains termes |
| `DELETE` | `/termes/{id}` | Supprimer la liste ou certains termes |

**Concept**

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/concepts` | Créer un concept, par génération automatique de l'agent TAC ou par saisie de l'utilisateur |
| `GET` | `/concepts` | Consulter les concepts |
| `PATCH` | `/concepts/{id}` | Corriger, valider ou régénérer un concept |
| `DELETE` | `/concepts/{id}` | Rejeter un concept |

**Thésaurus**

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/thesauri` | Générer un thésaurus |
| `GET` | `/thesauri` | Consulter les thésaurus |
| `PATCH` | `/thesauri/{id}` | Valider, corriger ou régénérer un thésaurus |
| `DELETE` | `/thesauri/{id}` | Supprimer un thésaurus |

**Alignement**

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/alignments` | Générer un alignement |
| `GET` | `/alignments` | Consulter les alignements |
| `PATCH` | `/alignments/{id}` | Corriger le type de lien ou recalculer |
| `DELETE` | `/alignments/{id}` | Supprimer un alignement |

**Export**

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/exports` | Générer un export |
| `GET` | `/exports` | Télécharger un export |
| `PATCH` | `/exports/{id}` | Corriger ou relancer la génération |
| `DELETE` | `/exports/{id}` | Supprimer un export |

---

## Architecture MVC

Le patron MVC (*Modèle - Vue - Contrôleur*) structure le code en séparant trois responsabilités distinctes. Cette séparation facilite la maintenance et permet de faire évoluer une couche sans impacter les autres.

### Rôle de chaque couche

**Contrôleur** : Reçoit les requêtes HTTP et les oriente. Selon la nature de la demande, il sollicite l'agent TAC pour une génération, ou directement le modèle pour une lecture, une modification ou une suppression.

**Modèle** : Représente les données sous forme de graphe. Il définit les entités manipulées concepts, thésaurus, alignements ainsi que les relations qui les lient, et assure leur persistance.

**Vue** : Met en forme la réponse retournée à l'utilisateur, sérialisée en JSON. Elle ne contient aucune logique métier.

L'agent TAC ne relève d'aucune de ces trois couches : il constitue un service applicatif appelé par le contrôleur, qui choisit l'outil adapté à la demande et dont les résultats sont ensuite confiés au modèle.

### Schéma

![mvc_agent_tac.svg](Application%20web/mvc_agent_tac.svg)

### Parcours d'une requête

La requête de l'utilisateur atteint d'abord le contrôleur, qui l'aiguille selon sa nature.

**Requête de lecture, de modification ou de suppression.** Le contrôleur s'adresse directement au modèle, qui interroge ou met à jour le graphe. Le résultat est sérialisé par la vue et retourné à l'utilisateur.

**Requête de génération.** Le contrôleur sollicite l'agent TAC, qui appelle l'outil correspondant. Chacun des quatre outils alimente une entité précise du modèle : l'outil 1 (génération de concepts) alimente les nœuds `Concept` et leurs relations `broader` et `narrower`, l'outil 2 (rattachement aux thésaurus) crée la relation d'appartenance du concept à son thésaurus, l'outil 3 (alignement) produit les liens `exactMatch` et `closeMatch`, et l'outil 4 (export) enregistre le SKOS généré. Une fois les résultats persistés dans le graphe, la réponse suit le même chemin de retour que précédemment, par la vue.

Cette correspondance directe entre chaque outil de génération et une entité du modèle est ce qui garantit que rien de ce que produit l'agent TAC ne reste hors du graphe.

---

## Outils et bibliothèques

Cette section recense les technologies employées et justifie leur choix.

### Critères de sélection

Trois critères ont guidé l'ensemble des choix techniques.

**La qualité de l'outil et de son langage** : maturité du projet, stabilité des versions, qualité de la documentation et adéquation aux besoins spécifiques du traitement de vocabulaires structurés.

**L'adoption à l'échelle internationale** : un outil largement utilisé bénéficie d'une communauté active, d'une documentation abondante et d'une pérennité mieux assurée. Ce critère est déterminant pour un projet destiné à être repris ou prolongé.

**Les recommandations d'usage établies** : existence de bonnes pratiques documentées et de retours d'expérience publiés, qui réduisent le risque de s'engager dans une voie sans issue.

### Outils retenus

| Sous-catégorie | Outil retenu | Motif du choix |
| --- | --- | --- |
| Backend | **FastAPI** | Écosystème Python, dominant en traitement automatique du langage · Documentation d'API générée automatiquement · Validation typée des échanges · Gestion native de l'asynchrone |
| Frontend | **React**, HTML, JavaScript | Bibliothèque frontend la plus utilisée au monde · Approche par composants réutilisables · Écosystème et documentation très fournis |
| DevOps | **Docker** | Reproductibilité de l'environnement d'exécution · Déploiement identique quelle que soit la machine · Standard de fait du domaine |

Pour chaque outil, la version utilisée est précisée : c'est une information indispensable à la reproductibilité des résultats.

---

## Démonstration

Cette version de l'application vise à rendre visible le cycle de vie complet du système TAC : depuis la saisie d'un terme initial jusqu'à la production d'un thésaurus exporté au format SKOS.

### Vidéo

[https://drive.google.com/file/d/1zO0GJ0O98xaN4Q5k_kUsRu2KrjSiLkjU/view?usp=drive_link](https://drive.google.com/file/d/1zO0GJ0O98xaN4Q5k_kUsRu2KrjSiLkjU/view?usp=drive_link)

### Organisation de l'interface

L'application est organisée en cinq pages, chacune associée à une entité du système.

| Page | Entité | Rôle |
| --- | --- | --- |
| 1. Termes | Terme, Liste de termes | Saisie d'un terme unique ou import d'une liste  point d'entrée du système |
| 2. Concepts | Concept | Génération, consultation, correction et validation des concepts |
| 3. Thésaurus | Thésaurus | Construction et consultation du thésaurus structuré |
| 4. Alignement | Alignement | Mise en correspondance avec des thésaurus externes |
| 5. Export | Export | Production et téléchargement du fichier SKOS |

Cette correspondance entre page et entité n'est pas un simple choix de découpage. Elle rend le cycle de vie du système lisible dans la navigation elle-même : l'utilisateur progresse de page en page en suivant l'avancement réel du traitement, chaque page produisant la matière première de la suivante.

### Modification du prompt

Les pages Concepts, Thésaurus et Alignement offrent la possibilité de **modifier directement le prompt** avant de lancer ou de relancer une génération.

Cette fonctionnalité donne à l'utilisateur une marge de manœuvre sur la génération elle-même, et non plus seulement sur son résultat. Elle prolonge la boucle de validation décrite dans la vue d'ensemble : lorsqu'un résultat est rejeté, la correction peut porter sur le prompt sans quitter l'interface ni intervenir dans le code.

### Statut des résultats présentés

Les résultats affichés à chaque étape de la démonstration ne constituent pas des résultats définitifs. Ils sont produits par un modèle de langage servant d'échantillon, associé à une approche par ingénierie de prompt. Ils illustrent le fonctionnement de la chaîne de traitement et la nature des sorties attendues, sans préjuger de la qualité obtenue avec les modèles et les prompts retenus en version finale.

### Évolutions prévues

Plusieurs développements sont envisagés pour la prochaine version :

- **Le réglage des paramètres du modèle** depuis l'interface, en complément de la modification du prompt déjà disponible
- **La saisie directe de concepts** par l'utilisateur, sans passer par une génération préalable
- **La refonte de l'interface**, tant sur la présentation que sur l'organisation des écrans

### Conformité avec l'architecture

La démonstration respecte l'ensemble des principes exposés dans les sections précédentes.

**Le tableau CRUD.** Les actions proposées sur chaque page correspondent exactement aux opérations recensées pour l'entité concernée, avec la même répartition entre utilisateur et agent TAC. La page Concepts, par exemple, propose la génération automatique, la saisie manuelle, la correction et le rejet ni plus, ni moins.

**L'architecture de l'API.** Chaque action déclenche l'appel de la route correspondante, selon la correspondance établie entre opérations CRUD et méthodes HTTP.

**L'architecture MVC.** Le parcours de chaque requête suit le cheminement décrit précédemment : le contrôleur reçoit la demande et l'oriente vers l'agent TAC ou vers le modèle de graphe, puis la vue met en forme la réponse retournée à l'interface.