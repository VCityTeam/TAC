import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from DataBase import get_session
import uuid
import json
import re
import requests
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from arango import ArangoClient

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_arango_db():
    try:
        client = ArangoClient(hosts="http://localhost:8529")
        db = client.db("_system", username="root", password="MIDvi1234!!")
        return db
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Impossible de se connecter à ArangoDB : {e}")


class Alignement(BaseModel):
    thesaurus_tac_id: str
    thesaurus_tac_nom: str
    concept_tac_id: str
    concept_tac_label: str
    type_alignement: str
    thesaurus_arango_nom: str
    concept_externe_label: str
    uri_externe: Optional[str] = ""
    source_externe: str
    validated_by: str
    statut: str

class AlignementUpdate(BaseModel):
    type_alignement: Optional[str] = None
    uri_externe: Optional[str] = None


class GenerateAlignementsRequest(BaseModel):
    thesaurus_tac_id: str
    thesaurus_arango_nom: str
    prompt_template: Optional[str] = None


DEFAULT_ALIGNEMENT_PROMPT = """Tu es un expert en alignement de thésaurus SKOS.

        Concepts du thésaurus TAC :
        {tac_text}

        Concepts du thésaurus externe ({thesaurus_arango_nom}) :
        {arango_text}

        Pour chaque concept TAC, trouve le concept externe le plus similaire sémantiquement.
        Le concept TAC "peinture" peut s'aligner avec "Fresque" ou "Tempera" car ce sont des techniques de peinture.

        Types d'alignement :
        - exactMatch : concepts identiques ou quasi-identiques
        - closeMatch : concepts très similaires ou du même domaine
        - noMatch : aucun concept externe ne correspond sémantiquement (domaines différents)

        IMPORTANT : Tu DOIS toujours retourner exactement une entrée par concept TAC, même s'il n'y a aucune correspondance.
        Dans ce cas, utilise "type_alignement": "noMatch" et laisse "concept_externe_label" vide "".
        Si l'URI est vide, mets une chaîne vide "".

        Réponds UNIQUEMENT avec ce JSON, sans texte avant ou après, sans markdown :

        [
        {{
            "concept_tac_id": "id du concept TAC",
            "concept_tac_label": "label TAC",
            "type_alignement": "exactMatch, closeMatch ou noMatch",
            "concept_externe_label": "label externe",

        }}
        ]"""


def call_ollama(prompt: str) -> str:
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=600)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama n'est pas démarré. Lance 'ollama serve' puis 'ollama pull mistral'.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama a mis trop de temps à répondre.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur Ollama : {e}")


