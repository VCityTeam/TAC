# Soft Precision and Recall : méthodologie détaillée

**Fränti, P., Mariescu-Istodor, R. (2023). « Soft precision and recall ». *Pattern Recognition Letters*, 167, p. 115-121. doi:10.1016/j.patrec.2023.02.005** (accès ouvert, licence CC BY)

---

## 1. Introduction : le problème

Précision et rappel sont des mesures classiques en apprentissage automatique. Elles reposent sur une **correspondance exacte** : un élément prédit est soit un vrai positif, soit un faux positif, alors qu'une correspondance inexacte est souvent préférable en reconnaissance de formes (résumé de l'article).

![Le problème posé par l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/01_probleme.png)

Elles donnent un score dans [0, 1] pour un ensemble prédit `P` par rapport à une référence `G` :

```
Précision = |G ∩ P| / |P|                        (1)
Rappel    = |G ∩ P| / |G|                        (2)
F-score   = 2·|G ∩ P| / (|G| + |P|)              (3)
```

![Fig. 1 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig01.png)

*Fig. 1 (article). Référence (G) et prédiction (P) : précision et rappel définis par les vrais positifs (TP), faux positifs (FP) et faux négatifs (FN). Les vrais négatifs (TN) sont généralement ignorés. `article_fig01.png`*

L'hypothèse principale est que prédictions et référence viennent du même ensemble fini d'éléments. Cette hypothèse n'est pas vérifiée dans beaucoup d'applications. Par exemple, la précision de la Fig. 2 n'est que de 2/5 = 40 % alors qu'un seul résultat n'est pas pertinent (plaza).

![Fig. 2 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig02.png)

*Fig. 2 (article). La prédiction (P) contient deux éléments corrects (café et pizza), une variante (coffee) et une faute de frappe (caffe). `article_fig02.png`*

Autre exemple : la détection d'activité vocale (segmentation audio). Chaque événement détecté de la Fig. 3 a un correspondant dans la référence : un appariement simple donnerait une précision et un rappel de 1,0 alors que la détection est loin d'être parfaite.

![Fig. 3 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig03.png)

*Fig. 3 (article). Appariement d'événements par recouvrement de segments. `article_fig03.png`*

Pour répondre à ces problèmes, l'article introduit la **soft precision** et le **soft recall**, fondés sur la cardinalité souple (*soft cardinality*) de Jimenez et al. Ils sont démontrés sur deux applications : l'extraction de mots-clés (similarités syntaxique et sémantique) et la recherche de trajectoires GPS.

---

## 2. Approches existantes (correspondance inexacte)

- **Ziolko [4]** : précision et rappel flous pour la segmentation audio. Il associe les segments de la référence à ceux de la prédiction, puis somme les similarités entre segments associés. Association dans un seul sens (de G vers P), trois valeurs : précision, rappel, F-score.
- **Similarity matching, Rezaei et al. [13]** : appariement glouton des paires les plus similaires jusqu'à épuisement d'un des ensembles, puis association des éléments restants à leur élément le plus similaire. Mesure symétrique, mais un seul score.
- **Sawade et al. [15]** : estimation active du F-score, en tirant de nouvelles instances de test.

L'article suit Ziolko et Rezaei et al. : il utilise les similarités entre les deux ensembles. La décision binaire classique {0, 1} est généralisée en une similarité dans [0, 1]. Au lieu de calculer une similarité moyenne entre les ensembles, précision et rappel sont dérivés des similarités par paires, avec une définition ensembliste.

![Fig. 4 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig04.png)

*Fig. 4 (article). Référence (G) et prédiction (P) dans un espace de caractéristiques imaginaire. Les vrais positifs sont un compte souple de l'intersection souple. Aucun élément prédit (blanc) n'est identique à un élément de référence (vert), mais certains sont proches et doivent contribuer aux vrais positifs. G et P ne sont plus des sous-ensembles du même ensemble d'éléments. `article_fig04.png`*

---

## 3. Soft precision et soft recall

Les ensembles crisp ont des appartenances binaires, les ensembles flous des degrés d'appartenance dans [0, 1]. Aucune des deux définitions ne convient : chaque élément n'appartient qu'à un ensemble, mais les éléments peuvent être **inexacts et redondants**. Exemple de l'article : {cafe, café, cafeteria, coffee house, coffee shop} contient cinq mots uniques mais un contenu très redondant.

Pour la précision et le rappel, il faut donc définir le **compte** des éléments, c'est-à-dire la **cardinalité** de l'ensemble.

![Notation](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/02_notation.png)

