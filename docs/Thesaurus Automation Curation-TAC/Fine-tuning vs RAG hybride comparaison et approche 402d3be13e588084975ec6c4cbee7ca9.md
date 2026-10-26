# Fine-tuning vs RAG hybride : comparaison et approches combinées

---

<aside>
📋

- **Plan**
</aside>

---

## 1. Objectif

L'objectif de ce benchmark est de choisir l'approche, ou la combinaison d'approches, qui donne les meilleurs résultats pour les deux tâches de l'agent TAC : la génération de concepts et le rattachement au thésaurus. Deux approches ont été développées et évaluées séparément, le fine-tuning ([Fine-tuning](Fine-tuning%203d4d3be13e58816eb546f3c810998ef4.md)) et le RAG hybride ([RAG hybride ](RAG%20hybride%203ebd3be13e58809aa015d3e717ebe9c9.md)). Cette page les compare, puis présente une approche qui combine les deux.

## 2. Fine-tuning vs RAG hybride

Cette partie compare le fine-tuning et le RAG hybride sur la génération de concepts et le rattachement au thésaurus. Chaque approche a fait l'objet de plusieurs essais : cinq niveaux de prompt et un niveau ALL pour le fine-tuning, un contexte à 1 ou 5 exemples pour le RAG hybride. Pour chaque approche, seule la meilleure configuration est retenue ici :

- **Fine-tuning** : Mistral-7B affiné au niveau 4, qui donne les meilleurs résultats sur les deux tâches (section 6.3 de la page Fine-tuning) ;
- **RAG hybride** : Mistral-7B de base avec un contexte de 5 exemples, la meilleure des deux configurations testées.

Le même modèle de base (Mistral-7B) est utilisé dans les deux cas : l'écart mesuré vient donc de l'approche, et non du modèle. Les métriques sont celles des deux pages : similarité cosinus (bge-m3), puis précision, rappel et F1 en versions crisp et soft pour la génération de concepts ; similarité cosinus pour le rattachement. Dans chaque tableau, la meilleure valeur de chaque ligne est surlignée en jaune, et la dernière ligne compte le nombre de métriques gagnées par chaque approche.

### 2.1. Génération de concepts

Toutes les approches de cette page sont évaluées sur les mêmes données de test : 268 concepts, identiques pour le fine-tuning, le RAG hybride et les variantes HyRAG-FT. La comparaison est donc directe.

#### 2.1.1. Similarité cosinus

Le tableau suivant compare la similarité cosinus entre chaque attribut généré et l'attribut de référence, puis la moyenne des quatre attributs.

![ft_vs_rag_similarite.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/ft_vs_rag_similarite.svg)

Le fine-tuning gagne 4 métriques sur 5 et obtient la meilleure similarité moyenne (0,656 contre 0,630). L'écart le plus net porte sur `definition` (0,687 contre 0,637) et sur `broader` (0,680 contre 0,644) : le modèle affiné a appris le style des définitions et la hiérarchie des thésaurus d'Opentheso. Le RAG hybride ne l'emporte que sur `altLabel`, et de très peu (0,647 contre 0,642) : les exemples récupérés dans la base vectorielle lui fournissent des synonymes proches.

#### 2.1.2. Précision, rappel et F1 : version crisp

Le tableau suivant compare la précision, le rappel et le F1 calculés en correspondance exacte, pour `altLabel`, `broader` et `narrower`.

![ft_vs_rag_crisp.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/ft_vs_rag_crisp.svg)

Le fine-tuning gagne 8 métriques sur 9, dont les trois F1. Le gain est le plus marqué sur `broader` (0,239 contre 0,216) et sur la précision de `narrower` (0,093 contre 0,060) : le modèle affiné reprend plus souvent la forme exacte des termes de référence. Le RAG hybride ne gagne que le rappel de `narrower` (0,093 contre 0,082) : il propose davantage de termes spécifiques, dont une partie est exacte. Pour les deux approches, les valeurs restent basses, sauf sur `broader`.

#### 2.1.3. Précision, rappel et F1 : version soft

Le tableau suivant compare la précision, le rappel et le F en version soft, qui accepte un terme proche par le sens (Fränti et Mariescu-Istodor, 2023).

![ft_vs_rag_soft.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/ft_vs_rag_soft.svg)

C'est sur ces métriques que la comparaison est la plus serrée : 5 pour le fine-tuning, 4 pour le RAG hybride. Le fine-tuning gagne toutes les mesures de `broader` et la précision des trois champs : ce qu'il propose est plus souvent juste. Le RAG hybride gagne le rappel et le soft F sur `altLabel` (0,5837 contre 0,5630) et sur `narrower` (0,6362 contre 0,6110) : grâce aux exemples du contexte, il retrouve davantage de synonymes et de termes spécifiques attendus. Les deux approches sont donc complémentaires : le fine-tuning apporte la précision, le RAG hybride la couverture, ce qui justifie de les combiner (section 3).

### 2.2. Rattachement au thésaurus

Les deux approches sont évaluées sur les mêmes 5 731 requêtes : la comparaison est donc directe.

#### 2.2.1. Similarité cosinus

