# TAC
Thesaurus Automation Curation

## Team
- Olivier Malavergne
- Violette Abergel
- Anaïs Guillem
- Kévin Reby
- Miled Rousset
- Rida Asri
- John Samuel
- Gilles Gesquière

## Le projet TAC (Thésaurus Automatisé par Curation)

L'objectif de TAC est de créer un **outil facilitant la documentation et la structuration de vocabulaires spécialisés pour le patrimoine culturel**, en s'appuyant à la fois sur les pratiques documentaires des institutions patrimoniales et sur les grands modèles de langage (LLMs).

Intégré à l'écosystème ESPADON, l'outil vise le versement et l'agrégation automatisée de vocabulaires vers le gestionnaire de thésaurus **Opentheso**. Plus précisément, il s'agit de faciliter la création de thésaurus à partir de listes de termes non structurées, en automatisant les étapes essentielles : **curation, définition, structuration et alignement de concepts**.

## La mission

L'outil TAC se compose de deux briques :

- **Un microservice** s'appuyant sur un LLM pour assurer automatiquement la curation, la structuration et l'alignement de concepts issus de listes d'autorité vers des référentiels terminologiques exposés en **SKOS** via Opentheso.
- **Une interface web** permettant aux utilisateurs de valider et corriger les résultats obtenus avant de les exporter et/ou de les soumettre à Opentheso via son API.

Le principe de fonctionnement : un utilisateur envoie une liste de termes non structurée ; celle-ci est traitée automatiquement par étapes (classification des termes, extraction des définitions, formalisation SKOS) pour aboutir à l'alignement avec les thésaurus pré-existants. L'outil est conteneurisé avec Docker et déployé dans l'écosystème ESPADON.

## Les trois phases du projet

1. **De l'expérimentation au cahier des charges** (2 mois) : dans la continuité de l'expérimentation **LLMtheso**, définition des cas d'usage, évaluation des prompts, tests RAG et fine-tuning, puis rédaction du cahier des charges.
2. **Développement de l'outil TAC** (6 mois) : développement de l'API et de l'interface utilisateur, avec documentation en vue de son ouverture.
3. **Évaluation, débogage, déploiement et diffusion** (4 mois) : cycles de tests, déploiement sur les serveurs ESPADON, communication et publication des résultats en open science.

## Cadre et collaboration

Le poste s'inscrit dans un **consortium national** (FSP, CNRS, ministère de la Culture, universités), avec des plateformes instrumentales, des laboratoires SHS et un WP Data fournissant stockage, calcul et gestion des données. L'ingénieur interagit avec la direction scientifique, les développeurs et les partenaires (laboratoires de recherche et institutions patrimoniales). Le travail se déroule au **LIRIS à Lyon**, dans un cadre open science.

## Origine

Le projet s'inscrit dans la lignée de **LLMtheso** (Guillem et al., 2025), preuve de concept neuro-symbolique qui a traité environ 13 000 termes bruts du patrimoine (LRMH) en thésaurus structuré, fondant l'approche que TAC vise à généraliser et industrialiser.
