# Compte rendu du point avec John (09/10/2026)

## Contexte

Aujourd'hui, j'ai fait un point avec John, environ 15 jours après le précédent. J'avais demandé à reporter la réunion à cette semaine, car le fine-tuning des thésaurus prend beaucoup de temps : nous avons 18 fine-tunings (3 modèles et 5 briques), et chacun prend entre 3 et 6 heures. Ce report m'a permis de présenter l'ensemble des résultats.

La présentation faite aujourd'hui était longue (environ 66 slides).

## 1. Fine-tuning pour le rattachement aux thésaurus

- Présentation du fine-tuning pour le cas du rattachement aux thésaurus, avec 5 briques.
- Extraction des données à partir d'Opentheso : **344 thésaurus** et **407 761 concepts**.
- Évaluation par calcul de similarité.
- Sélection de termes spécialisés dans le patrimoine pour bien illustrer les résultats.

**Conclusion avec John** : d'après les résultats, le meilleur modèle est **Mistral avec la brique 4**.

**Demande de John** : sélectionner d'autres exemples liés au patrimoine pour mieux comprendre les résultats.

## 2. Architecture Graph RAG

- Présentation de l'architecture Graph RAG :
  - la base vectorielle des concepts ;
  - la base vectorielle des thésaurus ;
  - le graphe de connaissances.
- Présentation des métadonnées et du document.
- Présentation du retriever (méthode de récupération des données à partir des bases vectorielles) et des améliorations apportées au retriever pour les bases de thésaurus et de concepts.

Les résultats obtenus avec le Graph RAG sont bons.

**Question de John** : pourquoi utiliser le Graph RAG et le fine-tuning plutôt qu'une simple base de données ?

**Réponse** : une base de données récupère les informations par correspondance exacte (même terme), alors que le Graph RAG récupère par similarité, et le fine-tuning permet de générer de nouveaux concepts.

John a demandé d'ajouter cette justification à la présentation pour bien montrer le rôle de chaque approche.

## 3. Comparaison Graph RAG et fine-tuning

Nous avons présenté la comparaison des résultats entre :

- le Graph RAG et le fine-tuning ;
- la combinaison Graph RAG + fine-tuning.

Je préfère la combinaison. Comme discuté en réunion, le fonctionnement serait le suivant :

1. Le Graph RAG sert uniquement à générer un contexte, présenté sous forme de prompt.
2. Ce prompt est affiché à l'utilisateur, qui peut le modifier ou le valider.
3. Le prompt est envoyé vers un modèle LLM fine-tuné (concepts ou thésaurus), qui génère la réponse.

Lors de la dernière réunion d'équipe, nous avions constaté que le prompt était généré de manière arbitraire. Avec cette méthode, à partir de la requête de l'utilisateur, nous créons des prompts contenant des exemples récupérés par le Graph RAG.

Le meilleur modèle fine-tuné est **Mistral brique 4**, pour les concepts comme pour les thésaurus. Le format du dataset de la brique 4 contient des exemples : si l'on choisit de bons exemples, qu'on les place dans le prompt et qu'on les donne au modèle brique 4, on obtient de bons résultats.

## 4. Architecture finale : l'Agent TAC

À partir de la comparaison des benchmarks, nous avons conclu que l'architecture finale est l'**Agent TAC**.

Un agent est un **LLM + des actions** : un modèle de langage capable d'agir, par exemple en se connectant à des bases externes ou à Gmail pour répondre à une question de l'utilisateur.

L'Agent TAC est relié à **quatre outils** :

1. Génération de concepts
2. Rattachement de concepts aux thésaurus
3. Alignement
4. Format SKOS

Point essentiel : l'agent détecte la demande de l'utilisateur et se connecte à l'outil adapté en fonction de la requête.

## 5. Synthèse des 6 derniers mois

John a demandé une synthèse de tout ce qui a été fait depuis 6 mois, pour faciliter la compréhension par les membres de l'équipe.

- La documentation du projet est déjà commencée et presque terminée.
- Je ferai un point avec John à partir de la semaine prochaine pour la création de cette synthèse (par exemple : toutes les présentations, la documentation, etc.).

## 6. Prochaines étapes (semaine prochaine)

Je présenterai :

- [ ] Graph RAG vs fine-tuning
- [ ] Graph RAG + fine-tuning vs fine-tuning
- [ ] Graph RAG vs fine-tuning + Graph RAG
- [ ] Poursuite du développement de l'Agent TAC

## 7. Conférence à Florence

Hier, Violette m'a proposé de partir avec elle, Anaïs, Amine et Marwan à Florence pour une conférence. C'est une très bonne opportunité pour présenter l'outil TAC.

**Actions :**

- [ ] Envoyer un email à Violette pour savoir quel financement couvre ce voyage (demande de John).
- [ ] Envoyer ensuite un email à Emmanuelle, directrice de la Fondation, pour obtenir l'accord pour une mission à l'étranger.
