# RAG hybride

---

<aside>
📋

- **Plan**
</aside>

---

## 1. Objectif

L'approche RAG hybride constitue la deuxième approche pour la génération de concepts et leur rattachement au thésaurus. Elle repose sur la combinaison de deux mécanismes de recherche : d'une part, deux bases vectorielles, l'une pour retrouver un concept par le sens et l'autre pour identifier le thésaurus pertinent ; d'autre part, un graphe de connaissances permettant d'en parcourir les relations exactes, à savoir les relations d'appartenance entre concepts et thésaurus ainsi que les relations hiérarchiques broader et narrower. L'ensemble constitue le contexte transmis au modèle de langage.

> **Pourquoi « RAG hybride » ?** Cette approche relève du Graph RAG au sens large, qui regroupe les méthodes où la génération s'appuie sur des informations récupérées dans un graphe ([Peng et al., 2024](https://arxiv.org/abs/2408.08921)). Plus précisément, elle suit une architecture **hybride** ([Sarmah et al., 2024](https://arxiv.org/abs/2408.04948)) : la recherche vectorielle sélectionne les concepts et les thésaurus pertinents, puis le graphe de connaissances fournit leurs relations exactes. Contrairement au GraphRAG de Microsoft, où le graphe est construit par le LLM à partir de textes, le graphe utilisé ici vient directement des relations SKOS d'Opentheso : il est fiable et ne dépend pas des erreurs du modèle.
> 

---

## 2. Architecture

![architecture-rag-hybride.svg](RAG%20hybride/architecture-rag-hybride.svg)

> **Principe** : chaque information est stockée une seule fois. Les attributs sont dans la base vectorielle, les relations dans le graphe. Le lien entre les deux est l'identifiant `id_concept`.
> 

---

## 3. Contenu des bases

### 3.1 Base vectorielle des concepts

Un élément par concept. Tous les concepts sont stockés, complets ou non.

| Champ | Rôle |
| --- | --- |
| `id_concept` | identifiant unique `idTheso/id` (par ex. `th943/1006`) |
| `uri` | URI du concept dans Opentheso |
| `prefLabel` | terme préférentiel |
| `altLabel` | synonymes |
| `definition` | définition |
| `id_opentheso` *(technique)* | id d'origine dans Opentheso |
| `id_theso` *(technique)* | thésaurus du concept, pour les mises à jour par thésaurus |
| `complet` *(technique)* | vrai si les 5 champs sont remplis, pour choisir les exemples |
| `hash` *(technique)* | empreinte du contenu, pour détecter les changements |

**Ce que la recherche renvoie pour un concept** : toujours ses **5 attributs**, rassemblés à partir des deux bases.

| Attribut | Lu dans |
| --- | --- |
| `prefLabel` | base vectorielle (métadonnées) |
| `altLabel` | base vectorielle (métadonnées) |
| `definition` | base vectorielle (métadonnées) |
| `broader` | graphe de connaissances (lien `BROADER` qui part du concept), libellés lus dans la base vectorielle |
| `narrower` | graphe de connaissances (liens `BROADER` qui arrivent sur le concept), libellés lus dans la base vectorielle |

> Les 5 attributs sont toujours présents dans la sortie. Un attribut vide dans Opentheso reste vide : seuls 0,9 % des concepts ont les 5 attributs remplis.
> 

### 3.2 Base vectorielle des thésaurus

Un élément par thésaurus, ou un par branche pour les grands thésaurus (voir décision 8).

| Champ | Rôle |
| --- | --- |
| `id_theso` | identifiant du thésaurus |
| `titre` | titre réel |
| `nb_concepts` | nombre de concepts |
| `branche` | nom de la branche décrite, vide pour un petit thésaurus |
| `hash` *(technique)* | empreinte, pour détecter les changements |

### 3.3 Graphe de connaissances

| Élément | Contenu |
| --- | --- |
| Nœud `Concept` | uniquement `id_concept` |
| Nœud `Thesaurus` | uniquement `id_theso` |
| Relation `BROADER` | entre deux concepts, de l'enfant vers le parent |
| Relation `APPARTIENT` | entre un concept et son thésaurus |

> 
> 
> 
> La relation *narrower* est l'inverse de la relation *broader* : là où *broader* relie un enfant à son parent, *narrower* relie le parent à ses enfants. Stocker les deux reviendrait donc à enregistrer deux fois la même information, avec un risque d'incohérence lors des mises à jour.
> 
> C'est pourquoi seule la relation `BROADER` est stockée dans le graphe, orientée de l'enfant vers le parent. La relation *narrower* s'en déduit en lisant ce même lien dans le sens inverse :
> 
> - **de l'enfant vers le parent** : on obtient le *broader* du concept ;
> - **du parent vers l'enfant** : on obtient ses *narrower*.
> 
> Il n'y a aucun attribut dans le graphe et aucune relation dans la base vectorielle.
> 

---

## 4. Document et métadonnées

Chaque élément d'une base vectorielle est formé de deux parties :

| Partie | Définition | Stockée ? |
| --- | --- | --- |
| **Document** | le texte donné au modèle d'embedding `bge-m3` pour calculer le vecteur | Non : il sert seulement au calcul du vecteur |
| **Métadonnées** | les informations gardées avec le vecteur, relues quand l'élément est retrouvé | Oui |

> Le document sert à **trouver** l'élément par le sens, les métadonnées servent à **l'utiliser** une fois trouvé.
> 

### 4.1 Concepts

**Document** : texte construit à partir des attributs remplis du concept. Un champ vide n'est pas écrit.

```
Terme : générateur électrique alternatif
Synonymes : alternateur
Définition : Générateur électrique produisant, à partir d'une source d'énergie
             mécanique, un courant électrique alternatif.
Terme générique : générateur électrique
```

| Ligne | Origine | Pourquoi |
| --- | --- | --- |
| Terme | `prefLabel` | le nom du concept |
| Synonymes | `altLabel` (20 au maximum) | les autres façons de le nommer |
| Définition | `definition` (1 500 caractères au maximum) | son sens précis |
| Terme générique | nom du broader, lu dans le graphe au moment du calcul | distinguer les homonymes (« chapelle » en architecture ou en orfèvrerie) |

Les narrower ne sont pas dans le document (voir décision 4).

**Métadonnées** :

```
id_concept   : th799/T69-5065
uri          : <http://data.culture.fr/thesaurus/resource/ark:/67717/T69-5065>
prefLabel    : générateur électrique alternatif
altLabel     : [alternateur]
definition   : Générateur électrique produisant, à partir d'une source d'énergie...
id_opentheso : T69-5065        (technique)
id_theso     : th799           (technique)
complet      : vrai            (technique)
hash         : 3f9a1c…         (technique)
```

Le broader sert à calculer le vecteur mais n'est pas dans les métadonnées : la relation reste uniquement dans le graphe.

### 4.2 Thésaurus

**Document** : le titre, suivi d'environ 150 libellés de concepts du thésaurus. Les concepts de tête viennent d'abord, puis un échantillon stable d'autres concepts (le même à chaque mise à jour).

```
Thésaurus : Ceramique_Lyon
Concepts : céramique | poterie | faïence | grès | porcelaine | tesson | …
```

| Ligne | Origine | Pourquoi |
| --- | --- | --- |
| Thésaurus | `titre` | le nom du thésaurus |
| Concepts | libellés de ses concepts (150 au maximum) | un titre seul, comme « theso1 » ou « Test PDF no images », ne dit rien du contenu : les libellés décrivent le domaine couvert |

**Métadonnées** :

```
id_theso    : th843
titre       : Ceramique_Lyon
nb_concepts : 263
hash        : b72e04…    (technique)
```

### 4.3 Pourquoi séparer document et métadonnées

- Le document peut contenir des informations non stockées (le broader, les libellés des concepts) sans dupliquer les données. Chaque information garde une seule copie : les attributs dans les métadonnées, les relations dans le graphe.
- Les métadonnées restent simples : seulement les champs utiles quand on retrouve un élément, plus quelques champs techniques pour les mises à jour et les filtres.
- Si le document change, le vecteur est recalculé (par exemple si un broader change, ou si de nouveaux concepts entrent dans l'échantillon d'un thésaurus). L'empreinte (`hash`) détecte ce changement.

---

## 5. Décisions de conception

### Décision 1 : `id_concept = idTheso/id`

Opentheso numérote les concepts à l'intérieur de chaque thésaurus, donc le même numéro peut désigner des concepts différents :

| id | thésaurus | concept |
| --- | --- | --- |
| 0001 | th717 | Pergamos |
| 0001 | th467 | Aérophones |

Avec l'id seul, ces deux concepts seraient fusionnés en un seul nœud et le graphe serait faux. On utilise donc `th717/0001` et `th467/0001`, à l'identique dans les deux bases.

### Décision 2 : un seul lien `BROADER` pour broader et narrower

Broader et narrower sont le même lien vu des deux côtés. On le stocke une seule fois, avec une flèche qui va toujours de l'enfant vers le parent :

```
Orientation de l'érosion ──BROADER──▶ TBL_enregistrement
```

- **De gauche à droite** : le broader de *Orientation de l'érosion* est *TBL_enregistrement*.
- **De droite à gauche** : un narrower de *TBL_enregistrement* est *Orientation de l'érosion*.

Stocker les deux liens séparément créerait tôt ou tard des contradictions. 

### Décision 3 : l'empreinte (hash) pour les mises à jour

Le hash est un code court calculé à partir de tout le contenu d'un concept. Si un seul caractère change, le code change.

**Ce n'est pas un vecteur.** Il est calculé **sans modèle d'IA**, avec l'algorithme **SHA-1** de la bibliothèque standard de Python (`hashlib`) :

1. tout le contenu du concept est écrit sous forme de texte (format JSON, champs toujours dans le même ordre) : prefLabel dans toutes les langues, altLabel, définition, notes, URI, liens broader et narrower et leurs libellés. Seule la date de modification est exclue, pour qu'un simple changement de date ne compte pas comme une modification ;
2. SHA-1 transforme ce texte en un code de 40 caractères.

```
"vase à deux anses..."    →  3f9a1c7e2b...
"vase à deux anses,..."   →  b72e04d91a...   (une virgule ajoutée : code complètement différent)
```

|  | Vecteur | Hash |
| --- | --- | --- |
| Calculé par | le modèle bge-m3, sur GPU | l'algorithme SHA-1, instantané |
| Forme | 1 024 nombres | 40 caractères |
| Sert à | trouver des concepts de sens proche | savoir si le concept a changé |
| Deux textes presque identiques donnent | des vecteurs proches | des codes complètement différents |

Pour un thésaurus, le hash est calculé de la même façon, à partir de son titre, de son nombre de concepts et du document de chaque branche.

À chaque mise à jour :

- **même empreinte** : rien n'a changé, on ne fait rien ;
- **empreinte différente** : le concept a été modifié, on le ré-encode ;
- **concept absent** : il est nouveau, on l'ajoute ;
- **concept disparu de l'API** : on le retire des deux bases.

Sans empreinte, il faudrait ré-encoder les quelque 400 000 concepts à chaque mise à jour, soit environ 20 minutes de calcul sur les GPU du serveur (et plusieurs heures sur une machine sans GPU), alors que seule une petite partie des concepts change.

### Décision 4 : le vecteur d'un concept inclut le nom de son générique

Le vecteur est calculé à partir d'un texte qui contient le terme, les synonymes, la définition et le nom du broader :

```
Terme : chapelle
Définition : Petit lieu de culte...
Terme générique : édifice religieux
```

Cela permet de distinguer les homonymes :

| Concept | Générique | Sens |
| --- | --- | --- |
| chapelle | édifice religieux | un bâtiment |
| chapelle | orfèvrerie | des objets liturgiques |

Ce texte sert uniquement à calculer le vecteur. Il n'est pas stocké, et le lien reste dans le graphe.

**Pourquoi pas les narrower ?**

|  | Broader | Narrower |
| --- | --- | --- |
| Combien ? | en général 1 | de 0 à plusieurs milliers |
| Dit quoi ? | ce qu'est le concept | ce qu'il contient |
| Change souvent ? | rarement | à chaque ajout d'enfant |
| Présent pour un concept nouveau ? | souvent connu | jamais |

Le vecteur sert à **une seule chose : comparer la question de l'utilisateur au concept**. Plus les deux textes se ressemblent, plus le concept est trouvé facilement.

**Exemple.** La question de l'utilisateur :

```
vase à deux anses pour transporter le vin
```

Texte du concept **sans narrower** (choix retenu) :

```
Terme : amphore
Définition : vase à deux anses pour transporter des liquides, surtout le vin
Terme générique : récipient de transport
```

