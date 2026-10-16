# Point avec John (16/10/2026)

Aujourd'hui, j'ai fait le point avec John. J'ai présenté la comparaison des résultats des différentes approches que j'ai mises en place, ainsi que l'architecture de l'Agent TAC.

## 1. Génération de concepts

J'ai commencé par le cas de la génération de concepts. Nous avons ajouté une nouvelle brique (**brique 5**), qui combine le GraphRAG et le fine-tuning.

- Meilleur modèle : **Mistral 7B**, avec l'approche **GraphRAG + fine-tuning**.

## 2. Rattachement des concepts aux thésaurus

La deuxième partie portait sur l'évaluation des modèles pour le rattachement des concepts aux thésaurus.

- Meilleur modèle : **Mistral 7B**, avec GraphRAG + fine-tuning comme avec le fine-tuning seul.
- La différence entre les approches est très faible (environ 0,01).

John a fait des **retours positifs** sur ce travail.

## 3. Architecture globale de l'Agent TAC

J'ai ensuite présenté en détail l'architecture globale de l'Agent TAC.

Remarque de John sur le **workflow** :

- Comme le nombre de concepts traités est important, l'étape de validation du résultat produit par le LLM n'est pas nécessaire.
- Cette étape sera donc supprimée : le résultat sera stocké **directement dans OpenTheso**.
- Une option pourra éventuellement être ajoutée pour permettre à l'utilisateur de valider avant l'enregistrement.

## 4. Conférence à Florence (Italie)

Nous avons discuté de la présentation du projet TAC à la conférence de Florence (financement, déplacement, etc.).

- John m'a demandé d'obtenir l'accord d'Emmanuel pour la mission à l'étranger.
- Violette m'a indiqué par e-mail qu'elle se charge de contacter Emmanuel pour l'accord.
- Les frais sont financés par **Teatime**.
- Aucune action de ma part n'est nécessaire sur ce point.

## 5. Autres conférences et article

Nous avons parlé de la participation à des conférences et de la rédaction d'un article pour présenter ce travail.

- John va m'envoyer par e-mail une liste de conférences.
- Je choisirai celle qui convient le mieux.

## Prochaines étapes (semaine prochaine)

- [ ] Finaliser la documentation des deux étapes : génération de concepts et rattachement aux thésaurus.
- [ ] Commencer le développement de la troisième approche de l'Agent TAC : l'**alignement avec des thésaurus externes**.
  - Relations déjà en place : `skos:broader`, `skos:narrower`.
  - Relations à traiter : `skos:exactMatch`, `skos:closeMatch`, etc.
