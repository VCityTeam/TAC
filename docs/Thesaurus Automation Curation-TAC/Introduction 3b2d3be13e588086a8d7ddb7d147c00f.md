# Introduction

---

<aside>
📋

- **Plan**
</aside>

---

## Le projet

L'objectif de TAC est de créer un **outil facilitant la documentation et la structuration de vocabulaires spécialisés pour le patrimoine culturel**, en s'appuyant à la fois sur les pratiques documentaires des institutions patrimoniales et sur les grands modèles de langage (LLM).

Intégré à l'écosystème ESPADON, l'outil vise à automatiser le versement et l'agrégation de vocabulaires vers le gestionnaire de thésaurus **Opentheso**. Plus précisément, il s'agit de faciliter la création de thésaurus à partir de listes de termes non structurées, en automatisant les étapes essentielles : **curation, définition, structuration et alignement de concepts**.

## La mission

L'outil TAC se compose de deux briques :

- **Un microservice** s'appuyant sur un LLM pour assurer automatiquement la curation, la structuration et l'alignement de concepts issus de listes d'autorité vers des référentiels terminologiques exposés en **SKOS** via Opentheso.
- **Une interface web** permettant aux utilisateurs de valider et de corriger les résultats obtenus avant de les exporter ou de les soumettre à Opentheso via son API.

Le principe de fonctionnement est le suivant : l'utilisateur envoie une liste de termes non structurée, qui est traitée automatiquement par étapes successives, classification des termes, extraction des définitions, formalisation SKOS, pour aboutir à l'alignement avec les thésaurus préexistants. L'outil est conteneurisé avec Docker et déployé dans l'écosystème ESPADON.

## Les trois phases du projet

1. **De l'expérimentation au cahier des charges** *(2 mois)* — Dans la continuité de l'expérimentation **LLMtheso** : définition des cas d'usage, évaluation des prompts, tests de RAG et de fine-tuning, puis rédaction du cahier des charges.
2. **Développement de l'outil TAC** *(6 mois)* — Développement de l'API et de l'interface utilisateur, accompagné d'une documentation en vue de son ouverture.
3. **Évaluation, débogage, déploiement et diffusion** *(4 mois)* — Cycles de tests, déploiement sur les serveurs ESPADON, communication et publication des résultats en science ouverte.

## Cadre et collaboration

Le projet s'inscrit dans un **consortium national** réunissant la Fondation des Sciences du Patrimoine, le CNRS, le ministère de la Culture et plusieurs universités. Il mobilise des plateformes instrumentales, des laboratoires en sciences humaines et sociales, ainsi qu'un lot de travail *Data* fournissant le stockage, le calcul et la gestion des données.

Le travail se déroule au **LIRIS, à Lyon**, dans un cadre de science ouverte, en interaction avec la direction scientifique, les développeurs et les partenaires, laboratoires de recherche et institutions patrimoniales.

## Origine

Le projet s'inscrit dans la lignée de **LLMtheso** (Guillem et al., 2025), une preuve de concept neuro-symbolique ayant permis de transformer environ 13 000 termes bruts issus du patrimoine — provenant du Laboratoire de recherche des monuments historiques (LRMH) — en un thésaurus structuré. C'est cette approche que TAC vise à généraliser et à industrialiser.