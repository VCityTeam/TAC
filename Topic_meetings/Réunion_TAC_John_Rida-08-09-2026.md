# Compte rendu de réunion, mardi 8 septembre 2026

**Participants :** Rida Asri, John Samuel
**Note :** réunion initialement prévue vendredi dernier, reportée à aujourd'hui.

## 1. Fine-tuning et jeux de prompts

Nous avons discuté des exemples d'entraînement du fine-tuning avec la nouvelle version.

- Utilisation de patterns pour améliorer les prompts.
- Création de **5 exemples de prompts** servant à entraîner le modèle.
- Objectif : tester plusieurs cas de figure et vérifier que le LLM comprend réellement la tâche au lieu de la mémoriser.
- Fine-tuning réalisé sur trois modèles : **Llama**, **Mistral** et **Qwen**.

**Demande de John :** réaliser un fine-tuning séparé pour chaque exemple de prompt, puis effectuer la comparaison. C'est le point à présenter vendredi prochain.

## 2. Graph RAG et évaluation

- Présentation de l'architecture du **Graph RAG**.
- Évaluation de base sur les concepts : résultats très bons.
- Métriques utilisées : **Hit@1**, **Hit@5** et **MRR**.
- Les scénarios de test ont été construits via l'**API Gemini** (gratuite).

**Remarque de John :** il serait préférable de travailler avec des modèles LLM plus petits et plus simples. Proposition : **Gemma**, modèle de la famille Gemini.

## 3. Choix de l'approche

La décision sur l'approche à retenir est repoussée jusqu'à la finalisation des trois pistes :

1. Fine-tuning seul
2. Graph RAG seul
3. Graph RAG combiné au fine-tuning

## 4. Publication

Discussion sur la publication et le choix de la revue. Si la bonne cible est identifiée parmi les revues ou les conférences, il faut commencer dès maintenant la rédaction de l'article ou la soumission, car les procédures prennent du temps.

## 5. Documentation du travail

John demande également de rédiger et de conserver l'ensemble du travail dans un document unique, l'avancement étant déjà important et le nombre de travaux réalisés conséquent.

Actuellement, tout est consigné dans une page Notion. Le problème est que le partage avec les autres membres nécessite de passer à la version payante de Notion. Pour cette raison, je vais créer un document au format **Word ou LaTeX** regroupant l'ensemble de ces éléments.

## 6. Prochaines étapes

- [ ] Finaliser l'évaluation des autres approches
- [ ] Réaliser le fine-tuning séparément pour chaque exemple de prompt
- [ ] Préparer la comparaison des résultats pour la présentation de vendredi
- [ ] Identifier la revue ou la conférence cible
- [ ] Rassembler le contenu Notion dans un document Word ou LaTeX partageable