*Image 2 : Notation. `02_notation.png`*

![Équations crisp vs soft](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/03_equations_crisp_vs_soft.png)

*Image 3 : Équations crisp vs soft. `03_equations_crisp_vs_soft.png`*

### 3.1 Cardinalité souple

Pour la segmentation (Fig. 3), la cardinalité est simplement la longueur du segment. Pour les mots-clés (Fig. 2), l'article adopte la cardinalité souple de Jimenez et al. Le compte souple d'un élément est l'inverse de la somme de ses similarités avec tous les éléments de l'ensemble :

```
count(Aᵢ) = 1 / Σ(j=1..K) Sim(Aᵢ, Aⱼ)            (4)
```

`Aᵢ` est un élément de l'ensemble et `K` la taille de l'ensemble. Un élément unique n'est similaire qu'à lui-même : son compte vaut 1,00. Des éléments en double ont chacun un compte de 0,50. Tous les éléments similaires réduisent le compte en conséquence.

![Comportement du soft count](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/04_comportement_count.png)

*Image 4 : Comportement du soft count (section 3.1). `04_comportement_count.png`*

La cardinalité de l'ensemble est la somme des comptes :

```
card(A) = Σ(i=1..K) count(Aᵢ)                    (5)
```

Une distance peut être convertie en similarité. Pour la distance d'édition de Levenshtein :

```
Sim(Aᵢ, Aⱼ) = 1 − edit(Aᵢ, Aⱼ) / max(|Aᵢ|, |Aⱼ|)  (6)
```

Dans l'exemple café avec Levenshtein (Fig. 5), les cardinalités crisp sont 3 (G) et 5 (P). Les mots cafe, coffee et caffe comptent beaucoup moins que leur compte crisp (3) : leurs comptes souples ne totalisent que 1,27, et la cardinalité souple de P n'est que de 2,45 au lieu de 5,00.

![Fig. 5 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig05.png)

*Fig. 5 (article). Cardinalités souples de l'exemple café avec la distance de Levenshtein. `article_fig05.png`*

### 3.2 Union et intersection

Pour la précision et le rappel, il faut aussi la cardinalité de l'intersection. En segmentation, c'est la longueur des segments qui se recouvrent. Dans les autres cas, l'intersection est obtenue **indirectement, via l'union** des deux ensembles.

Dans la variante soft, la cardinalité de l'union se calcule sur la **concaténation** des deux ensembles. Cela peut créer des doublons, mais la cardinalité souple les gère naturellement en divisant leur poids par deux.

```
card(G ∩ P) = card(G) + card(P) − card(G ∪ P)    (7)
```

![Fig. 6 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig06.png)

*Fig. 6 (article). Exemple de calcul de la cardinalité souple avec la similarité sémantique Word2Vec. `article_fig06.png`*

### 3.3 Précision et rappel

```
Soft Precision = card(G ∩ P) / card(P)
Soft Recall    = card(G ∩ P) / card(G)
Soft F-score   = 2 · card(G ∩ P) / (card(G) + card(P))
```

La différence avec les variantes crisp est la façon de définir les cardinalités. Les variantes soft ne peuvent plus être définies à partir des comptes TP, FP et FN.

![Tableau 1 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/05_tableau1_crisp_soft.png)

*Image 5 : Tableau 1 de l'article, variantes crisp et soft. `05_tableau1_crisp_soft.png`*

### 3.4 Similarité sémantique

Parfois, le sens des mots compte plus que leurs différences typographiques. L'article utilise aussi Word2Vec pour la similarité sémantique.

![Fig. 7 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig07.png)

*Fig. 7 (article). Exemple de calcul des cardinalités souples. `article_fig07.png`*

---

## 4. Calcul détaillé de l'exemple café

*Application des équations 4 à 7 de l'article à son exemple café. Les résultats sont identiques à la Fig. 5 et au Tableau 3 (colonne syntaxique).*

![Exemple café](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/06_exemple_cafe.png)

*Image 6 : Exemple café. `06_exemple_cafe.png`*

```
G = { cafe , pizza , hotel }                     |G| = 3
P = { cafe , coffee , caffe , pizza , plaza }    |P| = 5
```

### 4.1 Similarités (équation 6)

![Similarités de Levenshtein](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/07_similarites_levenshtein.png)

*Image 7 : Similarités de Levenshtein. `07_similarites_levenshtein.png`*

*Note : la légende de la Fig. 5 indique une distance de 2 entre café et coffee, mais les comptes publiés (0,40 pour cafe dans P) correspondent à une distance de 3 (Sim = 0,50), valeur utilisée ici.*