→ Il **ressemble beaucoup** à la question (vase, deux anses, transporter, vin) : le concept est trouvé. ✅

Texte du concept **avec narrower** :

```
Terme : amphore
Définition : vase à deux anses pour transporter des liquides, surtout le vin
Terme générique : récipient de transport
Spécifiques : amphore grecque | amphore phénicienne | amphore étrusque | amphore punique |
              amphore crétoise | amphore byzantine | amphore de Tarraconaise | amphorette | ...
```

→ La moitié du texte devient une **liste de noms** que la question ne contient pas : le texte **ressemble moins** à la question, et le concept risque d'être moins bien trouvé. ❌

> Le vecteur doit ressembler à **ce que l'utilisateur écrit**, et l'utilisateur n'écrit jamais la liste des enfants d'un concept.
> 

Deux autres raisons :

- certains concepts ont des milliers d'enfants : le vecteur représenterait la liste des enfants plutôt que le concept lui-même ;
- ajouter un enfant obligerait à recalculer le vecteur du parent.

**Les narrower ne sont pas perdus** : ils sont dans le graphe. Une fois le concept trouvé, le graphe donne ses narrower, qui sont affichés avec le résultat et donnés au LLM (voir 3.1). Ce choix est raisonné mais pas encore mesuré : on pourra tester une version avec narrower dans le vecteur et comparer les résultats.

### Décision 5 : le vecteur d'un thésaurus

Le vecteur est calculé à partir du titre et d'environ 150 libellés de ses concepts, les concepts de tête d'abord. Un titre seul, comme `theso1` ou `Test PDF no images`, ne dit rien du contenu. Seuls `id_theso`, `titre` et `nb_concepts` sont stockés.

### Décision 6 : Neo4j pour le graphe

Voir la page « Base de données graphe ».

### Décision 7 : les relations viennent des URI de l'API

Les relations parent / enfant (`broader` / `narrower`) sont récupérées directement depuis l'**API Opentheso**, au format **SKOS**. Dans ce format, le parent d'un concept n'est pas donné par son nom, mais par son **URI** : une adresse unique, qui désigne un seul concept.

```
amphore  →  parent : http://.../th943/12345
```

Retrouver un parent par son **nom** poserait plusieurs problèmes :

- deux concepts peuvent porter le même nom dans un thésaurus (homonymes) : lequel choisir ?
- le nom peut être écrit dans une autre langue (« Behälter » au lieu de « récipient ») ;
- une petite différence d'écriture (majuscule, accent, espace) empêche de le retrouver.

Avec l'URI, il n'y a aucune recherche à faire et aucune ambiguïté.

**Vérification** : sur le thésaurus Siamois, les **244 relations sur 244** sont exactes.

---

## 6. Fonctionnement

### 6.1 Mise à jour depuis l'API

Pour chaque thésaurus :

1. Télécharger le thésaurus depuis l'API et extraire les concepts avec leurs relations.
2. Comparer les empreintes avec la base vectorielle : ajouter, ré-encoder ou retirer.
3. Si le thésaurus a changé, mettre à jour son graphe (nœuds, `APPARTIENT`, `BROADER`).
4. Mettre à jour l'élément du thésaurus, seulement si son titre, sa taille ou ses libellés ont changé.

**Sécurités :**

- un thésaurus que l'API ne renvoie pas (erreur, réponse vide) n'est jamais effacé ;
- un thésaurus en erreur ne bloque pas les autres.

### 6.2 Trouver la famille d'un concept (broader et narrower)

1. **Graphe** : on suit la flèche `BROADER` qui part du concept (son broader) et celles qui arrivent sur lui (ses narrower). On obtient des `id_concept`.
2. **Base vectorielle** : on lit les attributs de ces `id_concept`.

![2-famille-concept_1.png](RAG%20hybride/2-famille-concept_1.png)

Résultat réel :

- **broader** : TBL_enregistrement
- **narrower** : N, NE, E, SE, S, SW

Les narrower sont trouvés sans aucun lien NARROWER stocké, simplement en lisant `BROADER` dans l'autre sens.

### 6.3 Recherche à partir d'un texte

1. **Base vectorielle : concepts proches**
    - Qdrant trouve les concepts les plus proches du texte ;
    - le **reranker** relit ces candidats avec la requête et les reclasse (décision 10) ;
    - si la requête est courte, les concepts dont le libellé est **exactement** la requête passent en tête (décision 12) ;
    - les **copies** d'un même concept n'occupent qu'une place (décision 11).
2. **Base vectorielle : thésaurus proches** : la requête est comparée à chaque thésaurus, et un grand thésaurus prend le score de sa meilleure branche (décision 8).
3. **Graphe** : les broader et narrower de chaque concept trouvé.
4. **Base vectorielle** : les attributs de ces voisins.
5. **Classement des thésaurus** : 40 % pour le vote des concepts trouvés, 60 % pour la similarité directe. Ce poids a été mesuré par évaluation (décision 13).
6. **Mise en forme** : le résultat est converti en texte, prêt à être inséré dans le prompt du LLM.

**Options** : ne garder que les concepts complets, exclure certains concepts, se limiter à certains thésaurus.
Les thésaurus de test sont toujours ignorés (décision 9).

## 7. Taille des données

### Vue d'ensemble