Le tableau suivant compare la similarité cosinus moyenne entre le thésaurus proposé et le thésaurus attendu, puis la répartition des requêtes par tranche de similarité. Seules deux tranches sont comptées : [0,95 ; 1,00], qui correspond au bon titre ou à un titre quasi identique, et [0,00 ; 0,70[, qui correspond à un mauvais rattachement. Les tranches intermédiaires ne le sont pas, car une valeur plus élevée n'y est ni meilleure ni moins bonne.

![ft_vs_rag_ratt_similarite.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/ft_vs_rag_ratt_similarite.svg)

Le fine-tuning l'emporte très nettement : similarité moyenne de 0,917 contre 0,645, 80,7 % de titres quasi identiques contre 18,7 %, et 12,5 % de mauvais rattachements contre 55,0 %. Le RAG hybride propose souvent un thésaurus de domaine voisin sans retrouver le titre exact : 26,2 % de ses requêtes se situent entre 0,70 et 0,95, contre 6,7 % pour le fine-tuning. Le modèle affiné, entraîné directement sur les titres des thésaurus, les reproduit à l'identique.

#### 2.2.2. Similarité selon la richesse du concept

Le tableau suivant compare la similarité moyenne selon la richesse du concept fourni en entrée, c'est-à-dire le nombre d'attributs remplis en plus du `prefLabel` (N est le nombre de requêtes de chaque classe).

![ft_vs_rag_ratt_richesse.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/ft_vs_rag_ratt_richesse.svg)

Le fine-tuning gagne aux cinq niveaux de richesse, avec un écart de 0,19 à 0,30. Même pour un concept réduit à son `prefLabel` (classe 0), il atteint 0,823, au-dessus du meilleur score du RAG hybride toutes classes confondues (0,704). Les deux approches progressent avec la richesse du concept, mais le fine-tuning progresse davantage jusqu'à la classe 3 (de 0,823 à 0,962, contre 0,636 à 0,686 pour le RAG hybride).

## 3. Fine-tuning + RAG hybride (HyRAG-FT)

La comparaison de la section 2 montre que les deux approches sont complémentaires : le fine-tuning apporte la précision et la maîtrise du format SKOS, le RAG hybride apporte la couverture grâce aux exemples récupérés dans la base. L'approche HyRAG-FT combine les deux : le contexte construit par le RAG hybride est injecté dans le prompt d'un modèle fine-tuné, au lieu d'un modèle de base. Deux variantes sont étudiées : la brique 4 avec contexte RAG, où le modèle fine-tuné au niveau 4 reçoit les exemples seulement au moment de l'inférence, et la brique 5, où le modèle est fine-tuné directement sur les prompts construits par le RAG hybride (section 3.2.3).

### 3.1. Architecture de la combinaison

Le schéma suivant présente l'architecture générale de HyRAG-FT, commune à la génération de concepts et au rattachement au thésaurus.

![architecture-hyrag-ft.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/architecture-hyrag-ft.svg)

La partie récupération reste celle du RAG hybride : la requête est recherchée dans la base vectorielle Qdrant, les candidats sont reclassés par le reranker, puis enrichis par le graphe Neo4j (relations hiérarchiques et thésaurus d'appartenance). Les exemples retenus forment le contexte du prompt. La seule différence avec le RAG hybride est le modèle de génération : un modèle affiné par LoRA au niveau 4 remplace le modèle de base. Le modèle connaît donc déjà le format attendu et le style des thésaurus, et le contexte lui apporte des exemples proches du concept traité.

### 3.2. Génération de concepts

Les deux variantes sont évaluées sur les trois modèles (Llama-3.1-8B, Mistral-7B et Qwen2.5-7B), avec les mêmes 268 concepts de test que le fine-tuning seul et le RAG hybride. Pour la brique 4 avec contexte RAG (sections 3.2.1 et 3.2.2), les modèles fine-tunés au niveau 4 sont testés avec deux tailles de contexte, 1 exemple et 5 exemples, comme pour le RAG hybride. Pour la brique 5 (section 3.2.3), les modèles sont fine-tunés sur des prompts qui contiennent déjà les 5 exemples du RAG hybride. Comme dans la section 2, la meilleure valeur de chaque ligne est surlignée en jaune, et la dernière ligne compte le nombre de métriques gagnées par chaque modèle (une égalité compte pour chaque modèle concerné).

#### 3.2.1. Brique 4 avec contexte RAG : 1 exemple

Dans cette configuration, le prompt du modèle fine-tuné contient un seul exemple de concept proche, le premier renvoyé par le RAG hybride après reclassement.

**a. Similarité cosinus**

Le tableau suivant compare la similarité cosinus entre chaque attribut généré et l'attribut de référence, ainsi que la moyenne des quatre attributs. La partie basse donne le taux de correspondance exacte, c'est-à-dire la part des concepts pour lesquels l'attribut généré est identique à la référence.

![hyragft_similarite.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_similarite.svg)

Llama-3.1-8B gagne toutes les lignes de similarité cosinus et obtient la meilleure moyenne (0,662, contre 0,652 pour Mistral et 0,636 pour Qwen). Mistral-7B gagne en revanche toutes les lignes de correspondance exacte, en particulier sur `definition` (6,7 %) et `altLabel` (1,9 %) : il reproduit plus souvent la formulation exacte de la référence. Sur `broader`, Llama et Mistral sont à égalité avec 26,1 % de parents exacts. Qwen2.5-7B ne gagne aucune ligne : son point faible est `narrower` (0,579 et 1,1 % exact).

**b. Précision, rappel et F1 : version crisp**

Le tableau suivant compare la précision, le rappel et le F1 calculés en correspondance exacte, pour `altLabel`, `broader` et `narrower`.

![hyragft_crisp.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_crisp.svg)

Mistral-7B gagne 7 métriques sur 9, dont les trois F1 : 0,085 sur `altLabel` et sur `narrower`, et 0,261 sur `broader` à égalité avec Llama. Llama gagne les deux rappels (0,112 sur `altLabel` et 0,100 sur `narrower`) : il propose davantage de termes, dont une partie est exacte, mais avec une précision plus faible. Sur `broader`, P, R et F1 sont identiques, car chaque concept n'a qu'un seul parent. Qwen reste en dernière position sur toutes les lignes.

**c. Précision, rappel et F1 : version soft**

Le tableau suivant compare la précision, le rappel et le F en version soft, qui accepte un terme proche par le sens (Fränti et Mariescu-Istodor, 2023).

![hyragft_soft.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_soft.svg)

Llama-3.1-8B gagne 6 métriques sur 9 : toutes celles de `broader`, ainsi que le rappel et le soft F de `narrower` (0,6343). Mistral gagne la précision soft sur `altLabel` (0,6206) et sur `narrower` (0,6754) : ce qu'il propose est juste, mais il propose moins de termes, comme le montre son rappel faible sur `altLabel` (0,5467). Qwen gagne une seule ligne, le soft F de `altLabel` (0,5821), grâce à un bon équilibre entre précision et rappel sur ce champ.

#### 3.2.2. Brique 4 avec contexte RAG : 5 exemples

Dans cette configuration, le prompt du modèle fine-tuné contient les cinq exemples les plus proches renvoyés par le RAG hybride. Les tableaux suivent la même structure que pour le contexte de 1 exemple.

**a. Similarité cosinus**

Le tableau suivant compare la similarité cosinus de chaque attribut et sa moyenne, puis le taux de correspondance exacte, pour un contexte de 5 exemples.

![hyragft5_similarite.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft5_similarite.svg)

Llama-3.1-8B gagne 5 métriques et garde la meilleure moyenne (0,662), avec les meilleurs scores sur `definition` (0,692) et `broader` (0,697). Il atteint surtout 30,6 % de parents exacts, le meilleur taux obtenu avec HyRAG-FT. Mistral-7B se rapproche nettement (moyenne 0,658) et prend la première place sur `narrower` (0,624). Qwen2.5-7B gagne `altLabel` (0,647), mais recule sur `broader` (0,642) et `narrower` (0,558) : sa moyenne descend à 0,626.

**b. Précision, rappel et F1 : version crisp**

Le tableau suivant compare la précision, le rappel et le F1 en correspondance exacte pour un contexte de 5 exemples.

![hyragft5_crisp.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft5_crisp.svg)

Les gains sont plus partagés qu'avec 1 exemple : 4 métriques pour Llama, 3 pour Mistral et 2 pour Qwen. Llama domine `broader` avec un F1 de 0,306, le meilleur score crisp de cette page sur ce champ. Mistral gagne les trois mesures de `narrower` (F1 0,098). Qwen gagne la précision et le F1 de `altLabel` (0,099 et 0,089), alors qu'il ne gagnait aucune ligne avec 1 exemple : les synonymes présents dans les cinq exemples l'aident à retrouver la forme exacte des `altLabel`.

**c. Précision, rappel et F1 : version soft**

Le tableau suivant compare la précision, le rappel et le F en version soft pour un contexte de 5 exemples.

![hyragft5_soft.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft5_soft.svg)

Llama-3.1-8B gagne 5 métriques sur 9 : toutes celles de `broader` (soft F 0,5870), ainsi que le rappel sur `altLabel` (0,6618) et sur `narrower` (0,6771). Mistral gagne la précision et le soft F de `narrower` (0,6871 et 0,6352). Qwen gagne la précision et le soft F de `altLabel` (0,6345 et 0,5950). Comme en crisp, chaque modèle a donc un champ de prédilection : `broader` pour Llama, `narrower` pour Mistral et `altLabel` pour Qwen.

#### 3.2.3. Brique 5 : fine-tuning sur les prompts du RAG hybride

Avec la brique 4, le modèle est fine-tuné sans contexte, puis reçoit les exemples du RAG hybride seulement au moment de l'inférence : il découvre donc un format de prompt qu'il n'a jamais vu pendant l'entraînement. La brique 5 supprime ce décalage : le contexte du RAG hybride est intégré au prompt dès l'entraînement, et le modèle apprend à générer le concept cible à partir de ce prompt enrichi. L'entraînement et l'inférence utilisent ainsi exactement le même format.

**a. Construction du prompt**

Le schéma suivant présente la construction d'un prompt de la brique 5, utilisée à la fois pour l'entraînement et pour le test.

![architecture_brique5.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/architecture_brique5.svg)

Le jeu de données de la brique 5 contient 2 427 concepts complets, répartis en 1 891 concepts d'entraînement, 268 de validation et 268 de test ; les 268 concepts de test sont les mêmes que pour les autres approches. Pour chaque concept cible, une requête est construite à partir de ses attributs (terme, synonymes, définition, terme générique), dans le même format que les documents indexés dans Qdrant. La recherche dans la collection `tac_concepts` (407 761 concepts) renvoie 40 candidats, reclassés par le reranker bge-reranker-v2-m3, puis enrichis par Neo4j avec le broader et les narrower de chaque candidat. La fonction `choisir()` retient ensuite 5 exemples, dont au moins un complet aux 5 attributs. Le prompt final reprend la structure des briques précédentes (rôle, préambule, exemples, cadre et demande, méthode, contraintes), avec deux ajouts : un avertissement indiquant que certains exemples sont incomplets, et un contexte listant les termes génériques et spécifiques possibles.

**b. Entraînement**

Les trois modèles sont fine-tunés par LoRA sur les prompts de la brique 5. Le tableau suivant regroupe, pour chaque modèle et chaque époque, la training loss, la validation loss, l'entropie, le nombre de tokens vus et la token accuracy. La meilleure époque de chaque modèle, celle où la validation loss est minimale, est surlignée en jaune.

![b5_train_table.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/b5_train_table.svg)

La meilleure époque est la 4 pour Llama-3.1-8B et Qwen2.5-7B, et la 3 pour Mistral-7B. À ce point, Mistral obtient la plus faible validation loss (0,3966), la plus faible entropie (0,3216) et la meilleure token accuracy (0,9133), tout en voyant moins de tokens que les deux autres modèles (5,6 millions contre environ 7,3 millions). Qwen a la validation loss la plus élevée (0,4556). Le checkpoint retenu pour chaque modèle est celui de sa meilleure époque.

La figure suivante présente l'évolution de la training loss et de la validation loss pour les trois modèles. La ligne pointillée marque la meilleure époque.

![b5_curves.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/b5_curves.svg)

Pour les trois modèles, la training loss baisse régulièrement, alors que la validation loss atteint un minimum puis remonte : au-delà de la meilleure époque, les modèles commencent à sur-apprendre. L'écart est le plus net pour Mistral, dont la validation loss remonte de 0,397 à 0,447 entre les époques 3 et 5 alors que la training loss tombe à 0,082. Mistral n'a donc été entraîné que sur 5 époques.

**c. Similarité cosinus**

Le tableau suivant compare la similarité cosinus de chaque attribut et sa moyenne, puis le taux de correspondance exacte, pour les trois modèles de la brique 5.

![b5_similarite.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/b5_similarite.svg)

Mistral-7B gagne les 9 lignes avec un écart net : similarité moyenne de 0,727, contre 0,674 pour Llama et 0,662 pour Qwen. Il dépasse 0,75 sur `definition` (0,753) et `broader` (0,756) et atteint 41,0 % de parents exacts. Ses taux de correspondance exacte dépassent aussi 11 % sur `altLabel`, `definition` et `narrower`, alors qu'ils restaient sous 7 % avec la brique 4. Llama et Qwen sont proches l'un de l'autre, Qwen restant le plus faible sur `narrower` (0,601).

**d. Précision, rappel et F1 : version crisp**

Le tableau suivant compare la précision, le rappel et le F1 en correspondance exacte pour les trois modèles de la brique 5.

![b5_crisp.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/b5_crisp.svg)

Mistral-7B gagne les 9 métriques, avec un F1 de 0,232 sur `altLabel`, 0,410 sur `broader` et 0,279 sur `narrower`. Sur les listes ouvertes, qui plafonnaient autour de 0,08 à 0,10 en F1 avec la brique 4, le score est presque multiplié par trois : le modèle reprend beaucoup plus souvent la forme exacte des termes de référence. Llama et Qwen progressent aussi (F1 `broader` de 0,340 et 0,332), mais restent nettement derrière Mistral.

**e. Précision, rappel et F1 : version soft**

Le tableau suivant compare la précision, le rappel et le F en version soft pour les trois modèles de la brique 5.

![b5_soft.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/b5_soft.svg)

Mistral-7B gagne 8 métriques sur 9, avec un soft F de 0,6663 sur `altLabel`, 0,6637 sur `broader` et 0,6966 sur `narrower`, ainsi qu'une précision soft de 0,7525 sur `narrower`. Qwen gagne seulement le rappel soft de `altLabel` (0,6829) : il propose davantage de synonymes proches de la référence, mais avec une précision plus faible que Mistral.

#### 3.2.4. Synthèse

**Par rapport au RAG hybride et au fine-tuning seuls.** Avec un contexte de 1 exemple, les trois modèles dépassent nettement leurs résultats en RAG hybride avec 1 exemple : la similarité moyenne passe de 0,579 à 0,662 pour Llama, de 0,627 à 0,652 pour Mistral et de 0,578 à 0,636 pour Qwen. Avec 5 exemples, Mistral HyRAG-FT (moyenne 0,658, F1 crisp `broader` 0,295) dépasse à la fois le fine-tuning seul (0,656 et 0,239) et le RAG hybride avec 5 exemples (0,630 et 0,216), et atteint en soft F sur `narrower` le niveau du RAG hybride (0,6352 contre 0,6362). La combinaison garde donc la précision du fine-tuning tout en récupérant la couverture du RAG hybride.

**1 exemple ou 5 exemples.** Le passage à 5 exemples profite surtout à `broader` : le F1 crisp passe de 0,261 à 0,306 pour Llama et de 0,261 à 0,295 pour Mistral, et le taux de parents exacts de 26,1 % à 30,6 % pour Llama. Mistral progresse aussi sur `narrower` (F1 crisp de 0,085 à 0,098) et sur sa similarité moyenne (de 0,652 à 0,658). Qwen réagit différemment : il progresse sur `altLabel` mais recule sur `broader` et `narrower`, et sa moyenne baisse (de 0,636 à 0,626). Il exploite donc moins bien un contexte long.

**Brique 5.** Intégrer le contexte du RAG hybride dès l'entraînement donne le gain le plus important de cette page. Mistral-7B en brique 5 atteint une similarité moyenne de 0,727, contre 0,658 avec la brique 4 et 5 exemples, 0,656 pour le fine-tuning seul et 0,630 pour le RAG hybride seul. Le F1 crisp de `broader` monte à 0,410 (contre 0,295, 0,239 et 0,216), et les F1 de `altLabel` et `narrower` sont multipliés par environ trois. Le modèle a appris à exploiter les exemples pendant l'entraînement : il sait quels éléments reprendre, compléter ou ignorer, au lieu de découvrir ce contexte au moment de l'inférence.

**Configuration retenue.** Pour la génération de concepts, Mistral-7B fine-tuné en brique 5 (meilleure époque : 3) est la meilleure configuration : il gagne presque toutes les métriques face aux deux autres modèles et dépasse toutes les autres approches. Pour la brique 4 avec contexte RAG, Llama-3.1-8B avec un contexte de 5 exemples donne les meilleurs résultats d'ensemble : meilleure similarité moyenne (0,662), meilleurs scores sur `broader` en cosinus, crisp et soft, et le plus de métriques gagnées dans les trois tableaux. Mistral-7B avec 5 exemples reste une alternative très proche, meilleure sur `narrower`.

### 3.3. Rattachement au thésaurus

Pour le rattachement, les trois modèles fine-tunés sur la tâche de rattachement (Llama-3.1-8B, Mistral-7B et Qwen2.5-7B) reçoivent un contexte de 1 ou de 5 exemples construit par le RAG hybride. L'évaluation porte sur les mêmes 5 731 requêtes que la section 2.2 : la comparaison avec le fine-tuning seul et le RAG hybride seul est donc directe. Comme dans la section 2.2.1, seules deux tranches de similarité sont comptées : [0,95 ; 1,00] (bon titre ou titre quasi identique, plus la part est haute, mieux c'est) et [0,00 ; 0,70[ (mauvais rattachement, plus la part est basse, mieux c'est). Pour les trois modèles et les deux contextes, la médiane vaut 1,000 et aucune réponse n'est vide.

#### 3.3.1. Contexte de 1 exemple

**a. Similarité cosinus**

Le tableau suivant compare la similarité cosinus moyenne entre le thésaurus proposé et le thésaurus attendu, puis la répartition des requêtes par tranche de similarité.

![hyragft_ratt1_sim.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_ratt1_sim.svg)

Mistral-7B gagne les trois métriques comptées : meilleure similarité moyenne (0,913), plus forte part de titres quasi identiques (77,2 %) et plus faible part de mauvais rattachements (12,7 %). Llama-3.1-8B suit de près (0,903, 74,5 % et 14,5 %). Qwen2.5-7B est en retrait (0,880) : il a moins de titres exacts (67,8 %) et davantage de réponses dans les tranches intermédiaires, en particulier entre 0,70 et 0,90 (12,6 %), ce qui correspond à un thésaurus voisin plutôt qu'au bon titre.

**b. Similarité selon la richesse du concept**

Le tableau suivant compare la similarité moyenne selon la richesse du concept fourni en entrée, c'est-à-dire le nombre d'attributs remplis en plus du `prefLabel` (N est le nombre de requêtes de chaque classe).

![hyragft_ratt1_rich.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_ratt1_rich.svg)

Mistral gagne les classes 1 à 4, avec un maximum de 0,948 en classe 3. Llama gagne la classe 0 (0,835 contre 0,828) : pour un concept réduit à son `prefLabel`, il exploite mieux l'exemple fourni. Les trois modèles progressent avec la richesse du concept jusqu'à la classe 2 ou 3, puis se stabilisent ou baissent légèrement en classe 4, qui ne compte que 56 requêtes. Qwen est le plus sensible au manque d'information : 0,765 en classe 0, soit 0,07 de moins que Llama.

#### 3.3.2. Contexte de 5 exemples

**a. Similarité cosinus**

Le tableau suivant compare la similarité cosinus moyenne et la répartition par tranche de similarité pour un contexte de 5 exemples.

![hyragft_ratt5_sim.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_ratt5_sim.svg)

Mistral-7B gagne de nouveau les trois métriques comptées (0,909, 75,2 % de titres quasi identiques et 12,8 % de mauvais rattachements), mais l'écart avec Llama-3.1-8B se réduit (0,906, 73,7 % et 13,5 %). Qwen2.5-7B reste derrière (0,883 et 16,8 % de mauvais rattachements). Par rapport au contexte de 1 exemple, les écarts sont très faibles : Mistral perd légèrement (de 0,913 à 0,909), Llama et Qwen gagnent légèrement (+0,003).

**b. Similarité selon la richesse du concept**

Le tableau suivant compare la similarité moyenne selon la richesse du concept pour un contexte de 5 exemples.

![hyragft_ratt5_rich.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/hyragft_ratt5_rich.svg)

La répartition des gains est la même qu'avec 1 exemple : Llama gagne la classe 0 (0,845) et Mistral les classes 1 à 4 (jusqu'à 0,941 en classe 4). Le contexte de 5 exemples aide surtout les concepts pauvres : en classe 0, la similarité passe de 0,835 à 0,845 pour Llama, de 0,828 à 0,835 pour Mistral et de 0,765 à 0,806 pour Qwen. Pour les concepts riches, l'effet est faible ou négatif, sauf pour Mistral en classe 4.

#### 3.3.3. Synthèse

**Par rapport au RAG hybride et au fine-tuning seuls.** HyRAG-FT dépasse très largement le RAG hybride seul (0,913 contre 0,645 en similarité moyenne, 77,2 % contre 18,7 % de titres quasi identiques) et reste très proche du fine-tuning seul : Mistral fine-tuné sans contexte obtient 0,917, 80,7 % de titres quasi identiques et 12,5 % de mauvais rattachements, contre 0,913, 77,2 % et 12,7 % avec 1 exemple. Pour le rattachement, le modèle affiné connaît déjà les titres des thésaurus : le contexte ne le rend pas plus précis, mais ne le dégrade presque pas.

**Selon la richesse du concept.** Le contexte apporte en revanche un gain sur les concepts les plus pauvres : en classe 0, HyRAG-FT atteint 0,845 (Llama, 5 exemples) contre 0,823 pour le fine-tuning seul. Pour les concepts riches, le fine-tuning seul reste légèrement meilleur (0,962 en classe 3 contre 0,948 au mieux avec HyRAG-FT).

**Configuration retenue.** Pour le rattachement, Mistral-7B avec un contexte de 1 exemple est la meilleure configuration HyRAG-FT (0,913). Ses résultats sont très proches de ceux du fine-tuning seul, et c'est elle qui est retenue pour l'agent TAC : le contexte construit par le HyRAG peut être affiché à l'utilisateur et validé avant la soumission au modèle (section 5).

## 4. Comparatif : RAG hybride, fine-tuning et HyRAG-FT

Cette partie rassemble la meilleure configuration de chaque approche pour les comparer directement. Pour que l'écart mesuré vienne de l'approche et non du modèle, toutes les colonnes utilisent Mistral-7B : fine-tuning seul (niveau 4), RAG hybride (modèle de base, 5 exemples), HyRAG-FT brique 4 (modèle fine-tuné au niveau 4, avec 5 exemples à l'inférence) et HyRAG-FT brique 5 (modèle fine-tuné sur les prompts du RAG hybride). Comme dans les sections précédentes, la meilleure valeur de chaque ligne est surlignée en jaune et la dernière ligne compte le nombre de métriques gagnées par chaque approche.

### 4.1. Génération de concepts

Les quatre approches sont évaluées sur les mêmes 268 concepts de test : les écarts mesurés viennent donc uniquement de l'approche.

#### 4.1.1. Similarité cosinus

Le tableau suivant compare la similarité cosinus de chaque attribut et sa moyenne pour les quatre approches.

![cmp4_similarite.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/cmp4_similarite.svg)

La brique 5 gagne les 5 lignes, avec une similarité moyenne de 0,727 contre 0,658 pour la brique 4, 0,656 pour le fine-tuning seul et 0,630 pour le RAG hybride. Le gain est régulier sur les quatre attributs, entre +0,06 et +0,07 par rapport à la deuxième meilleure approche. À l'inverse, la brique 4 n'apporte presque rien par rapport au fine-tuning seul (0,658 contre 0,656) : ajouter des exemples à un modèle qui n'a pas appris à les lire ne suffit pas.

#### 4.1.2. Précision, rappel et F1 : version crisp

Le tableau suivant compare la précision, le rappel et le F1 en correspondance exacte pour les quatre approches.

![cmp4_crisp.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/cmp4_crisp.svg)

La brique 5 gagne les 9 métriques. Le F1 de `broader` progresse à chaque étape : 0,216 pour le RAG hybride, 0,239 pour le fine-tuning seul, 0,295 pour la brique 4 et 0,410 pour la brique 5. Sur les listes ouvertes, la brique 5 change d'échelle : F1 de 0,232 sur `altLabel` et de 0,279 sur `narrower`, contre moins de 0,10 pour toutes les autres approches.

#### 4.1.3. Précision, rappel et F1 : version soft

Le tableau suivant compare la précision, le rappel et le F en version soft pour les quatre approches.

![cmp4_soft.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/cmp4_soft.svg)

La brique 5 gagne encore les 9 métriques. Elle réunit les deux qualités observées dans la section 2 : la précision du fine-tuning (soft P de 0,7525 sur `narrower`, contre 0,6829) et la couverture du RAG hybride (soft R de 0,6659 sur `altLabel` et de 0,6876 sur `narrower`, au-dessus du RAG hybride). Les approches précédentes devaient choisir entre précision et couverture ; la brique 5 obtient les deux.

### 4.2. Rattachement au thésaurus

Pour le rattachement, il n'y a pas de brique 5 : la comparaison porte sur le fine-tuning seul, le RAG hybride et HyRAG-FT avec un contexte de 1 exemple, la meilleure configuration HyRAG-FT pour Mistral-7B (section 3.3). Les trois approches sont évaluées sur les mêmes 5 731 requêtes : la comparaison est donc directe.

#### 4.2.1. Similarité cosinus

Le tableau suivant compare la similarité cosinus moyenne et la répartition des requêtes par tranche de similarité. Comme dans la section 2.2.1, seules les tranches [0,95 ; 1,00] et [0,00 ; 0,70[ sont comptées.

![cmp4_ratt_sim.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/cmp4_ratt_sim.svg)

Le fine-tuning seul gagne les trois métriques comptées, mais HyRAG-FT le suit de très près : 0,913 contre 0,917 en similarité moyenne, 77,2 % contre 80,7 % de titres quasi identiques, et 12,7 % contre 12,5 % de mauvais rattachements. Les deux approches qui utilisent un modèle fine-tuné sont très loin devant le RAG hybride seul (0,645 et 55,0 % de mauvais rattachements). Pour cette tâche, c'est le fine-tuning qui fait l'essentiel du travail ; l'écart avec HyRAG-FT est assez faible pour que la combinaison, mieux adaptée à l'agent TAC et à la validation humaine, soit retenue (section 5).

#### 4.2.2. Similarité selon la richesse du concept

Le tableau suivant compare la similarité moyenne selon la richesse du concept fourni en entrée (N est le nombre de requêtes de chaque classe).

![cmp4_ratt_rich.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/cmp4_ratt_rich.svg)

Le fine-tuning seul gagne les classes 1 à 4, et HyRAG-FT la classe 0 (0,828 contre 0,823). Le contexte du RAG hybride aide donc surtout les concepts réduits à leur `prefLabel`, pour lesquels le modèle manque d'information sur le domaine ; avec 5 exemples, ce gain monte jusqu'à 0,845 (Llama-3.1-8B, section 3.3.2). Pour les concepts décrits, les écarts restent faibles (moins de 0,015).

## 5. Intégration dans l'agent TAC et validation humaine

Les configurations retenues sont intégrées dans l'agent TAC. L'agent reçoit la requête de l'utilisateur et l'oriente vers la bonne étape : génération de concepts (outil 1), rattachement aux thésaurus (outil 2), ou les autres outils prévus. Il choisit ensuite la base vectorielle à interroger, les relations du graphe Neo4j à utiliser et le modèle fine-tuné adapté, modèle concepts ou modèle thésaurus. Le fonctionnement détaillé de l'agent TAC fait l'objet d'une page dédiée ; cette section présente seulement ce qui concerne les deux tâches étudiées ici.

La combinaison HyRAG-FT s'intègre mieux dans l'agent que le fine-tuning seul. Au lieu d'afficher à l'utilisateur un prompt construit de manière arbitraire, l'agent utilise le RAG hybride pour construire le prompt à partir des exemples les plus proches et de leurs relations dans le graphe. Ce prompt est affiché à l'utilisateur, en général un documentaliste ou un spécialiste du domaine, qui peut le vérifier, le corriger ou le valider, puis il devient l'entrée du modèle fine-tuné. Avec le fine-tuning seul, le modèle reçoit uniquement la requête, sans contexte à contrôler. La solution finale combine donc HyRAG-FT et une validation humaine dans la boucle (human-in-the-loop), pour les deux tâches.

### 5.1. Architecture de l'agent

Le schéma suivant présente l'architecture de l'agent telle qu'elle est utilisée : l'agent TAC et ses outils, les données et le GraphRAG, et les deux modèles Mistral 7B déjà fine-tunés. Les étapes d'entraînement ne sont pas représentées : celles du modèle concepts sont décrites dans la section 3.2.3 (brique 5). Le workflow est détaillé dans la section 5.2.

![architecture_agent_tac_v3.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/architecture_agent_tac_v3.svg)

L'utilisateur envoie une requête en langage naturel. L'agent TAC l'analyse, choisit l'outil, la base vectorielle et le modèle fine-tuné adaptés. Le contexte GraphRAG est ensuite assemblé avec la requête pour former le prompt, envoyé au modèle concepts ou au modèle thésaurus :

- **Outil 1 : génération de concepts**. L'agent utilise la base vectorielle de concepts (Qdrant) et le graphe Neo4j (relations broader et narrower) pour construire le contexte, puis le modèle Mistral-7B fine-tuné en brique 5. Ce modèle a été entraîné sur des prompts qui contiennent déjà les 5 exemples proches récupérés dans Qdrant et Neo4j (section 3.2.3) : la brique 5 a été créée pour améliorer les résultats de la génération de concepts.
- **Outil 2 : rattachement aux thésaurus**. L'agent utilise la base vectorielle de thésaurus et la relation « appartient à » du graphe Neo4j pour construire le contexte, puis le modèle Mistral-7B fine-tuné pour les thésaurus. Ce modèle a été entraîné directement sur des paires question/réponse. Ses résultats étant déjà très bons, une brique 5 n'a pas été nécessaire : avec le contexte du HyRAG, il obtient des résultats très proches du fine-tuning seul (0,913 contre 0,917, section 4.2), tout en permettant la validation par l'utilisateur.

Les données proviennent de l'API OpenTheso, qui alimente les deux bases vectorielles et le graphe de connaissances. Deux autres outils sont prévus dans l'agent mais restent à implémenter : l'alignement des thésaurus internes et externes (outil 3) et l'exportation au format SKOS (outil 4).

### 5.2. Workflow avec validation humaine

Le schéma suivant présente le workflow de l'agent. Il est commun aux deux outils : seul le modèle fine-tuné change, modèle concepts pour l'outil 1 et modèle thésaurus pour l'outil 2. Les deux losanges orange marquent les points de validation par l'utilisateur.

![workflow_agent_tac.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/workflow_agent_tac.svg)

Le workflow suit huit étapes, dont deux points de validation par l'utilisateur :

1. **Réception de la requête** par l'agent.
2. **Sélection** de l'outil, de la base vectorielle et du modèle fine-tuné (concepts ou thésaurus).
3. **Construction du contexte GraphRAG** : les 5 concepts les plus proches avec leurs broader et narrower pour l'outil 1, les thésaurus candidats avec la relation « appartient à » pour l'outil 2.
4. **Validation du contexte** par l'utilisateur. S'il n'est pas validé, l'utilisateur modifie le contexte (retrait d'un exemple hors sujet, correction d'un terme générique, etc.) et le prompt est reconstruit.
5. **Génération** par le modèle fine-tuné choisi : modèle concepts (brique 5) ou modèle thésaurus.
6. **Présentation du résultat** à l'utilisateur : le concept généré ou le thésaurus proposé.
7. **Validation du résultat**. S'il n'est pas validé, les corrections de l'utilisateur sont réinjectées dans la construction du prompt, et une nouvelle génération est lancée.
8. **Enregistrement** du résultat validé via l'API OpenTheso.

Cette validation humaine est importante pour deux raisons. D'une part, les modèles s'appuient sur les exemples du contexte, en particulier le modèle concepts de la brique 5 : un exemple hors sujet peut l'orienter vers un mauvais broader ou de mauvais narrower. La validation du contexte à l'étape 4 permet de corriger ce risque avant la génération. D'autre part, aucun résultat n'est enregistré dans OpenTheso sans avoir été vérifié par un spécialiste, ce qui est indispensable pour un thésaurus patrimonial. La brique 5 se prête bien à ce fonctionnement : le format du prompt est le même à l'entraînement et à l'inférence, donc un contexte modifié par l'utilisateur reste dans le format que le modèle connaît.

## 6. Conclusion

Ce benchmark compare trois approches pour les deux tâches de l'agent TAC : le fine-tuning, le RAG hybride et leur combinaison HyRAG-FT, étudiée en deux variantes (brique 4 avec contexte RAG et brique 5). Toutes les approches sont évaluées sur les mêmes données de test. Le tableau suivant résume la configuration retenue pour chaque tâche.

![recap_v2.svg](Fine-tuning%20vs%20RAG%20hybride%20comparaison%20et%20approche/recap_v2.svg)

**Génération de concepts.** La meilleure configuration est HyRAG-FT brique 5 avec Mistral-7B. La brique 5 a été créée spécifiquement pour améliorer les résultats de la génération de concepts. Le fine-tuning seul apporte la précision et le format, le RAG hybride seul apporte la couverture, mais les juxtaposer sans réentraînement (brique 4) ne donne presque aucun gain. C'est en entraînant le modèle directement sur les prompts du RAG hybride que la combinaison devient efficace : +0,07 de similarité moyenne par rapport au fine-tuning seul (0,727 contre 0,656) et un F1 crisp de 0,410 sur `broader`, contre 0,239.

**Rattachement au thésaurus.** Pour cette tâche, le modèle fine-tuné donne déjà de très bons résultats, et la combinaison HyRAG-FT avec 1 exemple en est très proche : 0,913 de similarité moyenne et 77,2 % de titres quasi identiques, contre 0,917 et 80,7 % pour le fine-tuning seul. Elle fait même mieux pour les concepts réduits à leur `prefLabel`. Une brique 5 n'a donc pas été nécessaire pour le rattachement, et c'est HyRAG-FT qui est retenu, car il permet à l'utilisateur de voir et de valider le contexte avant la soumission au modèle.

**Choix du modèle.** Mistral-7B est retenu pour les deux tâches : il obtient les meilleurs résultats en brique 5 et pour le rattachement, ainsi que la meilleure validation loss à l'entraînement. Llama-3.1-8B reste une alternative proche, en particulier avec la brique 4, tandis que Qwen2.5-7B est en retrait dans presque tous les tests.

**Solution retenue.** La meilleure approche pour TAC est la combinaison HyRAG-FT pour les deux tâches, intégrée dans l'agent TAC : la brique 5 pour la génération de concepts, et le modèle thésaurus fine-tuné avec le contexte du HyRAG pour le rattachement. Au lieu d'afficher un prompt construit de manière arbitraire, l'agent utilise le RAG hybride pour créer le prompt à partir des exemples et des relations les plus proches ; ce prompt est montré à l'utilisateur, qui peut le vérifier ou le corriger, puis il devient l'entrée du modèle fine-tuné. L'utilisateur valide enfin le résultat avant l'enregistrement dans OpenTheso. L'agent oriente chaque requête vers la bonne étape et choisit la base vectorielle, les relations et le modèle fine-tuné adaptés (section 5). Le modèle apporte la qualité de génération, le HyRAG l'ancrage dans les thésaurus existants, et le spécialiste la garantie de qualité.

**Prochaine étape.** La prochaine étape est l'alignement entre les thésaurus construits avec le LLM et les thésaurus externes (outil 3 de l'agent), afin de relier les concepts générés aux référentiels existants. L'exportation au format SKOS (outil 4) viendra ensuite compléter l'agent.