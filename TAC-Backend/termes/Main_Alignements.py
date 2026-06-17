import sys
import os
import uuid
import json
import re
import requests
import base64
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from arango import ArangoClient
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_arango_db():
    client = ArangoClient(hosts="http://localhost:8529")
    db = client.db("as", username="rasri", password="")
    return db


class Alignement(BaseModel):
    thesaurus_tac_id: str
    thesaurus_tac_nom: str
    concept_tac_id: str
    concept_tac_label: str
    type_alignement: str
    thesaurus_arango_nom: str
    concept_externe_label: str
    uri_externe: str
    source_externe: str
    validated_by: str
    statut: str

class AlignementUpdate(BaseModel):
    type_alignement: Optional[str] = None
    uri_externe: Optional[str] = None


def call_gemini(prompt: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text


@app.get("/alignements/arango/thesauri")
def get_arango_thesauri():
    db = get_arango_db()
    thesauri = list(db.aql.execute("FOR theso IN thesaurus RETURN theso"))
    
    # Nettoyer les champs ArangoDB non sérialisables
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
  
@app.get("/alignements/generate")
def generate_alignements(thesaurus_tac_id: str, thesaurus_arango_nom: str):

    with get_session() as session:
        result = session.run("""
            MATCH (c:Concept)-[:APPARTIENT_A]->(th:Thesaurus {id: $id})
            RETURN c.id AS id, c.prefLabel AS prefLabel,
                   c.altLabel AS altLabel, c.broader AS broader,
                   th.nom AS thesaurus_nom
        """, id=thesaurus_tac_id)
        concepts_tac = [dict(r) for r in result]

    if not concepts_tac:
        raise HTTPException(status_code=404, detail="Aucun concept trouvé")

    db = get_arango_db()
    results = list(db.aql.execute(f"FOR doc IN thesaurus FILTER doc.title == '{thesaurus_arango_nom}' RETURN doc"))
    thesaurus_arango = results[0] if results else None

    if not thesaurus_arango:
        raise HTTPException(status_code=404, detail="Thésaurus ArangoDB non trouvé")

    concepts_arango = thesaurus_arango.get("concepts", [])

    tac_text = "\n".join([
        f"- ID:{c['id']} | {c['prefLabel']} | altLabel: {c['altLabel']} | broader: {c['broader']}"
        for c in concepts_tac
    ])

    arango_text = "\n".join([
        f"- {c['prefLabel']} | URI: {c['uri']}"
        for c in concepts_arango
    ])

    prompt = f"""Tu es un expert en alignement de thésaurus SKOS.

            Concepts du thésaurus TAC :
            {tac_text}

            Concepts du thésaurus externe ({thesaurus_arango_nom}) :
            {arango_text}

            Pour chaque concept TAC, trouve le concept externe le plus similaire.
            Type d'alignement :
            - exactMatch : concepts identiques
            - closeMatch : concepts très similaires

            Réponds UNIQUEMENT en JSON sans texte avant ou après :

            [
            {{
                "concept_tac_id": "id du concept TAC",
                "concept_tac_label": "label TAC",
                "type_alignement": "exactMatch ou closeMatch",
                "concept_externe_label": "label externe",
                "uri_externe": "uri du concept externe"
            }}
            ]

            Si aucun alignement trouvé pour un concept, ne l'inclus pas."""

    raw = call_gemini(prompt)
    print("=== Gemini response ===", raw)

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="Gemini n'a pas retourné un JSON valide")

    alignements = json.loads(match.group())

    for a in alignements:
        a["thesaurus_tac_id"] = thesaurus_tac_id
        a["thesaurus_tac_nom"] = concepts_tac[0]["thesaurus_nom"]
        a["thesaurus_arango_nom"] = thesaurus_arango_nom
        a["source_externe"] = thesaurus_arango["source"]

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