### 4.2 Cardinalité souple de G

![Matrice interne de G](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/08_matrice_G.png)

*Image 8 : Matrice interne de G. `08_matrice_G.png`*

```
count(cafe)  = 1 / 1,20 = 0,833
count(pizza) = 1 / 1,00 = 1,000
count(hotel) = 1 / 1,20 = 0,833
card(G) = 2,667                     (Fig. 5 et Tableau 3 : 2,67)
```

### 4.3 Cardinalité souple de P

![Matrice interne de P](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/09_matrice_P.png)

*Image 9 : Matrice interne de P. `09_matrice_P.png`*

```
count(cafe)   = 1 / 2,50 = 0,400
count(coffee) = 1 / 2,17 = 0,462
count(caffe)  = 1 / 2,47 = 0,405
count(pizza)  = 1 / 1,60 = 0,625
count(plaza)  = 1 / 1,80 = 0,556
card(P) = 2,448                     (Fig. 5 et Tableau 3 : 2,45)
```

### 4.4 Union et intersection (section 3.2)

![Chaîne de calcul](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/10_chaine_de_calcul.png)

*Image 10 : Chaîne de calcul de l'article. `10_chaine_de_calcul.png`*

`G ∪ P` est la concaténation des 8 éléments : `cafe, pizza, hotel, cafe, coffee, caffe, pizza, plaza`.

