# Base de données graphe

---

<aside>
📋

- **Plan**
</aside>

---

# Introduction

Cette page décrit la couche de persistance de l'outil TAC. Elle s'inscrit dans l'architecture générale présentée dans la **Vue d'ensemble**, entre l'application web qui consulte les données et l'agent TAC qui les produit.

---

## Rôle dans le système

La base de données assure la conservation de l'ensemble des objets manipulés par TAC : les termes saisis par l'utilisateur, ainsi que les concepts, thésaurus et alignements générés par l'agent TAC. Elle remplit trois fonctions distinctes.

**Assurer la continuité entre les étapes de traitement.** La chaîne de traitement procède par étapes successives, chacune consommant le résultat de la précédente : un terme produit des concepts, les concepts produisent un thésaurus, le thésaurus produit un alignement puis un export. Sans persistance, chaque étape devrait être relancée depuis le début. La base conserve les résultats intermédiaires et permet à l'utilisateur d'interrompre son travail puis de le reprendre.

**Recueillir les résultats avant validation.** Les objets générés par l'agent TAC ne sont pas versés directement dans Opentheso. Ils sont d'abord stockés dans la base, où ils restent consultables et corrigeables jusqu'à leur validation par un spécialiste. La base constitue ainsi l'espace de travail intermédiaire dans lequel s'exerce la supervision humaine.

**Servir de base de connaissances à l'agent TAC.** C'est le point fort de cette architecture. Les thésaurus déjà constitués et validés ne sont pas seulement des résultats archivés : ils deviennent une ressource mobilisable par les outils de l'agent TAC pour la génération de nouveaux thésaurus. Le système s'enrichit ainsi de sa propre production, chaque vocabulaire validé améliorant la qualité des suivants.

---

## Pourquoi une base de graphe

Un thésaurus est, par construction, un graphe : des concepts reliés entre eux par des relations hiérarchiques et associatives. Le choix d'une base de graphe découle directement de cette nature.

Une base de graphe repose sur deux éléments : des **nœuds**, qui représentent les objets, et des **arêtes**, qui représentent les relations entre ces objets. Sa force tient à ce que les relations y sont des données de premier rang, stockées et parcourues directement, et non reconstituées à chaque interrogation.

Cette propriété correspond exactement aux besoins du projet :

- Un concept peut être plus générique ou plus spécifique qu'un autre relations `broader` et `narrower`
- Un concept appartient à un thésaurus
- Un concept d'un thésaurus peut être aligné sur un concept d'un référentiel externe

Dans une base relationnelle, la navigation hiérarchique remonter la chaîne des termes génériques, par exemple imposerait des jointures successives dont le coût croît avec la profondeur de l'arbre. Une base de graphe parcourt ces relations nativement, quelle que soit la profondeur.

---

## Modèle de données

Le modèle repose sur **cinq objets** reliés par **cinq relations**.

### Entités

