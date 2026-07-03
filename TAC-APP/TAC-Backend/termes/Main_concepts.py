import sys
sys.path.append("../")
from DataBase import get_arango_db

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConceptValide(BaseModel):
    terme_id: str
    prefLabel: str
    definition: str
    altLabel: str
    broader: str
    narrower: str
    model_id: str
    prompt_id: str
    iteration: int
    validated_by: str


class ConceptUpdate(BaseModel):
    prefLabel: Optional[str] = None
    definition: Optional[str] = None
    altLabel: Optional[str] = None
    broader: Optional[str] = None
    narrower: Optional[str] = None


class ConceptRejet(BaseModel):
    terme_id: str
    prefLabel: str
    definition: str
    altLabel: str
    broader: str
    narrower: str
    model_id: str
    prompt_id: str
    iteration: int


class TermeRef(BaseModel):
    id: str
    label: str


class GenerateBatchRequest(BaseModel):
    termes: List[TermeRef]
    prompt_template: Optional[str] = None


class ConceptManuel(BaseModel):
    terme: str
    prefLabel: Optional[str] = ""
    definition: Optional[str] = ""
    altLabel: Optional[str] = ""
    broader: Optional[str] = ""
    narrower: Optional[str] = ""
    validated_by: str


@app.get("/concepts/generate")
def generate_concept(terme_id: str, terme_label: str):
    prompt = generate_prompt(terme_label)
    response = requests.post("http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    result = response.json()["response"]
    parsed = parse_concept(result)
    return {
        "terme_id": terme_id,
        "model_id": "mistral:7b",
        "prompt_id": "prompt_v2_few_shot",
        "iteration": 1,
        "prefLabel": terme_label,
        "definition": parsed["definition"],
        "altLabel": parsed["altLabel"],
        "broader": parsed["broader"],
        "narrower": parsed["narrower"]
    }


@app.get("/concepts/prompt")
def get_default_prompt():
    return {"prompt_template": DEFAULT_PROMPT_TEMPLATE}


@app.post("/concepts/generate-batch")
def generate_concepts_batch(payload: GenerateBatchRequest):
    template = payload.prompt_template or DEFAULT_PROMPT_TEMPLATE
    concepts = []
    for terme in payload.termes:
        prompt = template.format(terme=terme.label)
        response = requests.post("http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        result = response.json()["response"]
        parsed = parse_concept(result)
        concepts.append({
            "terme_id": terme.id,
            "model_id": "mistral:7b",
            "prompt_id": "prompt_custom" if payload.prompt_template else "prompt_v2_few_shot",
            "iteration": 1,
            "prefLabel": terme.label,
            "definition": parsed["definition"],
            "altLabel": parsed["altLabel"],
            "broader": parsed["broader"],
            "narrower": parsed["narrower"]
        })
    return {"concepts": concepts}


@app.post("/concepts/manuel")
def create_concept_manuel(concept: ConceptManuel):
    terme_id = str(uuid.uuid4())[:8]
    concept_id = str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    label = concept.terme.strip()
    prefLabel = concept.prefLabel.strip() if concept.prefLabel else label

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("""
    #         MERGE (t:Terme {label: $label})
    #         ON CREATE SET t.id = $terme_id, t.statut = 'validé', t.source = 'manuel', t.created_at = $now
    #         ON MATCH SET t.statut = 'validé'
    #         WITH t
    #         CREATE (c:Concept {
    #             id: $concept_id, prefLabel: $prefLabel, definition: $definition,
    #             altLabel: $altLabel, broader: $broader, narrower: $narrower,
    #             model_id: 'manuel', prompt_id: 'manuel', iteration: 0,
    #             validated_by: $validated_by, validated_at: $now, statut: 'validé'
    #         })
    #         CREATE (t)-[:A_CONCEPT]->(c)
    #     """, label=label, terme_id=terme_id, concept_id=concept_id,
    #         prefLabel=prefLabel, definition=concept.definition or "",
    #         altLabel=concept.altLabel or "", broader=concept.broader or "",
    #         narrower=concept.narrower or "", validated_by=concept.validated_by, now=now)

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute("""
        UPSERT {label: @label}
          INSERT {id: @terme_id, label: @label, statut: 'validé', source: 'manuel', created_at: @now}
          UPDATE {statut: 'validé'}
          IN Termes
        RETURN NEW
    """, bind_vars={"label": label, "terme_id": terme_id, "now": now})
    terme_docs = list(cursor)
    t_cursor = db.aql.execute("FOR t IN Termes FILTER t.label == @label RETURN t", bind_vars={"label": label})
    termes = list(t_cursor)
    terme = termes[0]

    meta = db.collection("Concepts").insert({
        "id": concept_id, "prefLabel": prefLabel,
        "definition": concept.definition or "",
        "altLabel": concept.altLabel or "",
        "broader": concept.broader or "",
        "narrower": concept.narrower or "",
        "model_id": "manuel", "prompt_id": "manuel", "iteration": 0,
        "validated_by": concept.validated_by, "validated_at": now, "statut": "validé"
    })
    db.collection("TermeConcept").insert({"_from": terme["_id"], "_to": meta["_id"]})

    return {"message": "Concept créé manuellement", "id": concept_id}


@app.post("/concepts/validate")
def validate_concept(concept: ConceptValide):
    id = str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("""
    #         MATCH (t:Terme {id: $terme_id})
    #         CREATE (c:Concept {
    #             id: $id, prefLabel: $prefLabel, definition: $definition,
    #             altLabel: $altLabel, broader: $broader, narrower: $narrower,
    #             model_id: $model_id, prompt_id: $prompt_id, iteration: $iteration,
    #             validated_by: $validated_by, validated_at: $validated_at, statut: 'validé'
    #         })
    #         CREATE (t)-[:A_CONCEPT]->(c)
    #         SET t.statut = 'validé'
    #     """, terme_id=concept.terme_id, id=id, prefLabel=concept.prefLabel,
    #         definition=concept.definition, altLabel=concept.altLabel,
    #         broader=concept.broader, narrower=concept.narrower,
    #         model_id=concept.model_id, prompt_id=concept.prompt_id,
    #         iteration=concept.iteration, validated_by=concept.validated_by, validated_at=now)

    # ---- ARANGODB ----
    db = get_arango_db()
    t_cursor = db.aql.execute("FOR t IN Termes FILTER t.id == @id RETURN t", bind_vars={"id": concept.terme_id})
    termes = list(t_cursor)
    if not termes:
        raise HTTPException(status_code=404, detail="Terme non trouvé")
    terme = termes[0]

    meta = db.collection("Concepts").insert({
        "id": id, "prefLabel": concept.prefLabel,
        "definition": concept.definition, "altLabel": concept.altLabel,
        "broader": concept.broader, "narrower": concept.narrower,
        "model_id": concept.model_id, "prompt_id": concept.prompt_id,
        "iteration": concept.iteration, "validated_by": concept.validated_by,
        "validated_at": now, "statut": "validé"
    })
    db.collection("TermeConcept").insert({"_from": terme["_id"], "_to": meta["_id"]})
   
    db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id UPDATE t WITH {statut: 'validé'} IN Termes",
        bind_vars={"id": concept.terme_id}
    )

    return {"message": "Concept validé et sauvegardé", "id": id}


@app.post("/concepts/reject")
def reject_concept(concept: ConceptRejet):
    id = str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("""
    #         MATCH (t:Terme {id: $terme_id})
    #         CREATE (c:Concept {
    #             id: $id, prefLabel: $prefLabel, definition: $definition,
    #             altLabel: $altLabel, broader: $broader, narrower: $narrower,
    #             model_id: $model_id, prompt_id: $prompt_id, iteration: $iteration,
    #             validated_at: $validated_at, statut: 'rejeté'
    #         })
    #         CREATE (t)-[:A_CONCEPT]->(c)
    #         SET t.iteration = $next_iteration
    #     """, terme_id=concept.terme_id, id=id, prefLabel=concept.prefLabel,
    #         definition=concept.definition, altLabel=concept.altLabel,
    #         broader=concept.broader, narrower=concept.narrower,
    #         model_id=concept.model_id, prompt_id=concept.prompt_id,
    #         iteration=concept.iteration, validated_at=now,
    #         next_iteration=concept.iteration + 1)

    # ---- ARANGODB ----
    db = get_arango_db()
    t_cursor = db.aql.execute("FOR t IN Termes FILTER t.id == @id RETURN t", bind_vars={"id": concept.terme_id})
    termes = list(t_cursor)
    if not termes:
        raise HTTPException(status_code=404, detail="Terme non trouvé")
    terme = termes[0]

    meta = db.collection("Concepts").insert({
        "id": id, "prefLabel": concept.prefLabel,
        "definition": concept.definition, "altLabel": concept.altLabel,
        "broader": concept.broader, "narrower": concept.narrower,
        "model_id": concept.model_id, "prompt_id": concept.prompt_id,
        "iteration": concept.iteration, "validated_at": now, "statut": "rejeté"
    })
    db.collection("TermeConcept").insert({"_from": terme["_id"], "_to": meta["_id"]})
    db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id UPDATE t WITH {iteration: @next} IN Termes",
        bind_vars={"id": concept.terme_id, "next": concept.iteration + 1}
    )

    return {"message": "Concept rejeté", "id": id, "prochaine_iteration": concept.iteration + 1}


@app.get("/concepts")
def get_concepts():
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run("""
    #         MATCH (t:Terme)-[:A_CONCEPT]->(c:Concept)
    #         RETURN t.label AS terme, c.id AS id,
    #                c.prefLabel AS prefLabel, c.definition AS definition,
    #                c.altLabel AS altLabel, c.broader AS broader,
    #                c.narrower AS narrower, c.statut AS statut,
    #                c.validated_by AS validated_by, c.validated_at AS validated_at,
    #                c.model_id AS model_id, c.prompt_id AS prompt_id, c.iteration AS iteration
    #     """)
    #     concepts = [dict(r) for r in result]

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute("""
        FOR t IN Termes
          FOR c IN 1..1 OUTBOUND t TermeConcept
          RETURN {
            terme: t.label, id: c.id, prefLabel: c.prefLabel,
            definition: c.definition, altLabel: c.altLabel,
            broader: c.broader, narrower: c.narrower, statut: c.statut,
            validated_by: c.validated_by, validated_at: c.validated_at,
            model_id: c.model_id, prompt_id: c.prompt_id, iteration: c.iteration
          }
    """)
    concepts = list(cursor)

    return {"concepts": concepts}


@app.patch("/concepts/{id}")
def update_concept(id: str, concept: ConceptUpdate):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("""
    #         MATCH (c:Concept {id: $id})
    #         SET c.prefLabel = $prefLabel, c.definition = $definition,
    #             c.altLabel = $altLabel, c.broader = $broader,
    #             c.narrower = $narrower, c.updated_at = $updated_at
    #     """, id=id, prefLabel=concept.prefLabel, definition=concept.definition,
    #         altLabel=concept.altLabel, broader=concept.broader,
    #         narrower=concept.narrower, updated_at=now)

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute("""
        FOR c IN Concepts FILTER c.id == @id
          UPDATE c WITH {
            prefLabel: @prefLabel, definition: @definition,
            altLabel: @altLabel, broader: @broader,
            narrower: @narrower, updated_at: @now
          } IN Concepts
    """, bind_vars={
        "id": id, "prefLabel": concept.prefLabel, "definition": concept.definition,
        "altLabel": concept.altLabel, "broader": concept.broader,
        "narrower": concept.narrower, "now": now
    })

    return {"message": "Concept modifié", "id": id}


@app.delete("/concepts/{id}")
def delete_concept(id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("""
    #         MATCH (t:Terme)-[:A_CONCEPT]->(c:Concept {id: $id})
    #         SET t.statut = 'en attente'
    #     """, id=id)
    #     session.run("MATCH (c:Concept {id: $id}) DETACH DELETE c", id=id)

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute("""
        FOR c IN Concepts FILTER c.id == @id
          FOR t IN 1..1 INBOUND c TermeConcept
          UPDATE t WITH {statut: 'en attente'} IN Termes
    """, bind_vars={"id": id})
    db.aql.execute("""
        FOR c IN Concepts FILTER c.id == @id
          FOR e IN TermeConcept FILTER e._to == c._id
          REMOVE e IN TermeConcept
    """, bind_vars={"id": id})
    db.aql.execute("""
        FOR c IN Concepts FILTER c.id == @id
          FOR e IN ConceptThesaurus FILTER e._from == c._id
          REMOVE e IN ConceptThesaurus
    """, bind_vars={"id": id})
    db.aql.execute("FOR c IN Concepts FILTER c.id == @id REMOVE c IN Concepts", bind_vars={"id": id})

    return {"message": f"Concept {id} supprimé"}


@app.delete("/concepts")
def delete_all_concepts():
    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("MATCH (c:Concept) DETACH DELETE c")

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute("FOR e IN TermeConcept REMOVE e IN TermeConcept")
    db.aql.execute("FOR e IN ConceptThesaurus REMOVE e IN ConceptThesaurus")
    db.aql.execute("FOR e IN ConceptAlignement REMOVE e IN ConceptAlignement")
    db.aql.execute("FOR c IN Concepts REMOVE c IN Concepts")

    return {"message": "Tous les concepts supprimés"}


DEFAULT_PROMPT_TEMPLATE = """
        Tu es un expert en thésaurus pour le patrimoine culturel (SKOS).
        Réponds UNIQUEMENT en français, UNIQUEMENT sous forme de liste structurée.
        N'ajoute aucune explication, introduction ou commentaire.

        Règles strictes :
        - Définition : une seule phrase concise et générale (max 20 mots)
        - Termes alternatifs : 2 à 3 synonymes directs UNIQUEMENT, séparés par des virgules
        - Concept plus large : 1 seul concept parent direct, le plus proche
        - Concepts plus spécifiques : 3 à 5 types simples et génériques, séparés par des virgules
        - Concepts associés : 3 à 4 domaines ou disciplines liés, séparés par des virgules

        Exemples :

        ### Exemple 1 :
        Terme : "Peinture"
        1. Définition : Art d'appliquer des pigments sur une surface pour créer une œuvre visuelle.
        2. Termes alternatifs : art pictural, œuvre picturale
        3. Concept plus large : art visuel
        4. Concepts plus spécifiques : aquarelle, fresque, gouache, pastel, tempera
        5. Concepts associés : dessin, pigment, histoire de l'art, couleur

        ### Exemple 2 :
        Terme : "Sculpture"
        1. Définition : Art de créer des formes en trois dimensions à partir de matériaux solides.
        2. Termes alternatifs : art plastique, œuvre sculpturale
        3. Concept plus large : art visuel
        4. Concepts plus spécifiques : bas-relief, ronde-bosse, haut-relief, stèle
        5. Concepts associés : modelage, taille, fonte, histoire de l'art

        ### Exemple 3 :
        Terme : "Manuscrit"
        1. Définition : Document écrit à la main produit avant l'invention de l'imprimerie.
        2. Termes alternatifs : document manuscrit, texte autographe
        3. Concept plus large : patrimoine écrit
        4. Concepts plus spécifiques : codex, rouleau, parchemin, papyrus
        5. Concepts associés : calligraphie, enluminure, paléographie, archivistique

        ### Exemple 4 :
        Terme : "Château"
        1. Définition : Édifice fortifié servant de résidence seigneuriale ou royale.
        2. Termes alternatifs : demeure seigneuriale, forteresse résidentielle
        3. Concept plus large : architecture défensive
        4. Concepts plus spécifiques : donjon, bastide, manoir, palais
        5. Concepts associés : fortification, patrimoine bâti, histoire médiévale, archéologie

        ─────────────────────────────────────
        Maintenant applique le même modèle pour :

        Terme : "{terme}"
        1. Définition :
        2. Termes alternatifs :
        3. Concept plus large :
        4. Concepts plus spécifiques :
        5. Concepts associés :
        """


def generate_prompt(terme: str) -> str:
    return DEFAULT_PROMPT_TEMPLATE.format(terme=terme)

def parse_concept(text: str) -> dict:
    lines = text.strip().split("\n")
    result = {"prefLabel": "", "definition": "", "altLabel": "", "broader": "", "narrower": ""}
    for line in lines:
        line = line.strip()
        if line.startswith("1."):
            result["definition"] = line.split(":", 1)[-1].strip()
        elif line.startswith("2."):
            result["altLabel"] = line.split(":", 1)[-1].strip()
        elif line.startswith("3."):
            result["broader"] = line.split(":", 1)[-1].strip()
        elif line.startswith("4."):
            result["narrower"] = line.split(":", 1)[-1].strip()
    return result
