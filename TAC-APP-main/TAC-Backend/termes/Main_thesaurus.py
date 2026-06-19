import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from DataBase import get_session
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import re
import json
import requests




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ThesaurusGroupe(BaseModel):
    nom: str
    langue: str
    domaine: str
    concept_ids: List[str]
    validated_by: str

class ThesaurusUpdate(BaseModel):
    nom: Optional[str] = None
    langue: Optional[str] = None
    domaine: Optional[str] = None




@app.post("/thesaurus/generate")
def generate_thesaurus(concept_ids: List[str]):
    with get_session() as session:
        result = session.run("""
            MATCH (c:Concept)
            WHERE c.id IN $ids
            RETURN c.id AS id, c.prefLabel AS prefLabel, 
                   c.broader AS broader
        """, ids=concept_ids)
        concepts = [dict(r) for r in result]


    groupes = {}
    for c in concepts:
        broader = (c["broader"] or "").split(",")[0].strip().rstrip(".").lower()
        if not broader:
            broader = "général"
        # clé de regroupement basée sur le premier mot, pour fusionner
        # les variantes d'un même domaine (ex: "architecture" et "architecture civile")
        cle = broader.split(" ")[0]
        if cle not in groupes:
            groupes[cle] = {"label": broader, "concepts": []}
        elif len(broader) > len(groupes[cle]["label"]):
            groupes[cle]["label"] = broader
        groupes[cle]["concepts"].append(c)

    thesauri = [
        {
            "nom": f"Thésaurus — {g['label']}",
            "langue": "français",
            "domaine": g["label"],
            "concept_ids": [c["id"] for c in g["concepts"]],
            "concepts": [{"id": c["id"], "prefLabel": c["prefLabel"]} for c in g["concepts"]]
        }
        for g in groupes.values()
    ]

    return {"thesauri": thesauri}


@app.post("/thesaurus/validate")
def validate_thesaurus(thesaurus: ThesaurusGroupe):
    with get_session() as session:
        id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        session.run("""
            CREATE (th:Thesaurus {
                id: $id,
                nom: $nom,
                langue: $langue,
                domaine: $domaine,
                validated_by: $validated_by,
                validated_at: $validated_at,
                created_at: $created_at,
                statut: 'validé'
            })
        """,
            id=id, nom=thesaurus.nom,
            langue=thesaurus.langue, domaine=thesaurus.domaine,
            validated_by=thesaurus.validated_by,
            validated_at=now, created_at=now
        )

        for concept_id in thesaurus.concept_ids:
            session.run("""
                MATCH (c:Concept {id: $concept_id})
                MATCH (th:Thesaurus {id: $id})
                CREATE (c)-[:APPARTIENT_A]->(th)
            """, concept_id=concept_id, id=id)

    return {"message": "Thésaurus validé", "id": id}


@app.get("/thesaurus")
def get_thesaurus():
    with get_session() as session:
        result = session.run("""
            MATCH (th:Thesaurus)
            OPTIONAL MATCH (c:Concept)-[:APPARTIENT_A]->(th)
            OPTIONAL MATCH (t:Terme)-[:A_CONCEPT]->(c)
            RETURN th.id AS id, th.nom AS nom,
                   th.langue AS langue, th.domaine AS domaine,
                   th.statut AS statut,
                   th.validated_by AS validated_by,
                   th.validated_at AS validated_at,
                   th.created_at AS created_at,
                   count(c) AS nb_concepts,
                   collect(DISTINCT c.id) AS concept_ids,
                   collect(DISTINCT c.prefLabel) AS concept_labels,
                   collect(DISTINCT t.label) AS termes
        """)
        thesauri = [dict(r) for r in result]
    return {"thesauri": thesauri}


@app.patch("/thesaurus/{id}")
def update_thesaurus(id: str, data: ThesaurusUpdate):
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run("""
            MATCH (th:Thesaurus {id: $id})
            SET th.nom = $nom,
                th.langue = $langue,
                th.domaine = $domaine,
                th.updated_at = $updated_at
        """,
            id=id, nom=data.nom,
            langue=data.langue, domaine=data.domaine,
            updated_at=now
        )
    return {"message": "Thésaurus modifié", "id": id}


@app.delete("/thesaurus/{id}")
def delete_thesaurus(id: str):
    with get_session() as session:
        session.run(
            "MATCH (th:Thesaurus {id: $id}) DETACH DELETE th",
            id=id
        )
    return {"message": f"Thésaurus {id} supprimé"}


@app.delete("/thesaurus")
def delete_all_thesaurus():
    with get_session() as session:
        session.run("MATCH (th:Thesaurus) DETACH DELETE th")
    return {"message": "Tous les thésauri supprimés"}



@app.post("/thesaurus/reject")
def reject_thesaurus(thesaurus: ThesaurusGroupe):
    with get_session() as session:
        id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        session.run("""
            CREATE (th:Thesaurus {
                id: $id,
                nom: $nom,
                langue: $langue,
                domaine: $domaine,
                validated_by: $validated_by,
                validated_at: $validated_at,
                created_at: $created_at,
                statut: 'rejeté'
            })
        """,
            id=id, nom=thesaurus.nom,
            langue=thesaurus.langue, domaine=thesaurus.domaine,
            validated_by=thesaurus.validated_by or "—",
            validated_at=now, created_at=now
        )


        for concept_id in thesaurus.concept_ids:
            session.run("""
                MATCH (c:Concept {id: $concept_id})
                MATCH (th:Thesaurus {id: $id})
                CREATE (c)-[:APPARTIENT_A]->(th)
            """, concept_id=concept_id, id=id)

    return {"message": "Thésaurus rejeté et sauvegardé", "id": id}