| Entité | Description | Attributs |
| --- | --- | --- |
| **Terme** | Le mot brut, tel que saisi ou importé par l'utilisateur | `id`, `libellé` |
| **Concept** | Le terme structuré, enrichi par l'agent TAC | `id`, `définition`, `synonymes` |
| **Thésaurus** | Le conteneur regroupant un ensemble de concepts | `id`, `titre`, `langues`, `nombre de concepts` |
| **Thésaurus externe** | Un thésaurus issu d'un référentiel de référence, cible des alignements | `id`, `titre`, `référentiel d'origine` |
| **Export** | La représentation normalisée du thésaurus au format SKOS | `id`, `prefLabel`, `altLabel`, `definition`, `broader`, `narrower` |

### Relations

| Relation | De | Vers | Signification |
| --- | --- | --- | --- |
| **désigne** | Terme | Concept | Le terme brut est rattaché au concept qu'il désigne |
| **appartient à** | Concept | Thésaurus | Le concept fait partie d'un thésaurus donné |
| **broader / narrower** | Concept | Concept | Relation hiérarchique entre deux concepts d'un même thésaurus |
| **alignement** | Thésaurus | Thésaurus externe | Mise en correspondance du vocabulaire TAC avec un référentiel externe |
| **génère** | Thésaurus | Export | Production du fichier SKOS à partir du thésaurus |

La relation `broader / narrower` mérite d'être signalée : c'est la seule relation **réflexive** du modèle, un concept pointant vers un autre concept. C'est elle qui porte toute la structure hiérarchique du thésaurus, et donc l'essentiel de sa valeur documentaire.

### Précision sur l'alignement

L'alignement s'établit entre **deux thésaurus** : celui produit par TAC et celui d'un référentiel externe. C'est à ce niveau que l'opération se conçoit et se déclenche, et c'est donc à ce niveau qu'elle figure dans le modèle.

Il convient toutefois de distinguer l'opération de son résultat. Aligner deux thésaurus consiste à produire un ensemble de correspondances, et ces correspondances s'expriment en SKOS au moyen des propriétés `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch` et `relatedMatch`, qui s'appliquent à des concepts pris individuellement. L'alignement relie donc deux vocabulaires, tandis que les correspondances qu'il produit relient leurs concepts deux à deux.

### Schéma

![modele_donnees_graphe_tac.svg](Base%20de%20donn%C3%A9es%20graphe/modele_donnees_graphe_tac.svg)

Chaque entité apparaît avec ses attributs, et les cardinalités précisent la nature de chaque relation : un thésaurus regroupe plusieurs concepts, un concept peut avoir plusieurs concepts spécifiques, et un thésaurus TAC peut être aligné sur plusieurs thésaurus externes.

`CONCEPT_LIÉ` ne constitue pas une entité distincte : il s'agit du même objet `CONCEPT`, représenté une seconde fois pour rendre lisible la relation hiérarchique. Un concept en désigne un autre comme plus générique (`broader`) ou plus spécifique (`narrower`), les deux appartenant au même thésaurus.

L'entité `THÉSAURUS_EXTERNE` n'appartient pas au graphe TAC : elle représente un référentiel de référence, seul objet du modèle situé hors du périmètre de l'outil.

Le modèle se lit comme le parcours d'un terme à travers le système.

Un **terme** brut entre dans la base. L'agent TAC l'enrichit pour en faire un **concept**, doté d'une définition et de synonymes. Ce concept prend place dans un **thésaurus**, et se positionne par rapport aux autres concepts au moyen des relations `broader` et `narrower` c'est cette mise en relation qui transforme une liste plate en vocabulaire structuré. Le thésaurus ainsi constitué peut ensuite être aligné sur un **thésaurus externe** issu d'un référentiel de référence, ce qui situe le vocabulaire produit par rapport à des ressources reconnues. Il donne enfin lieu à un **export** au format SKOS, directement versable dans Opentheso.

Chacune de ces étapes est validée par un spécialiste avant que la suivante ne soit engagée.

# Choix de la base de données graphe

Le principe d'une base de graphe étant retenu, restait à déterminer laquelle. Deux solutions ont été comparées : **Neo4j** et **ArangoDB**. Elles ont fait l'objet d'un benchmark portant sur les performances, la volumétrie, l'expressivité du langage de requête, les capacités d'export et les conditions de licence.

## Présentation des deux solutions

**Neo4j** est une base de données orientée graphe **native**. Elle ne fait qu'une chose : stocker des nœuds et des relations, et les parcourir. Les relations y sont des objets de premier rang, physiquement stockés comme des pointeurs entre nœuds. Son langage de requête, **Cypher**, est conçu pour décrire des chemins dans un graphe.

**ArangoDB** est une base **multi-modèle**. Elle réunit trois paradigmes dans un même moteur : le stockage documentaire, le graphe et le clé-valeur. Son langage de requête, **AQL**, couvre l'ensemble de ces modes d'interrogation.

Cette différence de conception est déterminante. ArangoDB offre davantage de possibilités, mais son modèle graphe est construit au-dessus de son modèle documentaire : les nœuds y sont des documents, et les relations des documents d'un type particulier référençant les précédents. Neo4j ne propose qu'un seul modèle, mais l'implémente nativement.

|  | ArangoDB | Neo4j |
| --- | --- | --- |
| Modèle | Trois modèles en un : documents, graphe, clé-valeur | Un seul modèle : graphe |
| Implémentation du graphe | Construite sur le modèle documentaire | Native |
| Positionnement | Polyvalent | Spécialisé |

## Un exemple concret

Prenons une question simple issue du projet : **« à partir du terme *vitrail*, retrouver le thésaurus auquel il appartient »**. Le chemin à parcourir est le suivant : `Terme → Concept → Thésaurus`.

**Avec ArangoDB**, le terme *vitrail* est une fiche contenant une référence vers la fiche du concept correspondant. Pour atteindre le concept, il faut aller chercher cette seconde fiche ; pour atteindre le thésaurus, une troisième. Chaque étape du chemin donne lieu à une recherche.

**Avec Neo4j**, la relation entre le terme et le concept est stockée telle quelle. Le parcours consiste à suivre ce lien, sans recherche intermédiaire. Trois étapes se traduisent par trois sauts de pointeur, et non par trois recherches.

L'écart se creuse à mesure que le chemin s'allonge ce qui est précisément le cas d'un thésaurus, où l'on remonte fréquemment une hiérarchie de termes génériques.

## Les langages de requête

La même question, exprimée dans les deux langages :

**Cypher** (Neo4j)

```
MATCH (t:Terme {nom:'vitrail'})-[:DESIGNE]->(c:Concept)-[:APPARTIENT]->(th:Thesaurus)
RETURN th
```

La requête se lit comme une phrase, et sa syntaxe dessine visuellement le chemin parcouru : le terme désigne un concept, qui appartient à un thésaurus.

**AQL** (ArangoDB)

```
FOR v IN 2..2 OUTBOUND 'termes/vitrail' GRAPH 'tac_graph' 
FILTER IS_SAME_COLLECTION('thesaurus', v)
RETURN v
```

La requête impose de compter les sauts à effectuer (`2..2`), de nommer explicitement le graphe, puis de filtrer les résultats par collection pour ne conserver que les thésaurus. La logique métier (*un terme désigne un concept qui appartient à un thésaurus )* n'y apparaît plus.

Cette différence de lisibilité a des conséquences pratiques : sur un projet destiné à être repris et documenté, des requêtes Cypher restent compréhensibles par un lecteur qui découvre le code.

## L'export SKOS

L'export au format SKOS constitue la sortie finale de l'outil. Les deux solutions le traitent différemment.

**Neo4j** dispose du plugin **n10s** (*neosemantics*), qui assure la conversion vers RDF et SKOS directement dans la base. La transformation reste interne au moteur.

**ArangoDB** ne propose pas d'équivalent intégré. L'export suppose d'extraire les données, puis de les convertir au moyen d'un script externe en Python. Cette étape supplémentaire allonge la chaîne de traitement et introduit un point de défaillance : toute évolution du modèle de données impose de maintenir le script en parallèle.

## Protocole du benchmark

Le benchmark a porté sur un jeu de données identique concepts, thésaurus et relations chargé successivement dans les deux bases. Trois requêtes représentatives des usages de l'outil ont été mesurées.

### Q1 — Les concepts d'un thésaurus

*Quels sont les concepts appartenant à un thésaurus donné ?*

```
// Cypher
MATCH (c:Concept)-[:APPARTIENT]->(th:Thesaurus {id: $id})
RETURN c
```

```
// AQL
FOR v IN 1..1 INBOUND CONCAT('thesaurus/', @id) GRAPH 'tac_graph'
  FILTER IS_SAME_COLLECTION('concepts', v)
  RETURN v
