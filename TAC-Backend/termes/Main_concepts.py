import sys
sys.path.append("../")
from DataBase import get_session
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


class TermeRef(BaseModel):
    id: str
    label: str


class GenerateBatchRequest(BaseModel):
    termes: List[TermeRef]
    prompt_template: Optional[str] = None


@app.get("/concepts/generate")
def generate_concept(terme_id: str, terme_label: str):
    prompt = generate_prompt(terme_label)

    response = requests.post("http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
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
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
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


@app.post("/concepts/validate")
def validate_concept(concept: ConceptValide):
    with get_session() as session:
        id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        session.run("""
            MATCH (t:Terme {id: $terme_id})
            CREATE (c:Concept {
                id: $id,
                prefLabel: $prefLabel,
                definition: $definition,
                altLabel: $altLabel,
                broader: $broader,
                narrower: $narrower,
                model_id: $model_id,
                prompt_id: $prompt_id,
                iteration: $iteration,
                validated_by: $validated_by,
                validated_at: $validated_at,
                statut: 'validé'
            })
            CREATE (t)-[:A_CONCEPT]->(c)
            SET t.statut = 'validé'
        """,
            terme_id=concept.terme_id, id=id,
            prefLabel=concept.prefLabel,
            definition=concept.definition,
            altLabel=concept.altLabel,
            broader=concept.broader,
            narrower=concept.narrower,
            model_id=concept.model_id,
            prompt_id=concept.prompt_id,
            iteration=concept.iteration,
            validated_by=concept.validated_by,
            validated_at=now
        )
        
    return {"message": "Concept validé et sauvegardé", "id": id}


@app.post("/concepts/reject")
def reject_concept(terme_id: str, iteration: int):
    with get_session() as session:
        session.run("""
            MATCH (t:Terme {id: $terme_id})
            SET t.iteration = $iteration
        """, terme_id=terme_id, iteration=iteration + 1)
    return {"message": "Concept rejeté", "prochaine_iteration": iteration + 1}


@app.get("/concepts")
def get_concepts():
    with get_session() as session:
        result = session.run("""
            MATCH (t:Terme)-[:A_CONCEPT]->(c:Concept)
            RETURN t.label AS terme, c.id AS id,
                   c.prefLabel AS prefLabel, c.definition AS definition,
                   c.altLabel AS altLabel, c.broader AS broader,
                   c.narrower AS narrower, c.statut AS statut,
                   c.validated_by AS validated_by,
                   c.validated_at AS validated_at,
                   c.model_id AS model_id,
                   c.prompt_id AS prompt_id,
                   c.iteration AS iteration
        """)
        concepts = [dict(r) for r in result]
    return {"concepts": concepts}


@app.patch("/concepts/{id}")
def update_concept(id: str, concept: ConceptValide):
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run("""
            MATCH (c:Concept {id: $id})
            SET c.prefLabel = $prefLabel,
                c.definition = $definition,
                c.altLabel = $altLabel,
                c.broader = $broader,
                c.narrower = $narrower,
                c.updated_at = $updated_at
        """,
            id=id, prefLabel=concept.prefLabel,
            definition=concept.definition, altLabel=concept.altLabel,
            broader=concept.broader, narrower=concept.narrower,
            updated_at=now
        )
    return {"message": "Concept modifié", "id": id}


@app.delete("/concepts/{id}")
def delete_concept(id: str):
    with get_session() as session:
        session.run("""
            MATCH (t:Terme)-[:A_CONCEPT]->(c:Concept {id: $id})
            SET t.statut = 'en attente'
        """, id=id)
        session.run("MATCH (c:Concept {id: $id}) DETACH DELETE c", id=id)
    return {"message": f"Concept {id} supprimé"}


@app.delete("/concepts")
def delete_all_concepts():
    with get_session() as session:
        session.run("MATCH (c:Concept) DETACH DELETE c")
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

@app.patch("/concepts/{id}")
def update_concept(id: str, data: dict):
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run("""
            MATCH (c:Concept {id: $id})
            SET c.prefLabel = $prefLabel,
                c.definition = $definition,
                c.altLabel = $altLabel,
                c.broader = $broader,
                c.narrower = $narrower,
                c.updated_at = $updated_at
        """,
            id=id,
            prefLabel=data.get("prefLabel"),
            definition=data.get("definition"),
            altLabel=data.get("altLabel"),
            broader=data.get("broader"),
            narrower=data.get("narrower"),
            updated_at=now
        )
    return {"message": "Concept modifié", "id": id}

def parse_concept(text: str) -> dict:
    lines = text.strip().split("\n")
    result = {
        "prefLabel": "",
        "definition": "",
        "altLabel": "",
        "broader": "",
        "narrower": ""
    }
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