|  | Nombre |
| --- | --- |
| Thésaurus listés par l'API | 469 |
| Thésaurus qui contiennent des concepts | **344** |
| Thésaurus sans concept (vides, privés ou sans réponse de l'API) | 124 |
| Thésaurus en erreur côté API | 1 |
| dont thésaurus de test, gardés mais ignorés par la recherche | 84 |
| Concepts | **407 761** |
| Concepts complets (les 5 champs remplis) | 3 780 (0,9 %) |
| Concepts avec seulement un prefLabel | 45 559 (11,2 %) |

### Remplissage des champs des concepts

| Champ | Concepts où il est rempli | % |
| --- | --- | --- |
| `prefLabel` | 407 760 | 100 % |
| `broader` | 323 165 | 79,3 % |
| `altLabel` | 89 265 | 21,9 % |
| `definition` | 88 716 | 21,8 % |
| `narrower` | 46 793 | 11,5 % |
| **les 5 à la fois (complet)** | **3 780** | **0,9 %** |

> C'est pourquoi le système stocke **tous** les concepts, et pas seulement les complets. Les 3 780 concepts complets restent disponibles grâce au champ `complet` .
> 

### Taille des thésaurus

| Nombre de concepts par thésaurus | Nombre de thésaurus |
| --- | --- |
| moins de 10 | 54 |
| 10 à 99 | 134 |
| 100 à 999 | 92 |
| 1 000 à 9 999 | 55 |
| 10 000 ou plus | 9 |

**Taille médiane** : 64 concepts. **Minimum** : 1. **Maximum** : 38 987.

**Les plus grands thésaurus :**

| Thésaurus | id | Concepts |
| --- | --- | --- |
| Liste d'autorités Auteurs - Joconde | th69 | 38 987 |
| Entités producteurs | th87 | 38 327 |
| Liste d'autorités Représentation - Joconde | th73 | 32 796 |
| Initiale - Sujets | th1092 | 19 202 |
| Thesaurus_INRAE | th956 | 16 313 |

### Taille de chaque base

| Base | Éléments | Nombre |
| --- | --- | --- |
| Base vectorielle des concepts | un élément par concept | ≈ 407 761 |
| Base vectorielle des thésaurus | un élément par thésaurus, ou par branche (grands thésaurus) | 1 449 éléments pour 344 thésaurus |
| Graphe : nœuds `Concept` | un par concept | ≈ 407 761 |
| Graphe : nœuds `Thesaurus` | un par thésaurus | 344 |
| Graphe : relations `APPARTIENT` | une par concept | ≈ 407 761 |
| Graphe : relations `BROADER` | une par lien parent-enfant | ≈ 343 865 |

---

## 8. Technologies

| Rôle | Outil | Pourquoi |
| --- | --- | --- |
| Base vectorielle | **Qdrant** (Docker, sur le serveur) | rapide, filtres sur les métadonnées (thésaurus, concepts complets), tourne en local |
| Modèle d'embedding | **BAAI/bge-m3** (sentence-transformers, GPU) | multilingue (français, anglais, allemand… comme les thésaurus), textes longs (1 024 tokens), vecteurs de 1 024 dimensions |
| Reranker | **BAAI/bge-reranker-v2-m3** | relit la requête et chaque candidat ensemble, plus précis que la seule comparaison de vecteurs |
| Graphe de connaissances | **Neo4j 5** (Docker, sur le serveur) | Voir la page « Base de données graphe ». |

> Toutes les données restent sur le serveur  : aucun appel à un service extérieur pendant la recherche.
> 

### Construction des bases (étapes)

| Étape | Contenu | Résultat | Durée |
| --- | --- | --- | --- |
| 0. Extraction | téléchargement de tous les thésaurus depuis l'API Opentheso, enregistrés sur disque | 469 listés → 344 avec concepts, 407 761 concepts | 4 min |
| 1. Base des concepts | un vecteur par concept | 407 761 concepts, dont 3 780 complets, 0 échec d'encodage | 20 min |
| 2. Base des thésaurus | un vecteur par thésaurus ou par branche | 344 thésaurus, 1 449 documents | 40 s |
| 3. Graphe | nœuds et relations | 407 761 Concept, 344 Thesaurus, 343 865 BROADER | 23 s |

Ces durées courtes s'expliquent par le serveur de l'Université de Versailles utilisé pour la construction, équipé de deux GPU NVIDIA H100 NVL.

---

## 9. Améliorations apportées après les premiers résultats

Après la construction des bases, une première évaluation a montré plusieurs problèmes. Voici les 6 corrections apportées. Chacune a été gardée parce qu'elle améliore les résultats.

---

### Décision 8 : découper les grands thésaurus en branches

---

#### Un thésaurus est un arbre

Dans Opentheso, un thésaurus n'est pas une simple liste de concepts : les concepts sont rangés **en arbre**.
Chaque concept indique **son parent** (le champ `broader`, « terme générique »), choisi par les auteurs du thésaurus.

- Le parent est **toujours dans le même thésaurus** : chaque thésaurus est un arbre à lui seul.
- Un concept **sans parent** est un **concept de tête** : il est en haut de l'arbre.
- Les **enfants** d'un concept sont les concepts dont il est le parent.

Exemple simplifié (PACTOLS) :

![image.png](RAG%20hybride/image.png)

> Pour savoir où se trouve « amphore », on remonte ses parents :
amphore → récipient de transport → objets mobiles → **entités matérielles**.
> 

#### Le problème

Un grand thésaurus parle de beaucoup de sujets différents. Si on le décrit avec **un seul vecteur**, ce vecteur est un **mélange flou** de tous les sujets, et il ne ressemble à aucune question précise.
Avant le découpage, PACTOLS n'était trouvé en 1re position que dans **1,1 %** des cas.

#### La solution : un vecteur par branche

Une **branche** est un concept de tête **avec tous ses descendants** (enfants, enfants des enfants…).
Chaque branche reçoit son propre vecteur, calculé à partir de son nom et de 150 libellés de ses concepts.

![image.png](RAG%20hybride/image%201.png)

> Ici, « entités matérielles » était trop grande (plus de 2 000 concepts) : elle a été remplacée par ses sous-branches, « objets mobiles » et « environnements bâtis ».
> 

#### Comment les branches sont construites

On ne devine rien : on suit seulement les liens parent / enfant écrits dans le thésaurus.

1. **Départ** : chaque concept de tête commence une branche.
2. **Rangement** : en descendant l'arbre, chaque concept rejoint la branche de son concept de tête. Un concept qui a deux parents n'est rangé qu'une fois.
3. **Branche trop grande** (plus de 2 000 concepts) : elle est remplacée par ses sous-branches.
4. **Branche trop petite** (moins de 20 concepts) : elle rejoint une branche « autres concepts ». C'est le cas des concepts de tête isolés comme « Hadrien » ou « garum ».
5. **Maximum** : 40 branches par thésaurus.

| Règle | Valeur |
| --- | --- |
| Un thésaurus est découpé s'il a | 500 concepts ou plus |
| Une branche est redécoupée si elle a | plus de 2 000 concepts |
| Une branche rejoint « autres concepts » si elle a | moins de 20 concepts |
| Nombre maximal de branches | 40 |
| Thésaurus sans hiérarchie (aucun lien parent) | un seul vecteur, car on ne peut pas le découper |

#### Pendant la recherche

La question est comparée à **toutes les branches**. Chaque thésaurus prend le score de **sa meilleure branche**. Le résultat reste **le thésaurus**, et la branche est seulement indiquée pour expliquer le résultat.

![image.png](RAG%20hybride/image%202.png)

> On prend la **meilleure** branche et non la **moyenne** : la moyenne mélangerait de nouveau tous les sujets et redeviendrait floue.
> 

#### Résultat

- **78 thésaurus** découpés, **1 449 éléments** au total dans la base des thésaurus (au lieu de 344).
- PACTOLS : **25 branches**. Il est trouvé en 1re position dans **11,6 %** des cas, au lieu de **1,1 %**.

### Décision 9 : ignorer les thésaurus de test

**Le constat**

Dans Opentheso, des utilisateurs ont créé des thésaurus **pour s'entraîner** ou **pour faire des démonstrations**. Ce ne sont pas de vrais thésaurus :

```
testTest · theso1 · Test PDF no images · mon theso ...
```

Il y en a **84**. Ils contiennent souvent les mêmes concepts d'exemple, recopiés : lait, vase, Lyon…

**Le problème**

Quand on cherche « lait », les premiers résultats sont ces faux thésaurus :

```
1. lait  [testTest]        ❌ faux thésaurus
2. lait  [theso1]          ❌ faux thésaurus
3. lait  [Thésaurus de la désignation des objets mobiliers]   ✅ vrai thésaurus
```

**La solution**

Les 84 thésaurus de test sont mis dans une **liste**, et la recherche **ne les montre plus** :

```
1. lait  [Thésaurus de la désignation des objets mobiliers]   ✅
2. ...
```

> Ils ne sont **pas supprimés** des bases : ils sont seulement cachés pendant la recherche. Pour en réafficher un, il suffit de le retirer de la liste, sans rien reconstruire.
> 

**Résultat** : ils n'apparaissent plus dans les résultats.

---

### Décision 10 : relire les résultats avec un reranker

**Le constat**

La recherche par vecteurs transforme la question et chaque concept **séparément**, puis compare les deux vecteurs. C'est très rapide (on compare la question à des milliers de concepts), mais le modèle ne lit jamais la question et le concept **ensemble**. Il trouve souvent des concepts qui partagent des mots avec la question, sans comprendre ce que la question décrit.

**Le problème**

Le bon concept est souvent dans les résultats, mais **pas en premier**. Exemple réel du jeu d'évaluation :

```
Question : « Ensemble des dieux des peuples germaniques et scandinaves, tels Odin, Thor et Freyja »
Concept attendu : panthéon germanique

Recherche par vecteurs seule :
1. Thor
2. Odin
3. panthéon germanique   ← seulement 3e
```

Les vecteurs ramènent les concepts qui reprennent les **mots** de la question (Odin, Thor), alors que la question décrit un **ensemble** de dieux.

**La solution**

On ajoute un second modèle, le **reranker**. Il lit la question **et** un concept côte à côte, comme une paire, et donne un score de pertinence. Il est plus précis, mais plus lent : impossible de l'appliquer à tous les concepts. La recherche se fait donc en deux étapes :

1. **Recherche par vecteurs** (rapide) : on garde les 30 meilleurs concepts.
2. **Reranker** (précis) : il relit ces 30 concepts et les reclasse par score **décroissant** (le plus grand score en premier).

```
Question
   ↓  recherche par vecteurs (rapide, sur 407 761 concepts)
30 concepts candidats
   ↓  reranker (précis, relit chaque paire question + concept)
30 concepts reclassés  →  les 10 premiers sont affichés
```

Même exemple après le reranker : panthéon germanique passe de la **3e** à la **2e** place. Le reranker améliore le classement, mais il n'est pas parfait.

**Exemple illustratif** (pour montrer le principe)

Question : « récipient à deux anses pour transporter le vin »

| Rang | Après la recherche par vecteurs | Après le reranker |
| --- | --- | --- |
| 1 | anse | **amphore** |
| 2 | vin | cruche |
| 3 | récipient | récipient |
| 4 | amphore | anse |

Les vecteurs trouvent des concepts qui reprennent des **mots** de la question. Le reranker comprend que la question **décrit** une amphore.

**Résultat** (2 469 questions du jeu d'évaluation) :

|  | Vecteurs seuls | Vecteurs + reranker |
| --- | --- | --- |
| Bon concept en 1re position | 32 % | **45 %** |
| Bon concept dans les 10 premiers | 70 % | **73 %** |
| Temps par recherche | très rapide | environ 0,15 seconde de plus |

---

### Décision 11 : une copie n'occupe qu'une place

**Le constat**

Un même concept est parfois **copié tel quel** dans plusieurs thésaurus. Par exemple, « amphore », avec exactement la même définition, se trouve dans 3 thésaurus :

```
th799 : amphore  « Grand vase ovoïde, à deux anses... »
th103 : amphore  « Grand vase ovoïde, à deux anses... »   ← même texte
th211 : amphore  « Grand vase ovoïde, à deux anses... »   ← même texte
```

**Le problème**

La recherche affiche 10 résultats, et ces 3 copies prennent **3 places** pour la même information :

```
1. canthare
2. amphore [th799]
3. amphore [th103]   ← répétition
4. amphore [th211]   ← répétition
5. ...
```

**La solution**

Les copies sont **regroupées sur une seule ligne** :

```
1. canthare
2. amphore [th799]   (aussi dans : th103, th211)
3. stamnos
4. skyphos
5. ...
```

Les places libérées montrent **d'autres concepts utiles**, et l'information n'est pas perdue : on sait toujours que « amphore » existe aussi dans th103 et th211. Une copie compte aussi dans le vote pour son thésaurus (décision 13).

> **Seules les vraies copies sont regroupées** : même nom **et** même identifiant Opentheso, ou même nom **et** même définition. Deux « amphore » avec des définitions différentes (par exemple celle de PACTOLS et celle de Zoomathia) restent sur deux lignes : ce sont deux façons différentes de décrire le concept.
> 

**Résultat** : 10 concepts **différents** dans les résultats, au lieu de 7.

---

### Décision 12 : chercher d'abord le mot exact

**Le constat**

Quand la question n'est qu'un seul mot, le modèle de vecteurs a très peu d'information. Il se base alors en partie sur la **forme** du mot (ses morceaux de lettres) et pas seulement sur son sens. Il peut donc ramener un mot qui s'écrit de façon proche mais qui n'a rien à voir.

**Le problème**

« cathédrale » et « cathéter » commencent tous les deux par « cathé ». Sans contexte, leurs vecteurs sont proches :

```
Question : « cathédrale »

Recherche par vecteurs seule :
1. cathéter        ❌ terme médical
2. ...
3. cathédrale      ← le bon concept, mais pas en premier
```

**La solution**

Avant la recherche par vecteurs, on vérifie deux conditions :

1. la question est **courte** (6 mots au plus) ;
2. un concept porte **exactement** ce nom, ou l'a comme synonyme (sans tenir compte des majuscules ni de la ponctuation).

Si les deux sont vraies, ce concept est placé **en tête**, quel que soit le score des vecteurs :

```
Question : « cathédrale »

1. cathédrale      ← terme exact
2. ...             ← concepts proches trouvés par les vecteurs
```

**Pourquoi seulement pour une question courte ?**

Une question courte est souvent **un nom de concept** : l'utilisateur tape un terme. Une question longue est une **description** : aucun concept ne porte ce nom, et la recherche par vecteurs fait le travail.

| Question | Nombre de mots | Recherche du mot exact ? |
| --- | --- | --- |
| « amphore » | 1 | ✅ oui |
| « cathédrale » | 1 | ✅ oui |
| « Amphores de Narbonnaise » | 3 | ✅ oui |
| « vase à deux anses » | 4 | ✅ oui |
| « vase antique à deux anses pour transporter le vin » | 9 | ❌ non : recherche par vecteurs seulement |

> **Pourquoi 6 mots ?** C'est un choix pratique, pas une valeur mesurée : un nom de concept dépasse rarement 6 mots (« structure de combustion », « Amphores de Narbonnaise »), alors qu'une description en contient presque toujours plus. Cette valeur est réglable dans la configuration.
> 

> Les concepts au nom exact occupent **au plus la moitié** des places : le reste montre des concepts voisins, utiles au LLM.
> 

> **Limite** : l'orthographe doit être exacte, accents compris. « cathedrale » sans accent ne retrouve pas « cathédrale ».
> 

**Résultat** : si un concept porte exactement le nom demandé, il est toujours trouvé en premier. « amphore » trouve le concept « amphore », et « cathédrale » trouve « cathédrale ».

---

### Décision 13 : classer les thésaurus avec deux méthodes

**Problème**

Ici, on ne cherche plus un concept mais **le bon thésaurus**. Deux méthodes existent, et chacune se trompe dans des cas différents :

- **La similarité** : on compare la question au vecteur du thème de chaque thésaurus.
*Point faible* : un thésaurus peut parler du même sujet sans contenir le concept cherché.
- **Le vote** : on cherche les 10 concepts les plus proches de la question, puis on regarde dans quel thésaurus chacun est rangé. Chaque concept « vote » pour son thésaurus.
*Point faible* : un très grand thésaurus contient des concepts sur presque tout, il récolte donc des votes même quand il n'est pas le bon.

**Solution**

On combine les deux scores :

> **score final = 0,6 × similarité + 0,4 × vote**
> 

(le vote est la part des 10 concepts trouvés qui viennent du thésaurus : 4 concepts sur 10 → 0,4)

Cette méthode vient de la **fusion de résultats** en recherche d'information : quand plusieurs systèmes de recherche donnent chacun un score, on additionne ces scores, chacun multiplié par un poids qui représente la confiance qu'on lui accorde. Fox et Shaw (1994) ont montré que combiner plusieurs recherches donne de meilleurs résultats que chaque recherche seule. Vogt et Cottrell (1999) ont étudié la version pondérée utilisée ici, où les poids sont choisis à partir d'une évaluation.

Comme les deux méthodes ne se trompent pas sur les mêmes questions, l'une corrige souvent l'erreur de l'autre.

**Exemple 1 : la similarité se trompe, le vote corrige** (scores illustratifs)

Question : « vase antique ». Parmi les 10 concepts trouvés, 4 viennent de Joconde et aucun de Zoomathia.

| Thésaurus | Similarité | Vote | Score final |
| --- | --- | --- | --- |
| Zoomathia | **0,80** | 0 / 10 = 0,0 | 0,48 + 0,00 = 0,48 |
| Joconde | 0,65 | **4 / 10 = 0,4** | 0,39 + 0,16 = **0,55** ✓ |

Zoomathia (les animaux dans les textes antiques) ressemble au thème « Antiquité », donc la similarité seule le place en tête. Mais il ne contient pas de vases. Le vote le fait descendre, et Joconde passe devant.

**Exemple 2 : le vote se trompe, la similarité corrige** (scores illustratifs)

Question : « fibule ». Joconde, très grand, fournit 5 des 10 concepts trouvés. Le bon thésaurus, plus petit et spécialisé (« Parure »), n'en fournit que 2.

| Thésaurus | Similarité | Vote | Score final |
| --- | --- | --- | --- |
| Joconde | 0,45 | **5 / 10 = 0,5** | 0,27 + 0,20 = 0,47 |
| Parure | **0,85** | 2 / 10 = 0,2 | 0,51 + 0,08 = **0,59** ✓ |

Le vote seul choisirait Joconde. La similarité fait remonter Parure.

**Résultat**

| Méthode | Bon thésaurus en 1re position |
| --- | --- |
| Similarité seule | 43 % |
| Vote seul | 38 % |
| **Les deux ensemble** | **60 %** |

**Pourquoi 40 % vote + 60 % similarité** : 11 mélanges ont été testés (de 0 % à 100 % de vote, par pas de 10 %). Ce mélange donne le meilleur résultat (section 11.2).

---

## 10. Méthodologie d'évaluation

### 10.1 Jeu d'évaluation

|  | Nombre |
| --- | --- |
| Requêtes du jeu initial | 1 742 |
| Nouvelles requêtes (5 concepts par thésaurus, avec des descriptions générées par Gemini via l’API gratuite) | 1 000 |
| **Total** | **2 742** |
| Retirées : description vide, thésaurus attendu exclu (test) ou absent | 273 |
| **Requêtes évaluées** | **2 469** |

Chaque requête contient :

- la **requête** : une description du concept en langage naturel ;
- la **réponse attendue** : le concept (`id_concept`) et son thésaurus (`id_thesaurus`) ;
- la **source** : jeu initial ou nouvelles requêtes ;
- la **richesse** : nombre d'attributs remplis en plus du prefLabel (0 = prefLabel seul, 4 = concept complet).

### 10.2 Mesures

| Mesure | Définition |
| --- | --- |
| **Hit@K** | part des requêtes dont la bonne réponse est dans les K premiers résultats |
| **MRR@10** | moyenne de 1/rang de la bonne réponse (0 si elle n'est pas dans les 10 premiers). Récompense une bonne réponse placée haut. |
| **Rang médian** | rang de la bonne réponse pour la requête du milieu (parmi celles trouvées) |
| **Non trouvé** | part des requêtes dont la bonne réponse n'est pas dans les 10 premiers |

**A. Hit@1, Hit@5 et MRR : définitions et calcul**

Ces trois métriques évaluent un système de recherche (Base vectorielle, RAG, recherche de concepts et recherche de thésaurus). Elles répondent à une seule question : à quelle position ressort la bonne réponse ?

---

**A.1 La notion centrale : le rang rᵢ**

Pour chaque requête `i`, on note la position du bon résultat dans la liste renvoyée.

```
Requête : "voiture électrique"

Rang 1 → avion
Rang 2 → voiture thermique
Rang 3 → véhicule électrique      ← BON résultat
Rang 4 → vélo
Rang 5 → train

r_i = 3
```

Si le bon résultat n'est pas dans les `k` premiers : `r_i = ∞`, contribution `0`.

**Le rang dépend de k**

On n'observe un rang que dans la limite de ce qu'on a demandé. Avec `k = 5`, une réponse en 7ᵉ position est simplement **absente** : impossible de savoir si elle était 7ᵉ ou 400ᵉ.

Interroger à `k = 10` même pour un Hit@5 : cela ne change ni Hit@1 ni Hit@5, mais distingue un quasi-succès d'un échec total.

---

**A.2 Hit@1**

> **Hit@1  =  (1 / N)  ×  Σᵢ  1[ rᵢ = 1 ]**
> 
> 
> *somme sur i = 1 … N*
> 

***Proportion de requêtes où le bon résultat est classé premier.***

Exemple sur 5 requêtes, interrogation à `k = 5` :

| Requête | Rang du bon résultat | Compte pour Hit@1 |
| --- | --- | --- |
| Q1 | 1 | 1 |
| Q2 | 3 | 0 |
| Q3 | 1 | 1 |
| Q4 | absent | 0 |
| Q5 | 2 | 0 |

> **Hit@1  =  (1 + 0 + 1 + 0 + 0) / 5  =  0,40**
> 

👉 Bon résultat en première position dans **40 % des requêtes**.

---

**A.3 Hit@5**

> **Hit@5  =  (1 / N)  ×  Σᵢ  1[ rᵢ ≤ 5 ]**
> 

***Proportion de requêtes où le bon résultat apparaît dans les 5 premiers.***

| Requête | Rang | Compte pour Hit@5 |
| --- | --- | --- |
| Q1 | 1 | 1 |
| Q2 | 3 | 1 |
| Q3 | 1 | 1 |
| Q4 | absent | 0 |
| Q5 | 2 | 1 |

> **Hit@5  =  (1 + 1 + 1 + 0 + 1) / 5  =  0,80**
> 

👉 Dans **80 % des requêtes**, le bon résultat est dans les 5 premiers.

---

**A.4 MRR@k**

**Mean Reciprocal Rank** : plus le bon résultat est haut, plus il rapporte.

> **MRR@k  =  (1 / N)  ×  Σᵢ  ( 1 / rᵢ )**
> 
> 
> *avec 1 / rᵢ = 0 si rᵢ > k*
> 

Valeur de chaque rang :

```
rang 1 → 1/1 = 1
rang 2 → 1/2 = 0,500
rang 3 → 1/3 = 0,333
rang 4 → 1/4 = 0,250
rang 5 → 1/5 = 0,200
absent →       0
```

Exemple :

| Requête | Rang | Rang réciproque |
| --- | --- | --- |
| Q1 | 1 | 1,000 |
| Q2 | 3 | 0,333 |
| Q3 | 1 | 1,000 |
| Q4 | absent | 0,000 |
| Q5 | 2 | 0,500 |
| **Somme** |  | **2,833** |

> **MRR@5  =  2,833 / 5  ≈  0,567**
> 

**Effet de k**

Avec `k = 10` et Q4 découvert en 7ᵉ position, sa contribution passe de `0` à `1/7 = 0,143` :

> **MRR@10  =  2,976 / 5  ≈  0,595**
> 

Hit@1 et Hit@5 sont inchangés. **Toujours noter la profondeur : MRR@5, MRR@10, jamais « MRR » seul.**

**Le MRR n'est pas un pourcentage**

C'est une moyenne de rangs inversés, pas une proportion de requêtes. On écrit **MRR@5 = 0,567**, sans symbole pourcentage. Un MRR de 0,567 correspond à un rang typique légèrement inférieur à 2.

---

**A.5 Différence entre les trois**

| Métrique | Question posée |
| --- | --- |
| **Hit@1** | Le bon résultat est-il **premier** ? |
| **Hit@5** | Est-il quelque part dans les **5 premiers** ? |
| **MRR@k** | **En moyenne, à quel point** est-il bien classé ? |

Hit@1 et Hit@5 sont binaires au seuil choisi. Le MRR est le seul à tenir compte de la position exacte.

```
Système A : bon résultat au rang 1
Système B : bon résultat au rang 5
```

Hit@5 : les deux obtiennent 1, **score identique**.
MRR : A = 1,0 contre B = 0,2, **les deux sont séparés**.

Inversement, le MRR seul s'interprète mal en pratique. Hit@1 répond à « puis-je automatiser sans relecture ? », Hit@5 à « si je propose 5 candidats, la bonne réponse est-elle dans la liste ? ». Les trois se rapportent ensemble.

---

**A.6 Exemple complet sur 100 requêtes**

Interrogation à `k = 5`.

| Position du bon résultat | Nombre de requêtes |
| --- | --- |
| Rang 1 | 40 |
| Rang 2 | 25 |
| Rang 3 | 15 |
| Rang 4 | 6 |
| Rang 5 | 4 |
| Absent du top-5 | 10 |
| **Total** | **100** |

> **Hit@1  =  40 / 100  =  0,40**
> 

> **Hit@5  =  (40 + 25 + 15 + 6 + 4) / 100  =  0,90**
> 

> **MRR@5  =  [ 40×1 + 25×(1/2) + 15×(1/3) + 6×(1/4) + 4×(1/5) + 10×0 ] / 100**
> 
> 
> **=  (40 + 12,5 + 5 + 1,5 + 0,8) / 100  =  59,8 / 100  =  0,598**
> 

⚠️ **Pourquoi il faut garder le rang exact de chaque requête**

Ce calcul n'est possible que parce que les rangs 4 et 5 sont comptés séparément. C'est une différence de fond entre Hit@k et MRR.

**Hit@5 se contente d'un oui/non.** Rang 4 ou rang 5, peu importe : les deux sont ≤ 5, donc les deux comptent pour 1. Une ligne agrégée « 10 requêtes entre le rang 4 et le rang 5 » suffit.

**Le MRR a besoin du rang exact**, parce que chaque rang a une valeur différente :

```
rang 4 → 1/4 = 0,25
rang 5 → 1/5 = 0,20
```

Avec la seule information « 10 requêtes au rang 4-5 », impossible de trancher :

```
si les 10 sont au rang 4 → 10 × 0,25 = 2,50
si les 10 sont au rang 5 → 10 × 0,20 = 2,00
```

Ici l'écart reste faible parce que la tranche est étroite. Avec une tranche large, il devient massif. Exemple avec « 50 requêtes entre le rang 2 et le rang 10 » :

```
si toutes au rang 2  → 50 × 0,50 = 25
si toutes au rang 10 → 50 × 0,10 =  5
```

Le MRR passerait de 0,25 à 0,05 selon l'hypothèse retenue. La métrique ne veut alors plus rien dire.

**En pratique :** enregistrer une ligne par requête avec son rang exact (`1, 3, 1, absent, 2, 7...`). Tout se recalcule ensuite à partir de cette liste. En ne conservant que des totaux par tranche, le MRR est définitivement perdu.

---

**A.7 Contrôle de cohérence**

> **Hit@1  ≤  MRR@k  ≤  Hit@k**
> 

Toujours vrai. Sur l'exemple ci-dessus : `0,40 ≤ 0,598 ≤ 0,90` ✅

Si l'encadrement n'est pas respecté, il y a une erreur de calcul.

### 10.3 Trois évaluations

| Évaluation | Question posée | Bonne réponse |
| --- | --- | --- |
| **Base des concepts** | la requête retrouve-t-elle son concept ? | le concept attendu (ou une copie) |
| **Base des thésaurus** | la requête, comparée directement aux thésaurus, retrouve-t-elle le bon ? | le thésaurus attendu |
| **Rattachement** (vote + similarité) | le classement final propose-t-il le bon thésaurus ? | le thésaurus attendu |

> **Rattachement : le concept recherché est retiré des résultats.** En usage réel, le concept à ranger est **nouveau** : il n'existe pas encore dans la base. Si on le laissait, le vote retrouverait simplement le concept lui-même et donnerait directement son thésaurus : le score serait faussement élevé.
> 

---

## 11. Évaluation des bases vectorielles et du graphe

### 11.1 Base vectorielle des concepts

Cette partie présente l'évaluation de la base vectorielle des concepts. Deux méthodes de recherche sont comparées : la recherche par vecteurs seule (sans reranker) et la recherche avec reranker.

Pour cela, un jeu de test de 2 469 requêtes a été construit. Il contient des concepts de richesse différente : 1 708 requêtes portent sur un concept complet, 47 sur un concept à 3 attributs, 181 sur un concept à 2 attributs, 425 sur un concept à 1 attribut et 108 sur un concept qui n'a que son prefLabel.

Ce mélange reflète la base elle-même, qui contient à la fois des concepts complets et des concepts incomplets. Tous les concepts sont gardés : supprimer les concepts incomplets supprimerait aussi automatiquement leurs relations dans le graphe de connaissances.

Pour chaque méthode, les Hit@K sont calculés sur l'ensemble des requêtes, puis pour chaque niveau de richesse, afin de mesurer les différences. 

#### 11.1.1 Sans reranker (vecteurs seuls)

Cette partie présente la recherche par vecteurs seule : la question est transformée en vecteur par bge-m3, puis Qdrant renvoie les 10 concepts les plus proches.

**1. Résultats de la base vectorielle des concepts**

Le tableau suivant présente les résultats globaux de la base vectorielle des concepts, sur l'ensemble des requêtes : Hit@1, Hit@5, Hit@10, MRR@10, rang médian et part de non trouvés.

![1_resultats.png](RAG%20hybride/1_resultats.png)

Le bon concept est 1er pour 32 % des requêtes, dans les 5 premiers pour 61 % et dans les 10 premiers pour 70 %. Le rang médian est 2 : quand il est trouvé, il est le plus souvent 1er ou 2e. Le tableau montre aussi que, pour 29,8 % des requêtes, le bon concept est absent du top 10 : d'autres concepts ont obtenu un score de similarité plus élevé. 

**2. Courbe Hit@K**

La figure suivante présente la courbe Hit@K : la part des requêtes dont le bon concept est trouvé dans les K premiers résultats. 

![2_courbe_hitk.png](RAG%20hybride/2_courbe_hitk.png)

La courbe monte vite de K = 1 à 3 (de 0,32 à 0,54), puis lentement. Après le rang 5, chaque rang ajoute moins de 3 % : regarder plus de 10 résultats apporterait peu.

**3. Distribution des rangs : scores**

Le tableau suivant montre la distribution des rangs avec les scores de similarité entre la requête et le bon concept. Pour chaque rang, il donne l'effectif, les scores minimum, maximum et médian, la part des requêtes et le cumul (Hit@K).

![3_distribution_tableau.png](RAG%20hybride/3_distribution_tableau.png)

Le score du bon concept varie peu selon son rang, avec une médiane de 0,73 au rang 1 et de 0,67 au rang 10. Le rang 1 regroupe le plus grand effectif : 791 requêtes, avec des scores compris entre 0,540 et 0,850. Le tableau montre aussi 735 requêtes non trouvées : pour elles, le bon concept n'est pas dans les 10 premiers résultats.

**4. Distribution des rangs**

La figure suivante présente le nombre de requêtes pour chaque rang du bon concept, de 1 à 10, ainsi que les requêtes non trouvées.

![4_distribution_barres.png](RAG%20hybride/4_distribution_barres.png)

Deux groupes dominent : les requêtes trouvées tout de suite (791 au rang 1) et les requêtes non trouvées (735, soit 29,8 %). Entre les deux, les rangs 2 à 10 diminuent rapidement.

**5. Résultats selon la richesse**

Le tableau suivant montre les valeurs des Hit@K et du MRR@10 pour chaque niveau de richesse. 

![5_richesse_tableau.png](RAG%20hybride/5_richesse_tableau.png)

Les meilleurs résultats sont obtenus pour la richesse 4 (concept complet, 1 708 requêtes) : 38,8 % en Hit@1, 74,6 % en Hit@5, 84,2 % en Hit@10, un MRR@10 de 0,54 et seulement 15,8 % de non trouvés, contre 29,8 % sur l'ensemble des requêtes. Les valeurs les plus faibles concernent les concepts réduits à leur prefLabel (108 requêtes). C'est attendu : ces requêtes contiennent peu d'informations pour calculer la similarité. On en conclut que plus le concept est riche, mieux il est trouvé.

**6. Richesse : barres**

La figure suivante présente, pour chaque niveau de richesse, trois barres : Hit@1, Hit@5 et Hit@10.

![6_richesse_barres.png](RAG%20hybride/6_richesse_barres.png)

Le grand saut se fait entre 3 et 4 attributs. Les concepts complets (1 708 requêtes sur 2 469) portent l'essentiel du résultat global.

---

#### 11.1.2 Avec reranker

Même évaluation, avec une seconde étape : le reranker relit la question avec chacun des 30 premiers candidats de Qdrant, puis les reclasse. Les 2 469 requêtes sont les mêmes qu'en 11.1.1, ce qui permet la comparaison.

**1. Résultats de la base vectorielle des concepts**

Le tableau suivant présente les résultats globaux de la base vectorielle des concepts, sur l'ensemble des requêtes : Hit@1, Hit@5, Hit@10, MRR@10, rang médian et part de non trouvés.

![1_resultats.png](RAG%20hybride/1_resultats%201.png)

Le bon concept est 1er pour 45 % des requêtes (contre 32 % sans reranker), dans les 5 premiers pour 68 % et dans les 10 premiers pour 73 %. Le rang médian passe à 1. Le tableau montre aussi que, pour 27,1 % des requêtes, le bon concept est absent du top 10, contre 29,8 % sans reranker.

**2. Courbe Hit@K**

La figure suivante présente la courbe Hit@K : la part des requêtes dont le bon concept est trouvé dans les K premiers résultats. 

![2_courbe_hitk.png](RAG%20hybride/2_courbe_hitk%201.png)

La courbe part plus haut (0,45) mais monte moins. Le Hit@10 ne gagne que 3 points (de 0,70 à 0,73) : le reranker relit seulement les 30 candidats trouvés par Qdrant, il ne peut donc pas rattraper un concept que Qdrant n'a pas trouvé.

**3. Distribution des rangs : scores**

Le tableau suivant montre la distribution des rangs avec les scores du reranker pour le bon concept. Pour chaque rang, il donne l'effectif, les scores minimum, maximum et médian, la part des requêtes et le cumul (Hit@K). Ces scores ne sont pas sur la même échelle que la similarité cosinus de la partie 11.1.1 : on compare donc leur évolution selon le rang, pas leurs valeurs.

![3_distribution_tableau.png](RAG%20hybride/3_distribution_tableau%201.png)

Contrairement à la similarité cosinus, le score du reranker varie fortement selon le rang : la médiane vaut 0,964 au rang 1, mais 0,465 au rang 4 et moins de 0,21 à partir du rang 6. Sans reranker, elle variait seulement de 0,73 à 0,67. Le rang 1 regroupe le plus grand effectif : 1 102 requêtes, contre 791 sans reranker, avec des scores compris entre 0,040 et 1,000. Les requêtes non trouvées passent de 735 à 668. 

**4. Distribution des rangs**

La figure suivante présente le nombre de requêtes pour chaque rang du bon concept, de 1 à 10, ainsi que les requêtes non trouvées.

![4_distribution_barres.png](RAG%20hybride/4_distribution_barres%201.png)

Le pic au rang 1 grandit (de 791 à 1 102 requêtes) et les rangs 2 à 10 diminuent : le reranker remonte les bons concepts en tête. Les non trouvés baissent peu (de 735 à 668).

**5. Résultats selon la richesse**

Le tableau suivant montre les valeurs des Hit@K et du MRR@10 pour chaque niveau de richesse. 

![5_richesse_tableau.png](RAG%20hybride/5_richesse_tableau%201.png)

Les meilleurs résultats sont toujours obtenus pour la richesse 4 (concept complet, 1 708 requêtes) : 56,5 % en Hit@1, 82,7 % en Hit@5, 86,9 % en Hit@10, un MRR@10 de 0,68 et 13,1 % de non trouvés. Sans reranker, ces valeurs étaient de 38,8 %, 74,6 %, 84,2 %, 0,54 et 15,8 %. Sur l'ensemble des requêtes, les non trouvés représentent 27,1 %. Les valeurs les plus faibles concernent toujours les concepts réduits à leur prefLabel (108 requêtes), qui contiennent peu d'informations. On en conclut, ici aussi, que plus le concept est riche, mieux il est trouvé.

**6. Richesse : barres**

La figure suivante présente, pour chaque niveau de richesse, trois barres : Hit@1, Hit@5 et Hit@10.   

![6_richesse_barres.png](RAG%20hybride/6_richesse_barres%201.png)

L'écart se creuse : le Hit@1 atteint 0,56 pour un concept complet, contre 0,14 à 0,23 pour un concept avec 0 à 2 attributs.

---

#### 11.1.3 Comparaison : sans et avec reranker

Cette partie compare les deux méthodes sur les mêmes 2 469 requêtes : la recherche par vecteurs seule (11.1.1) et la recherche avec reranker (11.1.2).

**1. Résultats de la base vectorielle des concepts**

Le tableau suivant compare les résultats globaux des deux méthodes.

| Métrique | Sans reranker | Avec reranker | Lecture |
| --- | --- | --- | --- |
| Hit@1 | 0,320 | 0,446 | **+12,6 points** : le principal gain |
| Hit@5 | 0,614 | 0,679 | +6,5 points |
| Hit@10 | 0,702 | 0,729 | +2,7 points : le reranker reclasse, il trouve peu de nouveaux concepts |
| MRR@10 | 0,446 | 0,545 | +0,10 : les bons concepts sont mieux placés |
| Rang médian | 2 | 1 | le bon concept trouvé est le plus souvent 1er |
| Non trouvé | 29,8 % | 27,1 % | −2,7 points |

**2. Courbe Hit@K**

La figure suivante place côte à côte les courbes Hit@K sans reranker (à gauche) et avec reranker (à droite).

**Sans reranker**

![comparaison_sans_2_courbe_hitk.png](RAG%20hybride/comparaison_sans_2_courbe_hitk.png)

**Avec reranker**

![comparaison_avec_2_courbe_hitk.png](RAG%20hybride/comparaison_avec_2_courbe_hitk.png)

Les deux courbes se rapprochent quand K augmente : le reranker améliore surtout le haut du classement (K = 1 à 3).

**3. Distribution des rangs : scores**

Les scores ne sont pas comparables : sans reranker, c'est la similarité cosinus ; avec reranker, c'est le score du reranker, sur une autre échelle. On compare donc seulement les rangs.

| Rang | Sans reranker : requêtes | Sans : part cumulée | Avec reranker : requêtes | Avec : part cumulée |
| --- | --- | --- | --- | --- |
| 1 | 791 | 0,320 | 1 102 | 0,446 |
| 2 à 5 | 724 | 0,614 | 574 | 0,679 |
| 6 à 10 | 219 | 0,702 | 125 | 0,729 |
| Non trouvé | 735 | 1,000 | 668 | 1,000 |

Le reranker concentre les bons résultats en tête : 1 102 requêtes au rang 1 contre 791, et un cumul de 0,679 au rang 5 contre 0,614. Les rangs 6 à 10 passent de 219 à 125 requêtes.

**4. Distribution des rangs**

La figure suivante place côte à côte la distribution des rangs sans reranker (à gauche) et avec reranker (à droite).

**Sans reranker**

![comparaison_sans_4_distribution_barres.png](RAG%20hybride/comparaison_sans_4_distribution_barres.png)

**Avec reranker**

![comparaison_avec_4_distribution_barres.png](RAG%20hybride/comparaison_avec_4_distribution_barres.png)

En solde, le rang 1 gagne 311 requêtes (de 791 à 1 102), tandis que les rangs 2 à 10 en perdent 244 et les non trouvés 67.

**5. Résultats selon la richesse**

Le tableau suivant compare, pour chaque niveau de richesse, les Hit@1, Hit@5, Hit@10 et MRR@10 sans reranker (S) et avec reranker (A).

| Richesse | N | Hit@1 S | Hit@1 A | Hit@5 S | Hit@5 A | Hit@10 S | Hit@10 A | MRR@10 S | MRR@10 A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (prefLabel seul) | 108 | 0,185 | 0,176 | 0,306 | 0,315 | 0,352 | 0,389 | 0,240 | 0,237 |
| 1 attribut | 425 | 0,129 | 0,141 | 0,278 | 0,304 | 0,353 | 0,372 | 0,195 | 0,209 |
| 2 attributs | 181 | 0,232 | 0,232 | 0,381 | 0,403 | 0,436 | 0,481 | 0,293 | 0,309 |
| 3 attributs | 47 | 0,234 | 0,340 | 0,447 | 0,596 | 0,617 | 0,638 | 0,353 | 0,437 |
| 4 (concept complet) | 1 708 | 0,388 | 0,565 | 0,746 | 0,827 | 0,842 | 0,869 | 0,540 | 0,676 |

Le gain en Hit@1 augmente avec la richesse : il est presque nul pour les concepts à 0, 1 ou 2 attributs (entre −0,9 et +1,2 point), puis atteint +10,6 points pour 3 attributs et +17,7 points pour un concept complet. Le MRR@10 suit la même tendance (+0,14 pour un concept complet). Pour le Hit@10, les écarts restent faibles à tous les niveaux (au plus +4,5 points) : le reranker améliore surtout l'ordre des résultats, pas le nombre de concepts trouvés dans le top 10.

**6. Richesse : barres**

La figure suivante place côte à côte les résultats par richesse sans reranker (à gauche) et avec reranker (à droite).

**Sans reranker**

![comparaison_sans_6_richesse_barres.png](RAG%20hybride/comparaison_sans_6_richesse_barres.png)

**Avec reranker**

![comparaison_avec_6_richesse_barres.png](RAG%20hybride/comparaison_avec_6_richesse_barres.png)

La différence se voit surtout à droite des figures : pour les concepts complets, la barre Hit@1 monte nettement avec le reranker (de 0,39 à 0,57), alors que les barres Hit@5 et Hit@10 changent moins. Pour les concepts pauvres (0 à 2 attributs), les barres restent presque identiques.

**À retenir** : le reranker sert surtout à mettre le bon concept en 1re position (+12,6 points en Hit@1), et ses scores indiquent la fiabilité du résultat.

#### 11.1.4 Concepts complets et concepts incomplets

Le jeu de test vient de deux sources, qui correspondent à deux types de concepts : le jeu initial (1 709 requêtes, dont 1 708 sur des concepts complets) et les nouvelles requêtes (760 requêtes, toutes sur des concepts incomplets, de 0 à 3 attributs). Le tableau suivant compare ces deux groupes, sans reranker (S) et avec reranker (A).

| Groupe | N | Hit@1 S | Hit@1 A | Hit@5 S | Hit@5 A | Hit@10 S | Hit@10 A | MRR@10 S | MRR@10 A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jeu initial (concepts complets) | 1 709 | 0,388 | 0,565 | 0,745 | 0,826 | 0,841 | 0,868 | 0,540 | 0,676 |
| Nouvelles requêtes (concepts incomplets) | 760 | 0,168 | 0,180 | 0,317 | 0,347 | 0,389 | 0,417 | 0,235 | 0,251 |

Les deux groupes donnent des résultats très différents. Pour les concepts complets, le reranker fait passer le Hit@1 de 0,388 à 0,565 (+17,7 points), et le bon concept est dans le top 10 pour 87 % des requêtes. Pour les concepts incomplets, le reranker ne gagne que +1,2 point en Hit@1 (de 0,168 à 0,180), et le bon concept reste absent du top 10 pour environ 58 % des requêtes. La qualité du résultat dépend donc d'abord de la richesse du concept dans Opentheso, bien plus que de la méthode de recherche.

### 11.2 Base vectorielle des thésaurus

Cette partie évalue le rattachement d'une requête au bon thésaurus, sur les mêmes 2 469 requêtes qu'en 11.1 et avec les mêmes mesures (Hit@K, MRR@10, rang médian et part de non trouvés). Comme expliqué en 10.3, le concept recherché est retiré des résultats avant le vote. Les thésaurus sont classés avec le score de la décision 13, où w est le poids donné au vote :

> **score final = (1 − w) × similarité + w × vote**
> 
- **w = 0** : score final = similarité (similarité seule) ;
- **w = 1** : score final = vote (vote seul) ;
- **w entre 0 et 1** : combinaison des deux méthodes.

Pour choisir w, 11 valeurs ont été testées, de 0 à 1 par pas de 0,1. Le tableau et la figure suivants donnent, pour chaque valeur, les Hit@1, Hit@3, Hit@5, Hit@10 et MRR@10.

| Poids du vote (w) | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 |
| --- | --- | --- | --- | --- | --- |
| 0 (similarité seule) | 0,433 | 0,607 | 0,691 | 0,808 | 0,545 |
| 0,1 | 0,554 | 0,721 | 0,785 | 0,865 | 0,652 |
| 0,2 | 0,590 | 0,741 | 0,812 | 0,886 | 0,683 |
| 0,3 | 0,602 | 0,747 | 0,829 | 0,904 | 0,695 |
| **0,4 (retenu)** | **0,605** | **0,750** | **0,832** | **0,912** | **0,699** |
| 0,5 | 0,595 | 0,741 | 0,827 | 0,911 | 0,691 |
| 0,6 | 0,590 | 0,736 | 0,821 | 0,912 | 0,686 |
| 0,7 | 0,586 | 0,729 | 0,811 | 0,910 | 0,683 |
| 0,8 | 0,583 | 0,726 | 0,806 | 0,903 | 0,679 |
| 0,9 | 0,583 | 0,723 | 0,800 | 0,894 | 0,675 |
| 1 (vote seul) | 0,384 | 0,654 | 0,766 | 0,860 | 0,536 |

![0_choix_poids.png](RAG%20hybride/0_choix_poids.png)

Le tableau et la figure montrent que w = 0,4 donne les meilleurs résultats : Hit@1 = 0,605, Hit@3 = 0,750, Hit@5 = 0,832, Hit@10 = 0,912 (à égalité avec w = 0,6) et MRR@10 = 0,699. Les deux extrêmes sont nettement moins bons : Hit@1 = 0,433 pour la similarité seule (w = 0) et 0,384 pour le vote seul (w = 1). Dès w = 0,1, le Hit@1 gagne 12 points (0,554) : un peu de vote suffit à corriger une bonne partie des erreurs de la similarité. Entre w = 0,2 et w = 0,9, les résultats varient peu (Hit@1 entre 0,583 et 0,605) : le choix exact de w a donc peu d'influence dans cette plage.

Pour comparer les méthodes en détail, les parties suivantes présentent trois cas : w = 0 (similarité seule), w = 1 (vote seul) et w = 0,4 (combinaison retenue). 

#### 11.2.1 Similarité seule (w = 0)

La requête est comparée directement au vecteur de chaque thésaurus, ou de chacune de ses branches pour un grand thésaurus (décision 8). Les concepts trouvés ne sont pas utilisés.

**1. Résultats globaux**

Le tableau suivant présente les résultats globaux sur l'ensemble des requêtes : Hit@1, Hit@5, Hit@10, MRR@10, rang médian et part de non trouvés.

![w0.0_1_resultats.png](RAG%20hybride/w0.0_1_resultats.png)

Le bon thésaurus est 1er pour 43,3 % des requêtes, dans les 5 premiers pour 69,1 % et dans les 10 premiers pour 80,8 %. Le MRR@10 vaut 0,545 et le rang médian est 1. Pour 19,2 % des requêtes, le bon thésaurus est absent du top 10.

**2. Courbe Hit@K**

La figure suivante présente la courbe Hit@K : la part des requêtes dont le bon thésaurus est dans les K premiers résultats. 

![w0.0_2_courbe_hitk.png](RAG%20hybride/w0.0_2_courbe_hitk.png)

La courbe passe de 0,433 à K = 1 à 0,691 à K = 5, puis à 0,808 à K = 10. Elle continue de monter après le rang 5 (environ 2,3 points par rang) : la similarité seule place souvent le bon thésaurus loin dans la liste.

**3. Distribution des rangs**

Le tableau et la figure suivants présentent le nombre de requêtes pour chaque rang du bon thésaurus, de 1 à 10, ainsi que les requêtes non trouvées. La colonne cumul correspond à la courbe Hit@K.  

![w0.0_3_distribution_tableau.png](RAG%20hybride/w0.0_3_distribution_tableau.png)

![w0.0_4_distribution_barres.png](RAG%20hybride/w0.0_4_distribution_barres.png)

Le rang 1 regroupe 1 069 requêtes (Hit@1 = 0,433). Les 5 premiers rangs en regroupent 1 707 (Hit@5 = 0,691) et les 10 premiers 1 996 (Hit@10 = 0,808). Les rangs 6 à 10 restent assez fournis (de 43 à 70 requêtes chacun) et 473 requêtes ne sont pas trouvées.

**4. Résultats selon la richesse**

Le tableau et la figure suivants présentent les Hit@K, le MRR@10 et la part de non trouvés pour chaque niveau de richesse du concept recherché (même découpage qu'en 11.1). 

![w0.0_5_richesse_tableau.png](RAG%20hybride/w0.0_5_richesse_tableau.png)

![w0.0_6_richesse_barres.png](RAG%20hybride/w0.0_6_richesse_barres.png)

Les concepts complets (1 708 requêtes) donnent les meilleurs résultats : Hit@1 = 0,452, Hit@5 = 0,707, Hit@10 = 0,823, MRR@10 = 0,562 et 17,7 % de non trouvés. Les concepts réduits à leur prefLabel (108 requêtes) donnent les valeurs les plus faibles : Hit@1 = 0,343 et 30,6 % de non trouvés. L'écart reste modéré (Hit@1 de 0,343 à 0,452) : la similarité compare la requête au thésaurus et non aux concepts, elle dépend donc peu de la richesse du concept recherché.

---

#### 11.2.2 Vote seul (w = 1)

Les 10 concepts les plus proches de la requête sont cherchés dans la base des concepts, puis chacun vote pour son thésaurus. Les thésaurus sont classés par leur part de votes, sans similarité directe.

**1. Résultats globaux**

Le tableau suivant présente les résultats globaux sur l'ensemble des requêtes. 

![w1.0_1_resultats.png](RAG%20hybride/w1.0_1_resultats.png)

Le bon thésaurus est 1er pour 38,4 % des requêtes, contre 43,3 % avec la similarité seule. En revanche, il est dans les 5 premiers pour 76,6 % des requêtes (contre 69,1 %) et dans les 10 premiers pour 86,0 % (contre 80,8 %). Le MRR@10 vaut 0,536 et le rang médian 2. Les non trouvés baissent de 19,2 % à 14,0 %. Le vote place donc moins souvent le bon thésaurus en tête, mais il le ramène plus souvent dans la liste.

**2. Courbe Hit@K**

La figure suivante présente la courbe Hit@K.

![w1.0_2_courbe_hitk.png](RAG%20hybride/w1.0_2_courbe_hitk.png)

La courbe part plus bas (0,384) mais monte plus vite : 0,766 à K = 5 et 0,860 à K = 10. Elle dépasse la courbe de la similarité seule à partir de K = 3 (0,654 contre 0,607).

**3. Distribution des rangs**

Le tableau et la figure suivants présentent le nombre de requêtes pour chaque rang du bon thésaurus, ainsi que les requêtes non trouvées. 

![w1.0_3_distribution_tableau.png](RAG%20hybride/w1.0_3_distribution_tableau.png)

![w1.0_4_distribution_barres.png](RAG%20hybride/w1.0_4_distribution_barres.png)

Le rang 1 regroupe 948 requêtes, contre 1 069 avec la similarité seule. Les 5 premiers rangs en regroupent 1 891 (contre 1 707) et les 10 premiers 2 123 (contre 1 996). Les non trouvés passent de 473 à 346, soit 127 de moins. Le rang 10 regroupe 90 requêtes, nettement plus que les rangs 6 à 9 (de 16 à 62).

**4. Résultats selon la richesse**

Le tableau et la figure suivants présentent les résultats pour chaque niveau de richesse. 

![w1.0_5_richesse_tableau.png](RAG%20hybride/w1.0_5_richesse_tableau.png)

![w1.0_6_richesse_barres.png](RAG%20hybride/w1.0_6_richesse_barres.png)

Les concepts complets (1 708 requêtes) donnent de très bons résultats : Hit@1 = 0,472, Hit@5 = 0,916, Hit@10 = 0,975, MRR@10 = 0,645 et seulement 2,5 % de non trouvés. Les résultats chutent fortement pour les concepts pauvres : pour un concept réduit à son prefLabel (108 requêtes), Hit@1 = 0,093 et 53,7 % de non trouvés. Contrairement à la similarité, le vote dépend directement de la richesse : il faut d'abord retrouver des concepts proches dans la base des concepts, ce qui marche mal quand la requête décrit un concept pauvre (voir 11.1).

---

#### 11.2.3 Combinaison retenue (w = 0,4)

Le score final combine les deux méthodes : 0,6 × similarité + 0,4 × vote (décision 13).

**1. Résultats globaux**

Le tableau suivant présente les résultats globaux sur l'ensemble des requêtes.  

![w0.4_1_resultats.png](RAG%20hybride/w0.4_1_resultats.png)

Le bon thésaurus est 1er pour 60,5 % des requêtes, contre 43,3 % avec la similarité seule et 38,4 % avec le vote seul. Il est dans les 5 premiers pour 83,2 % des requêtes (contre 69,1 % et 76,6 %) et dans les 10 premiers pour 91,2 % (contre 80,8 % et 86,0 %). Le MRR@10 atteint 0,699 et le rang médian est 1. Les non trouvés tombent à 8,8 %, contre 19,2 % et 14,0 %. La combinaison fait mieux que chaque méthode seule sur toutes les métriques.

**2. Courbe Hit@K**

La figure suivante présente la courbe Hit@K.

![w0.4_2_courbe_hitk.png](RAG%20hybride/w0.4_2_courbe_hitk.png)

La courbe part de 0,605 à K = 1, atteint 0,832 à K = 5 et 0,912 à K = 10. Elle reste au-dessus des courbes de la similarité seule et du vote seul pour toutes les valeurs de K.

**3. Distribution des rangs**

Le tableau et la figure suivants présentent le nombre de requêtes pour chaque rang du bon thésaurus, ainsi que les requêtes non trouvées.

![w0.4_3_distribution_tableau.png](RAG%20hybride/w0.4_3_distribution_tableau.png)

![w0.4_4_distribution_barres.png](RAG%20hybride/w0.4_4_distribution_barres.png)

Le rang 1 regroupe 1 494 requêtes, contre 1 069 avec la similarité seule et 948 avec le vote seul. Les 5 premiers rangs en regroupent 2 053 (contre 1 707 et 1 891) et les 10 premiers 2 251 (contre 1 996 et 2 123). Il reste 218 requêtes non trouvées, contre 473 et 346 : par rapport à la similarité seule, la combinaison en récupère 255, soit plus de la moitié.

**4. Résultats selon la richesse**

Le tableau et la figure suivants présentent les résultats pour chaque niveau de richesse. 

![w0.4_5_richesse_tableau.png](RAG%20hybride/w0.4_5_richesse_tableau.png)

![w0.4_6_richesse_barres.png](RAG%20hybride/w0.4_6_richesse_barres.png)

Les concepts complets (1 708 requêtes) obtiennent Hit@1 = 0,744, contre 0,452 avec la similarité seule et 0,472 avec le vote seul, soit environ +28 points. Ils atteignent aussi Hit@5 = 0,923, Hit@10 = 0,970, MRR@10 = 0,820 et 3,0 % de non trouvés. Pour les concepts incomplets (0 à 3 attributs), la combinaison fait mieux que le vote seul mais reste en dessous de la similarité seule en Hit@1 : par exemple 0,241 contre 0,343 pour un concept réduit à son prefLabel. Le gain global vient donc surtout des concepts complets, qui représentent 1 708 requêtes sur 2 469.

---

#### 11.2.4 Comparaison des trois méthodes

Le tableau suivant résume les résultats des trois méthodes sur les mêmes 2 469 requêtes.

| Métrique | Similarité seule (w = 0) | Vote seul (w = 1) | Combinaison (w = 0,4) |
| --- | --- | --- | --- |
| Hit@1 | 0,433 | 0,384 | **0,605** |
| Hit@3 | 0,607 | 0,654 | **0,750** |
| Hit@5 | 0,691 | 0,766 | **0,832** |
| Hit@10 | 0,808 | 0,860 | **0,912** |
| MRR@10 | 0,545 | 0,536 | **0,699** |
| Rang médian | 1 | 2 | 1 |
| Non trouvé | 19,2 % | 14,0 % | **8,8 %** |
| Hit@1, concepts complets (1 708) | 0,452 | 0,472 | **0,744** |
| Hit@1, prefLabel seul (108) | **0,343** | 0,093 | 0,241 |

**À retenir** : la combinaison w = 0,4 améliore toutes les métriques globales, avec +17,2 points de Hit@1 par rapport à la similarité seule. Ce gain vient surtout des concepts complets ; pour les concepts incomplets, la similarité seule reste la meilleure en Hit@1.

### 11.3 Graphe de connaissances

Cette partie ne mesure pas une qualité de recherche : elle vérifie que le graphe chargé dans Neo4j est complet et cohérent. Le graphe contient deux types de relations : `BROADER` entre deux concepts (le *narrower* s'en déduit en lisant le même lien dans l'autre sens, décision 2) et `APPARTIENT` entre un concept et son thésaurus. Le tableau suivant compare les nombres trouvés dans Neo4j aux nombres attendus d'après l'extraction de l'API. 

| Élément | Dans Neo4j | Attendu d'après l'extraction | Contrôle |
| --- | --- | --- | --- |
| Nœuds `Concept` | 407 761 | 407 761 | ✅ |
| Nœuds `Thesaurus` | 344 | 344 | ✅ |
| Relations `APPARTIENT` | 407 761 | 407 761 | ✅ |
| Relations `BROADER` | 343 865 | 343 865 | ✅ |
| Concepts sans thésaurus | 0 | 0 | ✅ |

Tous les contrôles sont validés : aucun nœud ni aucune relation n'a été perdu au chargement. Le graphe permet aussi les observations suivantes :

- **Broader et narrower symétriques** : dans l'API, chaque lien broader a un narrower correspondant. Ne stocker que `BROADER` ne fait donc perdre aucune relation (décision 2).
- **84 596 concepts sans générique** (407 761 − 323 165) : ce sont les concepts de tête et les concepts des listes sans hiérarchie.
- **Thésaurus sans hiérarchie** : th1065 et th1187 (12 038 concepts au total) n'ont aucun lien, et Liste d'autorités Auteurs - Joconde (th69 : 38 987 concepts) n'en a que 349. Pour ces thésaurus, le graphe n'apporte presque rien : seule la base vectorielle est utile.
- **Polyhiérarchie** : un concept peut avoir plusieurs génériques. C'est pourquoi le graphe contient 343 865 liens `BROADER` pour 323 165 concepts qui ont un générique, soit 20 700 liens de plus. Certains thésaurus ont même plus de liens que de concepts (Initiale - Sujets : 26 468 liens pour 19 202 concepts).

La figure suivante montre un extrait du graphe de connaissances dans Neo4j :

![visualisation (1).png](RAG%20hybride/visualisation_(1).png)

Dans cette figure, les nœuds `Concept` sont en vert et les nœuds `Thesaurus` en rouge. Chaque nœud est affiché avec son identifiant : `id_theso` pour un thésaurus (par ex. `th943`) et `id_concept`, de la forme `idTheso/id`, pour un concept (par ex. `th943/1006`). Les flèches `BROADER` relient un concept à son générique ; lues dans le sens inverse, elles donnent ses *narrower* (décision 2). Les flèches `APPARTIENT` relient chaque concept à son thésaurus.

## 12. Résultats globaux du RAG hybride

Les parties 11.1 à 11.3 ont évalué séparément les deux bases vectorielles et le graphe de connaissances. Cette partie évalue la sortie complète du RAG hybride : la génération d'un concept et son rattachement au thésaurus. Pour cela, un contexte est construit à partir de la requête de l'utilisateur : on récupère les concepts ou les thésaurus les plus proches de la requête, ainsi que leurs relations `BROADER` et `APPARTIENT` dans le graphe de connaissances, puis on les insère dans le prompt du LLM (voir l'architecture en section 2). 

### 12.1 Construction du contexte

Le contexte suit le format de la **brique 4**, décrit dans la page « Construction du corpus : patterns de prompt à briques » : RÔLE + EXEMPLES + CADRE + MÉTHODE, avec la DEMANDE toujours présente. Ce format a été retenu parce que l'étude menée dans l'approche fine-tuning a montré que c'est celui que le LLM comprend le mieux. Le contexte est composé ainsi :

- **RÔLE** : Tu es documentaliste spécialisé en terminologie du patrimoine culturel.
- **EXEMPLES** : les exemples **les plus proches** du terme demandé, récupérés dans la base vectorielle des concepts ou dans celle des thésaurus selon la tâche, et complétés par les relations `BROADER` et `APPARTIENT` lues dans le graphe de connaissances ;
- **CADRE** : Dans le cadre de la construction d'un thésaurus SKOS pour une institution patrimoniale,
- **DEMANDE** : quel est le concept SKOS complet associé au terme « {terme} » ?
- **MÉTHODE** : Procède champ par champ : d'abord la forme retenue, puis les synonymes, puis la définition, puis le générique, puis les spécifiques.

Exemple de contexte au format brique 4 pour le terme « amphore » :

**Contexte (entrée du LLM)** :

```
Tu es documentaliste spécialisé en terminologie du patrimoine culturel.

Exemple 1.
Terme : « canthare »
prefLabel: canthare
altLabel: kantharos
definition: Vase à boire grec à deux grandes anses verticales.
broader: vase à boire
narrower: canthare à anses hautes
### FIN

Dans le cadre de la construction d'un thésaurus SKOS pour une institution patrimoniale, quel est le concept SKOS complet associé au terme « amphore » ? Procède champ par champ : d'abord la forme retenue, puis les synonymes, puis la définition, puis le générique, puis les spécifiques.
```

**Réponse attendue** :

```
prefLabel: amphore
altLabel: amphora ; amphores
definition: Vase à deux anses et à fond pointu, utilisé pour le transport et le stockage des liquides, notamment le vin et l'huile.
broader: récipient de transport
narrower: amphore vinaire ; amphore à huile ; amphore de Narbonnaise
### FIN
```

Ce contexte est donné en entrée à un LLM de base, non fine-tuné. Trois modèles ont été testés : 

1. Llama-3.1-8B (Meta)
2. Mistral-7B (Mistral AI)
3. Qwen2.5-7B (Alibaba)

> **Pourquoi pas les modèles fine-tunés ?** Cette partie évalue l'approche RAG hybride seule. La combinaison du RAG hybride avec les modèles fine-tunés dans l'approche fine-tuning fera l'objet de l'étape suivante.
> 

### 12.2 Évaluation de la sortie du RAG hybride

La sortie du RAG hybride est évaluée avec les mêmes méthodes que dans l'approche fine-tuning :

- **génération de concepts** : similarité cosinus (bge-m3) entre chaque attribut généré et l'attribut de référence, puis précision, rappel et F1 pour les champs à valeurs multiples (altLabel, broader, narrower), en version *crisp* (correspondance exacte) et en version *soft* (correspondance par similarité) ;
- **rattachement au thésaurus** : similarité cosinus entre le thésaurus proposé et le thésaurus attendu.

Par défaut, le contexte contient un seul exemple. Or l'évaluation des bases vectorielles (section 11) a montré que le bon concept n'est pas toujours en 1re position, mais qu'il se trouve beaucoup plus souvent dans les 5 premiers résultats (Hit@5 nettement supérieur au Hit@1). Deux configurations sont donc testées : un contexte avec **1 exemple** et un contexte avec **5 exemples**. Le jeu de test contient 268 concepts pour la génération et 5 731 requêtes pour le rattachement.

#### 12.2.1 Génération de concepts

Pour chaque modèle, trois tableaux sont présentés :

1. **Similarité** : similarité cosinus moyenne entre l'attribut généré et l'attribut de référence ; `n` est le nombre de concepts évalués et `exact` la part des attributs strictement identiques à la référence ;
2. **Crisp** : précision (P), rappel (R) et F1 calculés avec une correspondance exacte des valeurs ;
3. **Soft** : précision, rappel et F calculés avec une correspondance par similarité, qui accepte une valeur proche mais pas identique.
**a. Contexte avec 1 exemple**
**a.1 Llama-3.1-8B**
Le tableau suivant présente la similarité entre les attributs générés par Llama et les attributs de référence.

![h1_llama_sim.svg](RAG%20hybride/h1_llama_sim.svg)

Le tableau suivant présente les scores crisp (correspondance exacte).

![h1_llama_crisp.svg](RAG%20hybride/h1_llama_crisp.svg)

Le tableau suivant présente les scores soft (correspondance par similarité).

![h1_llama_soft.svg](RAG%20hybride/h1_llama_soft.svg)

La similarité moyenne vaut 0,579, avec des attributs entre 0,533 (narrower) et 0,596 (altLabel et broader). Les valeurs exactes sont presque absentes, sauf pour le broader (16,0 %). Le F1 crisp reste très faible (0,045 pour altLabel, 0,047 pour narrower), alors que le soft F se situe entre 0,48 et 0,56 : Llama génère des valeurs proches de la référence par le sens, mais rarement identiques.
**a.2 Mistral-7B**
Le tableau suivant présente la similarité entre les attributs générés par Mistral et les attributs de référence.

![h1_mistral_sim.svg](RAG%20hybride/h1_mistral_sim.svg)

Le tableau suivant présente les scores crisp.

![h1_mistral_crisp.svg](RAG%20hybride/h1_mistral_crisp.svg)

Le tableau suivant présente les scores soft.

![h1_mistral_soft.svg](RAG%20hybride/h1_mistral_soft.svg)

Mistral obtient la meilleure similarité moyenne des trois modèles (0,627), portée par altLabel (0,651) et definition (0,644). C'est aussi le meilleur sur les narrower : cosinus de 0,588 et soft F de 0,6146. En revanche, son broader exact est le plus bas (14,9 %, F1 crisp 0,149) : le générique proposé est proche du bon, mais moins souvent identique.
**a.3 Qwen2.5-7B**
Le tableau suivant présente la similarité entre les attributs générés par Qwen et les attributs de référence.

![h1_qwen_sim.svg](RAG%20hybride/h1_qwen_sim.svg)

Le tableau suivant présente les scores crisp.

![h1_qwen_crisp.svg](RAG%20hybride/h1_qwen_crisp.svg)

Le tableau suivant présente les scores soft.

![h1_qwen_soft.svg](RAG%20hybride/h1_qwen_soft.svg)

Qwen obtient les meilleures similarités sur definition (0,661) et broader (0,647), et le meilleur broader exact (17,5 %, F1 crisp 0,175). Mais il génère mal les spécifiques : cosinus narrower de 0,375 et soft F narrower de 0,365, nettement en dessous des deux autres modèles. Sa moyenne (0,578) est donc tirée vers le bas par ce champ.
**b. Contexte avec 5 exemples**
**b.1 Llama-3.1-8B**
Le tableau suivant présente la similarité entre les attributs générés par Llama et les attributs de référence, avec 5 exemples dans le contexte.

![h5_llama_sim.svg](RAG%20hybride/h5_llama_sim.svg)

Le tableau suivant présente les scores crisp.

![h5_llama_crisp.svg](RAG%20hybride/h5_llama_crisp.svg)

Le tableau suivant présente les scores soft.

![h5_llama_soft.svg](RAG%20hybride/h5_llama_soft.svg)

La similarité moyenne reste stable (0,576 contre 0,579 avec 1 exemple). Le gain se voit sur le broader : 20,9 % de broader exact au lieu de 16,0 %, et un F1 crisp qui passe de 0,164 à 0,209. Le soft F progresse aussi sur altLabel (de 0,556 à 0,585) et narrower (de 0,549 à 0,570).
**b.2 Mistral-7B**
Le tableau suivant présente la similarité entre les attributs générés par Mistral et les attributs de référence, avec 5 exemples dans le contexte.

![h5_mistral_sim.svg](RAG%20hybride/h5_mistral_sim.svg)

Le tableau suivant présente les scores crisp.

![h5_mistral_crisp.svg](RAG%20hybride/h5_mistral_crisp.svg)

Le tableau suivant présente les scores soft.

![h5_mistral_soft.svg](RAG%20hybride/h5_mistral_soft.svg)

Mistral garde la meilleure similarité moyenne (0,630) et devient le meilleur sur les quatre attributs. Son broader exact passe de 14,9 % à 21,6 % (F1 crisp de 0,149 à 0,216), et le soft F progresse sur broader (de 0,495 à 0,521) et narrower (de 0,615 à 0,636).
**b.3 Qwen2.5-7B**
Le tableau suivant présente la similarité entre les attributs générés par Qwen et les attributs de référence, avec 5 exemples dans le contexte.

![h5_qwen_sim.svg](RAG%20hybride/h5_qwen_sim.svg)

Le tableau suivant présente les scores crisp.

![h5_qwen_crisp.svg](RAG%20hybride/h5_qwen_crisp.svg)

Le tableau suivant présente les scores soft.

![h5_qwen_soft.svg](RAG%20hybride/h5_qwen_soft.svg)

Qwen obtient le meilleur broader exact des deux configurations (23,1 %, F1 crisp 0,246) et le meilleur soft F sur altLabel (0,601). Sa similarité moyenne baisse légèrement (0,569 contre 0,578), surtout sur definition (de 0,661 à 0,616). Les narrower s'améliorent (cosinus de 0,375 à 0,424, soft F de 0,365 à 0,451) mais restent le point faible du modèle.

> **1 exemple ou 5 exemples ?** La similarité moyenne change peu, mais les trois modèles trouvent plus souvent le broader exact avec 5 exemples (+5 à +7 points) : des exemples plus nombreux donnent au modèle davantage de génériques corrects à reprendre.
> 

#### 12.2.2 Rattachement des concepts au thésaurus

Pour chaque requête, le modèle propose un thésaurus. On mesure la similarité cosinus (bge-m3) entre le thésaurus proposé et le thésaurus attendu, sur 5 731 requêtes. Pour chaque modèle, deux tableaux sont présentés :

1. **Similarité** : similarité moyenne, médiane, part de réponses vides et répartition des requêtes par tranche de similarité ;
2. **Selon la richesse** : similarité moyenne selon le nombre d'attributs remplis en plus du prefLabel (`N` est le nombre de requêtes de chaque niveau).
**a. Contexte avec 1 exemple**
**a.1 Llama-3.1-8B**
Le tableau suivant présente la similarité entre le thésaurus proposé par Llama et le thésaurus attendu.

![q1_llama_sim.svg](RAG%20hybride/q1_llama_sim.svg)

Le tableau suivant présente cette similarité selon la richesse du concept.

![q1_llama_rich.svg](RAG%20hybride/q1_llama_rich.svg)

La similarité moyenne vaut 0,600 et la médiane 0,597. Seules 4,6 % des requêtes obtiennent un thésaurus quasi identique au thésaurus attendu (similarité ≥ 0,95), alors que 64,6 % restent sous 0,70. La similarité augmente avec la richesse du concept : de 0,578 pour un concept réduit à son prefLabel à 0,677 pour un concept complet.
**a.2 Mistral-7B**
Le tableau suivant présente la similarité entre le thésaurus proposé par Mistral et le thésaurus attendu.

![q1_mistral_sim.svg](RAG%20hybride/q1_mistral_sim.svg)

Le tableau suivant présente cette similarité selon la richesse du concept.

![q1_mistral_rich.svg](RAG%20hybride/q1_mistral_rich.svg)

Mistral obtient les résultats les plus faibles avec 1 exemple : similarité moyenne de 0,576, médiane de 0,565, seulement 3,3 % de requêtes au-dessus de 0,95 et 69,3 % sous 0,70. La similarité progresse avec la richesse (de 0,531 à 0,606), mais reste en dessous des deux autres modèles à tous les niveaux.
**a.3 Qwen2.5-7B**
Le tableau suivant présente la similarité entre le thésaurus proposé par Qwen et le thésaurus attendu.

![q1_qwen_sim.svg](RAG%20hybride/q1_qwen_sim.svg)

Le tableau suivant présente cette similarité selon la richesse du concept.

![q1_qwen_rich.svg](RAG%20hybride/q1_qwen_rich.svg)

Qwen est nettement le meilleur : similarité moyenne de 0,699 et médiane de 0,761. 29,1 % des requêtes obtiennent un thésaurus quasi identique (≥ 0,95), contre moins de 5 % pour Llama et Mistral, et la part sous 0,70 tombe à 44,7 %. Même pour un concept réduit à son prefLabel, Qwen atteint 0,669, presque le niveau de Llama sur les concepts complets (0,677).
**b. Contexte avec 5 exemples**
**b.1 Llama-3.1-8B**
Le tableau suivant présente la similarité entre le thésaurus proposé par Llama et le thésaurus attendu, avec 5 exemples dans le contexte.

![q5_llama_sim.svg](RAG%20hybride/q5_llama_sim.svg)

Le tableau suivant présente cette similarité selon la richesse du concept.

![q5_llama_rich.svg](RAG%20hybride/q5_llama_rich.svg)

La similarité moyenne passe de 0,600 à 0,654 et la médiane de 0,597 à 0,678. La part de thésaurus quasi identiques double (de 4,6 % à 9,2 %) et la part sous 0,70 baisse de 64,6 % à 53,2 %. Le gain se retrouve à tous les niveaux de richesse (de 0,635 à 0,711).
**b.2 Mistral-7B**
Le tableau suivant présente la similarité entre le thésaurus proposé par Mistral et le thésaurus attendu, avec 5 exemples dans le contexte.

![q5_mistral_sim.svg](RAG%20hybride/q5_mistral_sim.svg)

Le tableau suivant présente cette similarité selon la richesse du concept.

![q5_mistral_rich.svg](RAG%20hybride/q5_mistral_rich.svg)

Mistral profite le plus des 5 exemples : la similarité moyenne passe de 0,576 à 0,645 (+0,069), et la part de thésaurus quasi identiques de 3,3 % à 18,7 %. La part sous 0,70 baisse de 69,3 % à 55,0 %. Selon la richesse, la similarité va de 0,636 à 0,704.
**b.3 Qwen2.5-7B**
Le tableau suivant présente la similarité entre le thésaurus proposé par Qwen et le thésaurus attendu, avec 5 exemples dans le contexte.

![q5_qwen_sim.svg](RAG%20hybride/q5_qwen_sim.svg)

Le tableau suivant présente cette similarité selon la richesse du concept.

![q5_qwen_rich.svg](RAG%20hybride/q5_qwen_rich.svg)

Qwen reste le meilleur : similarité moyenne de 0,732, médiane de 0,796, 32,2 % de thésaurus quasi identiques et seulement 40,2 % de requêtes sous 0,70. C'est la seule configuration où un niveau de richesse dépasse 0,80 (0,807 pour les concepts complets).

> **1 exemple ou 5 exemples ?** Les trois modèles s'améliorent avec 5 exemples : +0,054 pour Llama, +0,069 pour Mistral et +0,033 pour Qwen en similarité moyenne. Plus d'exemples donnent au modèle davantage de thésaurus candidats dans le contexte. La similarité augmente globalement avec la richesse, sans être strictement croissante : le niveau 2 est souvent un peu en dessous du niveau 1.
> 

#### 12.2.3 Comparaison des modèles

**a. Génération de concepts**

Les deux tableaux suivants comparent les trois modèles sur les métriques de génération de concepts, avec 1 exemple puis avec 5 exemples. Dans chaque ligne, la meilleure valeur est surlignée en jaune, et la dernière ligne compte le nombre de métriques gagnées par chaque modèle.

![comparaison_generation_1_exemple.svg](RAG%20hybride/comparaison_generation_1_exemple.svg)

Avec 1 exemple, Mistral gagne 6 métriques sur 12, Qwen 5 et Llama 1. Mistral domine la similarité moyenne (0,627) et le soft F des trois champs. Qwen obtient les meilleurs scores exacts sur le broader et les meilleures similarités sur definition et broader. Llama ne gagne que le F1 crisp narrower, avec des valeurs très faibles pour les trois modèles (moins de 0,05).

![comparaison_generation_5_exemples.svg](RAG%20hybride/comparaison_generation_5_exemples.svg)

Avec 5 exemples, le décompte reste le même (Mistral 6, Qwen 5, Llama 1), mais la répartition change : Mistral gagne désormais les cinq similarités cosinus, tandis que Qwen prend la tête du soft F sur altLabel et broader, en plus des métriques exactes du broader.

> **À retenir** : Mistral-7B est le modèle le plus régulier, avec la meilleure similarité moyenne dans les deux configurations (0,627 puis 0,630) et les meilleurs narrower. Qwen2.5-7B est le plus précis sur le générique exact, mais génère mal les spécifiques. Ce résultat rejoint celui de l'approche fine-tuning, où Mistral-7B avait déjà été retenu.
> 

**b. Rattachement au thésaurus**

Les deux tableaux suivants comparent les trois modèles sur le rattachement, avec 1 exemple puis avec 5 exemples. La meilleure valeur de chaque ligne est surlignée en jaune ; pour la ligne « Part < 0.70 », c'est la valeur la plus basse qui est la meilleure.

![comparaison_rattachement_1_exemple.svg](RAG%20hybride/comparaison_rattachement_1_exemple.svg)

Avec 1 exemple, Qwen gagne les 10 métriques. L'écart est important sur la part de thésaurus quasi identiques (29,1 % contre 4,6 % pour Llama et 3,3 % pour Mistral) et sur la médiane (0,761 contre 0,597 et 0,565).

![comparaison_rattachement_5_exemples.svg](RAG%20hybride/comparaison_rattachement_5_exemples.svg)

Avec 5 exemples, Qwen gagne encore les 10 métriques (similarité moyenne de 0,732). Mistral se rapproche de Llama (0,645 contre 0,654) et le dépasse nettement sur les thésaurus quasi identiques (18,7 % contre 9,2 %), mais reste loin derrière Qwen.

> **À retenir** : le meilleur modèle dépend de la tâche. Pour la **génération de concepts**, Mistral-7B est le plus régulier ; pour le **rattachement au thésaurus**, Qwen2.5-7B est nettement en tête dans les deux configurations. Le contexte avec **5 exemples** améliore nettement le rattachement pour les trois modèles ; en génération, il améliore surtout le broader exact, sans changer la similarité moyenne.
> 

## 13. Conclusion

Cette page a présenté l'approche RAG hybride pour la génération de concepts et leur rattachement au thésaurus. Elle combine deux bases vectorielles (concepts et thésaurus, dans Qdrant) et un graphe de connaissances (Neo4j), construits à partir de l'API Opentheso : 407 761 concepts et 344 thésaurus.

**Ce qu'il faut retenir**

- **Une architecture simple à maintenir** : chaque information n'est stockée qu'une fois (les attributs dans les bases vectorielles, les relations dans le graphe), et l'empreinte (hash) permet de mettre à jour les bases et le graphe rapidement, sans tout ré-encoder.
- **Une recherche efficace sur les concepts riches** : avec le reranker, le bon concept est en 1re position pour 45 % des requêtes (56,5 % pour les concepts complets), et la combinaison similarité + vote place le bon thésaurus en 1re position pour 60,5 % des requêtes.
- **Un graphe complet et cohérent** : tous les nœuds et toutes les relations attendus sont présents dans Neo4j.
- **Une qualité qui dépend d'abord des données** : seuls 0,9 % des concepts d'Opentheso sont complets, et les concepts pauvres sont nettement moins bien retrouvés.
- **Les résultats du RAG hybride** : avec un LLM de base, la génération de concepts reste difficile (similarité moyenne entre 0,57 et 0,63, valeurs exactes rares), alors que le rattachement donne de meilleurs résultats. Mistral-7B est le plus régulier en génération, Qwen2.5-7B le meilleur en rattachement, et un contexte avec 5 exemples améliore surtout le rattachement et le broader exact.

**Limites**

- Le rattachement est évalué par la similarité entre le thésaurus proposé et le thésaurus attendu : un thésaurus au nom proche mais différent peut obtenir un score élevé. Un taux de bonnes réponses exactes (même identifiant de thésaurus) compléterait cette mesure.
- Les deux tâches n'utilisent pas le même jeu de test (268 concepts pour la génération, 5 731 requêtes pour le rattachement) : les comparaisons entre tâches restent donc indicatives.
- Pour la génération, il faut vérifier que le concept testé (ou l'une de ses copies) n'est pas récupéré comme exemple dans le contexte, comme c'est fait pour le rattachement (section 10.3).

**Prochaine étape**

Combiner le RAG hybride avec les modèles fine-tunés de l'approche fine-tuning, puis comparer les trois configurations (fine-tuning seul, RAG hybride seul, RAG hybride + fine-tuning) sur les mêmes jeux de test. Les benchmarks construits dans cette approche et dans l'approche fine-tuning serviront à choisir l'approche qui donne les meilleurs résultats.