@app.get("/alignements/arango/thesauri")
def get_arango_thesauri():
    db = get_arango_db()
    try:
        thesauri = list(db.aql.execute("FOR theso IN Thesaurus RETURN theso"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur requête ArangoDB : {e}")

    clean = []
    for t in thesauri:
        clean.append({
            "key": t.get("_key"),
            "title": t.get("title"),
            "description": t.get("description"),
            "language": t.get("language"),
            "creator": t.get("creator"),
            "concepts": t.get("concepts", [])
        })

    return {"thesauri": clean}
  
@app.get("/alignements/prompt")
def get_default_alignement_prompt():
    return {"prompt_template": DEFAULT_ALIGNEMENT_PROMPT}


@app.post("/alignements/generate")
def generate_alignements(payload: GenerateAlignementsRequest):
    thesaurus_tac_id = payload.thesaurus_tac_id
    thesaurus_arango_nom = payload.thesaurus_arango_nom

    # 1. Récupérer les concepts TAC depuis Neo4j
    try:
        with get_session() as session:
            result = session.run("""
                MATCH (c:Concept)-[:APPARTIENT_A]->(th:Thesaurus {id: $id})
                RETURN c.id AS id, c.prefLabel AS prefLabel,
                       c.altLabel AS altLabel, c.broader AS broader,
                       th.nom AS thesaurus_nom
            """, id=thesaurus_tac_id)
            concepts_tac = [dict(r) for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Neo4j : {e}")

    if not concepts_tac:
        raise HTTPException(status_code=404, detail="Aucun concept trouvé pour ce thésaurus TAC.")

    # 2. Récupérer le thésaurus ArangoDB
    db = get_arango_db()
    try:
        results = list(db.aql.execute(f"FOR doc IN Thesaurus FILTER doc.title == '{thesaurus_arango_nom}' RETURN doc"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur requête ArangoDB : {e}")

    thesaurus_arango = results[0] if results else None
    if not thesaurus_arango:
        raise HTTPException(status_code=404, detail=f"Thésaurus ArangoDB '{thesaurus_arango_nom}' non trouvé.")

    concepts_arango = thesaurus_arango.get("concepts", [])

    # 3. Construire le prompt
    tac_text = "\n".join([
        f"- ID:{c['id']} | {c['prefLabel']} | altLabel: {c.get('altLabel','')} | broader: {c.get('broader','')}"
        for c in concepts_tac
    ])
    arango_text = "\n".join([f"- {c['prefLabel']}" for c in concepts_arango])

    template = payload.prompt_template or DEFAULT_ALIGNEMENT_PROMPT
    try:
        prompt = template.format(
            tac_text=tac_text,
            arango_text=arango_text,
            thesaurus_arango_nom=thesaurus_arango_nom
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Prompt invalide — variable inconnue : {e}")

    # 4. Appeler Ollama
    raw = call_ollama(prompt)

    # 5. Parser la réponse JSON
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail=f"Gemini n'a pas retourné un JSON valide. Réponse : {raw[:300]}")
    try:
        alignements = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON Gemini malformé : {e}")

    thesaurus_nom = concepts_tac[0].get("thesaurus_nom") or thesaurus_tac_id
    for a in alignements:
        a["thesaurus_tac_id"] = thesaurus_tac_id
        a["thesaurus_tac_nom"] = thesaurus_nom
        a["thesaurus_arango_nom"] = thesaurus_arango_nom
        a["source_externe"] = thesaurus_arango.get("source", thesaurus_arango_nom)
        if a.get("type_alignement") == "noMatch":
            a["concept_externe_label"] = "Not found"

    return {"alignements": alignements}


@app.post("/alignements/validate")
def validate_alignement(alignement: Alignement):
    with get_session() as session:
        id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run("""
            MATCH (c:Concept {id: $concept_tac_id})
            CREATE (a:Alignement {
                id: $id,
                thesaurus_tac_id: $thesaurus_tac_id,
                thesaurus_tac_nom: $thesaurus_tac_nom,
                concept_tac_label: $concept_tac_label,
                type_alignement: $type_alignement,
                thesaurus_arango_nom: $thesaurus_arango_nom,
                concept_externe_label: $concept_externe_label,
                uri_externe: $uri_externe,
                source_externe: $source_externe,
                validated_by: $validated_by,
                validated_at: $validated_at,
                created_at: $created_at,
                statut: 'validé'
            })
            CREATE (c)-[:A_ALIGNEMENT]->(a)
        """,
            id=id, thesaurus_tac_id=alignement.thesaurus_tac_id,
            thesaurus_tac_nom=alignement.thesaurus_tac_nom,
            concept_tac_id=alignement.concept_tac_id,
            concept_tac_label=alignement.concept_tac_label,
            type_alignement=alignement.type_alignement,
            thesaurus_arango_nom=alignement.thesaurus_arango_nom,
            concept_externe_label=alignement.concept_externe_label,
            uri_externe=alignement.uri_externe,
            source_externe=alignement.source_externe,
            validated_by=alignement.validated_by,
            validated_at=now, created_at=now
        )
    return {"message": "Alignement validé", "id": id}


@app.post("/alignements/reject")
def reject_alignement(alignement: Alignement):
    with get_session() as session:
        id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run("""
            MATCH (c:Concept {id: $concept_tac_id})
            CREATE (a:Alignement {
                id: $id,
                thesaurus_tac_id: $thesaurus_tac_id,
                thesaurus_tac_nom: $thesaurus_tac_nom,
                concept_tac_label: $concept_tac_label,
                type_alignement: $type_alignement,
                thesaurus_arango_nom: $thesaurus_arango_nom,
                concept_externe_label: $concept_externe_label,
                uri_externe: $uri_externe,
                source_externe: $source_externe,
                validated_by: $validated_by,
                validated_at: $validated_at,
                created_at: $created_at,
                statut: 'rejeté'
            })
            CREATE (c)-[:A_ALIGNEMENT]->(a)
        """,
            id=id, thesaurus_tac_id=alignement.thesaurus_tac_id,
            thesaurus_tac_nom=alignement.thesaurus_tac_nom,
            concept_tac_id=alignement.concept_tac_id,
            concept_tac_label=alignement.concept_tac_label,
            type_alignement=alignement.type_alignement,
            thesaurus_arango_nom=alignement.thesaurus_arango_nom,
            concept_externe_label=alignement.concept_externe_label,
            uri_externe=alignement.uri_externe,
            source_externe=alignement.source_externe,
            validated_by=alignement.validated_by,
            validated_at=now, created_at=now
        )
    return {"message": "Alignement rejeté", "id": id}


@app.get("/alignements")
def get_alignements():
    with get_session() as session:
        result = session.run("""
            MATCH (c:Concept)-[:A_ALIGNEMENT]->(a:Alignement)
            RETURN a.id AS id,
                   a.thesaurus_tac_nom AS thesaurus_tac_nom,
                   a.concept_tac_label AS concept_tac_label,
                   a.type_alignement AS type_alignement,
                   a.thesaurus_arango_nom AS thesaurus_arango_nom,
                   a.concept_externe_label AS concept_externe_label,
                   a.uri_externe AS uri_externe,
                   a.source_externe AS source_externe,
                   a.statut AS statut,
                   a.validated_by AS validated_by,
                   a.validated_at AS validated_at
        """)
        alignements = [dict(r) for r in result]
    return {"alignements": alignements}


@app.patch("/alignements/{id}")
def update_alignement(id: str, data: AlignementUpdate):
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        session.run("""
            MATCH (a:Alignement {id: $id})
            SET a.type_alignement = $type_alignement,
                a.uri_externe = $uri_externe,
                a.updated_at = $updated_at
        """,
            id=id, type_alignement=data.type_alignement,
            uri_externe=data.uri_externe, updated_at=now
        )
    return {"message": "Alignement modifié", "id": id}


@app.delete("/alignements/{id}")
def delete_alignement(id: str):
    with get_session() as session:
        session.run("MATCH (a:Alignement {id: $id}) DETACH DELETE a", id=id)
    return {"message": f"Alignement {id} supprimé"}


@app.delete("/alignements")
def delete_all_alignements():
    with get_session() as session:
        session.run("MATCH (a:Alignement) DETACH DELETE a")
    return {"message": "Tous les alignements supprimés"}