```

### Q2 — Les thésaurus d'un concept

*À quels thésaurus appartient un concept donné ?*

```
// Cypher
MATCH (c:Concept {id: $id})-[:APPARTIENT]->(th:Thesaurus)
RETURN th
```

```
// AQL
FOR v IN 1..1 OUTBOUND CONCAT('concepts/', @id) GRAPH 'tac_graph'
  FILTER IS_SAME_COLLECTION('thesaurus', v)
  RETURN v
```

### Q3 — Le concept d'un terme

*Quel concept correspond à un terme donné ?*

```
// Cypher
MATCH (t:Terme {nom: $nom})-[:DESIGNE]->(c:Concept)
RETURN c
```

```
// AQL
FOR v IN 1..1 OUTBOUND CONCAT('termes/', @id) GRAPH 'tac_graph'
  FILTER IS_SAME_COLLECTION('concepts', v)
  RETURN v
```

La comparaison des deux colonnes fait apparaître une constante : Cypher nomme la relation parcourue (`APPARTIENT`, `DESIGNE`), tandis qu'AQL désigne une direction et un nombre de sauts, puis filtre le résultat par collection. La première formulation exprime la logique métier, la seconde décrit un parcours technique.

## Mesure de la taille des données

Les deux systèmes n'exposent pas cette information de la même manière.

**ArangoDB** fournit la méthode `figures()` sur chaque collection. La taille totale s'obtient en additionnant les documents et les index de l'ensemble des collections, depuis `arangosh` :

```jsx
let total = 0;
db._collections()
  .filter(c => c.name()[0] !== '_')          // exclut les collections système
  .forEach(function (c) {
    const f = c.figures();
    total += f.documentsSize + f.indexes.size;
  });
