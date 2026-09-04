**Date** : 03 Juillet 2026  
**Participants** : Rida Asri, John Samuel  
**Projet** : TAC (Thésaurus Automatisé par Curation) — FSP Patrimoine / LIRIS Lyon  

---

## Points abordés

### 1. Comparaison Neo4j vs ArangoDB

Présentation comparative des deux bases de données dans le cadre du projet TAC.

**Neo4j**
- Base orientée graphe pure
- Stockage optimisé pour le parcours de relations hiérarchiques (adjacence sans index)
- Recommandé pour la navigation SKOS (`broader` / `narrower`)
- Plugin **n10s (neosemantics)** intégré : permet l'export natif en SKOS/RDF sans script Python supplémentaire

**ArangoDB**
- Base multi-modèle (document, graphe, clé-valeur)
- Plus flexible pour le stockage de documents riches
- Moins performant pour les parcours de graphe profonds à grande échelle

**Conclusion** : Les deux bases offrent des performances similaires à l'échelle testée. Neo4j est plus rapide pour le stockage et la récupération de données de graphe volumineuses.  
→ **Neo4j retenu pour le graphe SKOS principal**  
→ **ArangoDB maintenu pour les référentiels de référence**

---

### 2. Test du pipeline RAG

- Modèle utilisé : **Mistral via Ollama** (local)
- Base de connaissances : **116 thésaurus** contenant **3 603 concepts SKOS complets**
- Source : API OpenTheso (`opentheso2.mom.fr`)
- Résultats : **satisfaisants** ✓

---

## Action assignée

| Action | Responsable | Demandé par |
|--------|-------------|-------------|
| Créer un benchmark comparatif Neo4j vs ArangoDB (stockage, traversal, export SKOS) | Rida Asri | John Samuel |

---

### 3. Fine-tuning — état d'avancement et plan d'action

**État actuel**
- Une exécution de fine-tuning a été lancée localement avec le modèle **TinyLlama/TinyLlama-1.1B-Chat-v1.0**
- L'exécution est en cours depuis **5 jours** et le temps restant estimé est trop long pour être viable sur la machine locale (GPU insuffisant — GTX 960, 4 Go VRAM)

**Plan d'action**
- Migration du fine-tuning vers le serveur **Pagouda**, recommandé par **Jay** et **Diago**
- Implémentation et exécution du fine-tuning directement sur ce serveur afin de disposer des ressources GPU nécessaires

| Élément | Détail |
|---------|--------|
| Modèle | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` |
| Statut actuel | En cours localement — non viable (trop lent) |
| Solution retenue | Serveur Pagouda |
| Recommandé par | Jay, Diago |

---

*Projet TAC — EquipEx+ ESPADON — FSP Patrimoine / LIRIS INSA Lyon*