![Matrice de l'union](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/11_matrice_union.png)

*Image 11 : Matrice de l'union. `11_matrice_union.png`*

![Counts dans l'union](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/12_union_counts.png)

*Image 12 : Counts dans l'union. `12_union_counts.png`*

```
card(G ∪ P) = 2,911                                (Tableau 3 : 2,91)
card(G ∩ P) = 2,667 + 2,448 − 2,911 = 2,203        (Tableau 3 : 2,21)
```

### 4.5 Résultats

```
Soft Precision = 2,203 / 2,448 = 0,90
Soft Recall    = 2,203 / 2,667 = 0,83
Soft F-score   = 2 × 2,203 / (2,667 + 2,448) = 0,86
```

![Résultats crisp vs soft](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/13_resultats_crisp_vs_soft.png)

*Image 13 : Résultats crisp vs soft. `13_resultats_crisp_vs_soft.png`*

![Récapitulatif](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/14_recap_cardinalites.png)

*Image 14 : Récapitulatif de l'exemple café. `14_recap_cardinalites.png`*

---

## 5. Exemples numériques (section 4 de l'article)

La similarité syntaxique est la distance de Levenshtein, la similarité sémantique est Word2Vec (entraîné sur l'anglais par Google). Une interface web des mesures soft est disponible : https://cs.uef.fi/sipu/soft/SoftEval/

![Tableau 2 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/15_tableau2_exemples.png)

*Image 15 : Tableau 2 de l'article, description des exemples. `15_tableau2_exemples.png`*

![Tableau 3 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/16_tableau3_cardinalites.png)

*Image 16 : Tableau 3 de l'article, cardinalités des ensembles. `16_tableau3_cardinalites.png`*

### 5.1 Exemple café

Les mots viennent d'une entreprise qui propose hébergement, restauration et cafétéria. Les mots-clés prédits retrouvent deux des trois mots de référence : le rappel crisp (0,67) est correct. La mesure sémantique surestime le rappel (0,93) car plaza est en partie « prédit » par les autres mots. Pour la précision, coffee et caffe (café mal orthographié) sont proches de la référence, mais seules les variantes soft donnent une précision élevée (0,80 et 0,90).

![Fig. 8 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig08.png)

*Fig. 8 (article). Synthèse de l'exemple café. `article_fig08.png`*

### 5.2 Exemple University

Les mesures crisp ne considèrent que university comme correct, d'où un F-score faible (0,14). Les mesures soft donnent de meilleurs scores (0,61 et 0,74). Le rappel devrait être élevé, car tous les mots de référence sont prédits sous une forme ou une autre. La variante sémantique fonctionne mieux car elle reconnaît les similarités entre university, teacher, student et pupil.

![Fig. 9 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig09.png)

*Fig. 9 (article). Synthèse de l'exemple University. `article_fig09.png`*

### 5.3 Exemple Gray Color

La prédiction est correcte, à de petites différences près. La variante crisp échoue (0,00 en précision et en rappel). La variante sémantique donne aussi des scores faibles, car le modèle Word2Vec, entraîné en anglais US, ne fournit pas de valeurs pour colour et grey (orthographe britannique). La mesure syntaxique donne un rappel élevé (0,82) mais ne peut pas écarter le mot vide (the). La précision reste donc un peu plus basse qu'attendu (0,63), mais c'est la seule mesure non nulle.

![Fig. 10 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig10.png)

*Fig. 10 (article). Synthèse de l'exemple Gray Color. `article_fig10.png`*

### 5.4 Jeu de données Countries

Jeu D6 du *Countries dataset* : dix clusters de pays européens, chacun contenant 50 variantes du nom obtenues par modifications aléatoires de caractères. Trois pays sont choisis comme référence, et quatre types de prédiction sont faits : (1) les trois corrects ; (2) seulement deux corrects ; (3) les trois corrects et un incorrect ; (4) deux corrects et un incorrect.

![Exemples Countries](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/17_countries_exemples.png)

*Image 17 : Exemples Countries et valeurs attendues. `17_countries_exemples.png`*

L'expérience est répétée 100 fois avec la variante soft (Levenshtein). La variante crisp étant pratiquement inutile (tous les résultats valent 0), l'article considère aussi une **variante à seuil simple (Crisp*)** : deux chaînes correspondent si leur similarité de Levenshtein vaut 0,8 ou plus. Le Tableau 4 montre que la variante soft est nettement supérieure aux variantes crisp.

![Tableau 4 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/18_tableau4_countries.png)

*Image 18 : Tableau 4 de l'article, expérience Countries. `18_tableau4_countries.png`*

### 5.5 Exemple de segmentation

Motivé par la segmentation de la parole. La similarité est la longueur des segments partagés. Aucune correspondance n'est exacte, donc la variante crisp est inutile. Crisp* ne fonctionne pas non plus, car aucun segment prédit n'a une similarité supérieure à 0,8 avec la référence. Les valeurs soft sont en revanche significatives et simples à calculer.

![Fig. 12 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig12.png)

*Fig. 12 (article). Exemple de segmentation. `article_fig12.png`*

![Tableau 5 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/19_tableau5_segmentation.png)

*Image 19 : Tableau 5 de l'article, expérience de segmentation. `19_tableau5_segmentation.png`*

### 5.6 Trajectoires GPS

Recherche par similarité dans Mopsi : l'utilisateur dessine une forme sur la carte, et les trajectoires les plus similaires sont retrouvées avec une mesure de similarité par grille. On attend des tours complets du lac (parcours Kaltimonkierto). La recherche est bonne mais manque un tour passant par un autre chemin à l'est (0,62) et renvoie un tour partiel (0,95). Les valeurs attendues sont 0,83. La variante crisp est encore inutile (0), Crisp* donne la bonne précision (0,83), la variante soft donne 0,86 et 0,95.

![Fig. 11 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/article_fig11.png)

*Fig. 11 (article). La recherche par geste renvoie les trajectoires les plus similaires (scores C-SIM de 0,77 ou plus). La référence est constituée des tours (presque) complets du lac Kaltimo, appelés Kaltimonkierto. `article_fig11.png`*

![Tableau 6 de l'article](Soft%20Precision%20and%20Recall%20m%C3%A9thodologie%20d%C3%A9taill%C3%A9e/20_tableau6_gps.png)

*Image 20 : Tableau 6 de l'article, trajectoires GPS. `20_tableau6_gps.png`*

---

## 6. Conclusions de l'article

- Les variantes soft de la précision et du rappel reposent sur une mesure de similarité propre à l'application : Levenshtein (syntaxique) et Word2Vec (sémantique) pour les chaînes, similarité par grille pour les trajectoires GPS.
- Les expériences montrent que les variantes soft donnent des résultats plus significatifs que la variante crisp. Cela peut réduire le temps passé à créer des jeux de référence, car l'exactitude n'est plus critique.
- **Inconvénient :** la méthode nécessite une mesure de similarité dépendante de l'application, même si des choix naturels existent pour les chaînes, les segments et les données GPS.
- **Limite :** la mesure peut donner des valeurs supérieures à 1 dans certains cas. Cela vient de la cardinalité souple, bien définie intuitivement mais qui tend à surestimer la taille des ensembles. Les auteurs n'ont pas trouvé de définition alternative fonctionnant parfaitement dans tous les cas ; les cardinalités peuvent toujours être bornées si on le souhaite.
- Les mesures soft donnent des estimations utiles pour l'extraction de mots-clés, là où les mesures crisp échouent, et peuvent être adoptées dans d'autres applications de recherche d'information et d'appariement où les correspondances inexactes sont utilisées.