print((total / 1024 / 1024).toFixed(2) + ' Mo');
```

Pour le détail d'une collection : `db.concepts.figures()`.

**Neo4j** n'expose pas d'équivalent direct. La taille se lit dans les propriétés du moteur, interrogeables en JMX depuis Cypher :

```
CALL dbms.queryJmx("org.neo4j:instance=kernel#0,name=Store file sizes")
YIELD attributes
UNWIND keys(attributes) AS metrique
RETURN metrique, attributes[metrique]["value"]
```

La ligne `TotalStoreSize` donne la taille totale ; les autres détaillent la répartition entre nœuds, relations, propriétés et index.

**Vérification sur le système de fichiers.** Les deux mesures peuvent être recoupées en observant directement le volume occupé sur disque, ce qui constitue la méthode la plus fiable pour une comparaison :

```bash
du -sh $NEO4J_HOME/data/databases/<nom_de_la_base>
du -sh /var/lib/arangodb3/databases/
```

## Résultats

| Critère | Neo4j | ArangoDB | Avantage |
| --- | --- | --- | --- |
| Stockage (concepts + thésaurus + relations) | **6,72 s** | 536,08 s | Neo4j |
| Q1 — concepts d'un thésaurus | **27,94 ms** | 46,35 ms | Neo4j |
| Q2 — thésaurus d'un concept | **4,26 ms** | 49,42 ms | Neo4j |
| Q3 — concept d'un terme | **3,88 ms** | 50,96 ms | Neo4j |
| Taille des données | **3,98 Mo** | 12,55 Mo | Neo4j |
| Export SKOS | **Natif (plugin n10s)** | Script Python externe | Neo4j |
| Langage de requête | Cypher | AQL | — |

Le résultat le plus marquant concerne le **chargement des données** : 6,72 secondes contre 536 secondes, soit un rapport de 1 à 80. Cet écart s'explique par le mode d'insertion des relations, qui suppose dans ArangoDB la création et l'indexation de documents supplémentaires.

Sur les requêtes, l'écart est moins spectaculaire mais constant. Il devient particulièrement net sur Q2 et Q3, qui parcourent des relations soit exactement l'usage pour lequel Neo4j est conçu.

Enfin, la **taille des données** stockées est trois fois moindre, conséquence directe de la représentation native des relations plutôt que de leur matérialisation sous forme de documents.

## Licence et coût

Les deux solutions proposent une édition gratuite, mais assortie de conditions différentes.

| Critère | Neo4j | ArangoDB |
| --- | --- | --- |
| Édition gratuite | Neo4j Community | ArangoDB Community |
| Licence | GPLv3 | Community License (BSL 1.1) |
| Limite de volume | Aucune | 100 Go maximum en production |

Ce point mérite attention dans la perspective d'un déploiement : la limite de 100 Go d'ArangoDB en édition communautaire constitue un plafond qu'un projet d'agrégation de vocabulaires pourrait atteindre à terme.

## Jeu de démonstration

Les données présentées ici constituent un **exemple**, créé uniquement pour illustrer le fonctionnement de Neo4j et la structure du modèle. Elles ne reflètent ni le contenu, ni le volume des données réelles du projet.

Le graphe porte sur le domaine du vitrail et comprend **13 nœuds et 16 relations** :

| Type de nœud | Nombre |
| --- | --- |
| Terme | 5 |
| Concept | 5 |
| Thésaurus | 1 |
| Thésaurus externe | 1 |
| Export | 1 |
| **Total** | **13** |

Les cinq types de relations du modèle y sont représentés : `DESIGNE`, `APPARTIENT`, `BROADER`, `ALIGNEMENT` et `GENERE`.

Ce volume est volontairement réduit : au-delà de quelques dizaines de nœuds, la représentation graphique cesse d'être lisible et perd son intérêt explicatif.

[graphe_tac.html](Base%20de%20donn%C3%A9es%20graphe/graphe_tac.html)

## Conclusion

**Neo4j est retenu comme base de données du projet TAC.** Il l'emporte sur l'ensemble des critères mesurés, et l'écart est particulièrement marqué là où se situent les usages réels de l'outil : le chargement de volumes importants de concepts et le parcours de relations.

Trois raisons se dégagent au-delà des seuls chiffres. Le **modèle natif** correspond exactement à la structure d'un thésaurus. La **lisibilité de Cypher** facilite la reprise du projet par un tiers. L'**export SKOS intégré** évite d'introduire une dépendance externe sur l'étape finale de la chaîne de traitement.

La polyvalence d'ArangoDB trois modèles en un n'apporte ici aucun bénéfice, le projet n'ayant besoin que du modèle graphe.