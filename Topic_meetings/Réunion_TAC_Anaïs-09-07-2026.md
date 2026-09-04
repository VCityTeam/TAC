# Point projet avec Anaïs — 17/07/2026

**Participants :** Rida, Anaïs

## Méthodologie, génération de concepts et thésaurus

Aujourd'hui, j'ai fait un point avec Anaïs sur l'avancement du projet. J'ai commencé par présenter la méthodologie : la partie génération de concepts et de thésaurus a été validée.

## Alignement

Concernant l'alignement, Anaïs a évoqué un plan : comme nous n'avons pas de données comme ArangoDB, nous allons réaliser un alignement entre OpenTheso et HSpocial, c'est-à-dire un modèle de LLM qui fait le lien entre les deux. Je suis toutefois bloqué sur ce point ; j'ai donc demandé qu'on m'envoie par email une présentation sur cet alignement afin de mieux le comprendre.

## Validation humaine et export

J'ai ensuite présenté l'étape de validation humaine et d'export, qui a été validée.

## Base de données Neo4j

J'ai présenté la base de données Neo4j. J'ai expliqué que les résultats y sont stockés afin de les conserver et de les réutiliser à l'étape suivante du modèle LLM.

Anaïs a demandé, par exemple, pourquoi nous n'avons pas utilisé autre chose, comme un modèle SKOS, puisque le format des concepts est en SKOS. En réalité, Neo4j est simplement une base de stockage qui sert à réutiliser les résultats à l'étape suivante ; le résultat final sera au format SKOS, généré par n10s pour la structure.

## Tables CRUD

J'ai ensuite présenté les tables CRUD. Une bonne idée est ressortie : dans l'opération *update*, nous ajouterons un modèle LLM qui réalisera aussi la mise à jour, y compris avec l'utilisateur. Par exemple, à l'avenir, lorsque des thésaurus seront documentés, nous l'utiliserons pour effectuer la mise à jour. Pour les autres cas, tout était bon.

## Application

J'ai présenté l'application, mais elle ne fonctionne pas — je n'en connais pas encore la cause et je suis en train de la corriger.

## Évaluation des résultats du LLM

Nous nous sommes surtout concentrés sur l'évaluation des résultats du LLM, qui est un point très important. Anaïs a proposé de créer un ensemble de thésaurus avec des termes annotés pour évaluer les résultats.

Pour l'instant, nous disposons déjà d'un résultat de RAG. Je vais commencer le fine-tuning avec Pagoda pour terminer l'entraînement. L'alignement viendra ensuite : nous procéderons étape par étape. La prochaine étape consiste à évaluer les résultats des concepts et de la génération issue du fine-tuning.
