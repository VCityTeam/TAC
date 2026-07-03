import sys
sys.path.append("../")
from DataBase import get_arango_db

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Terme(BaseModel):
    label: str

class TermeUpdate(BaseModel):
    label: Optional[str] = None


@app.post("/terme")
def create_terme(terme: Terme):
    id = str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run(
    #         "CREATE (t:Terme {id: $id, label: $label, created_at: $created_at, updated_at: $updated_at, statut: $statut})",
    #         id=id, label=terme.label, created_at=now, updated_at=None, statut="en attente"
    #     )

    # ---- ARANGODB ----
    db = get_arango_db()
    db.collection("Termes").insert({
        "id": id, "label": terme.label,
        "created_at": now, "updated_at": None, "statut": "en attente"
    })

    return {"message": "Terme créé", "id": id, "label": terme.label, "created_at": now, "statut": "en attente"}


@app.get("/terme/{id}")
def get_terme(id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run(
    #         "MATCH (t:Terme {id: $id}) RETURN t.id AS id, t.label AS label, t.created_at AS created_at, t.updated_at AS updated_at, t.statut AS statut ORDER BY t.created_at DESC",
    #         id=id
    #     )
    #     record = result.single()
    #     if not record:
    #         raise HTTPException(status_code=404, detail="Terme non trouvé")
    # return {"id": record["id"], ...}

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id RETURN t",
        bind_vars={"id": id}
    )
    records = list(cursor)
    if not records:
        raise HTTPException(status_code=404, detail="Terme non trouvé")
    t = records[0]
    return {"id": t["id"], "label": t["label"], "created_at": t.get("created_at"), "updated_at": t.get("updated_at"), "statut": t.get("statut")}


@app.patch("/terme/{id}")
def update_terme(id: str, terme: TermeUpdate):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run(
    #         "MATCH (t:Terme {id: $id}) SET t.label = $label, t.updated_at = $updated_at",
    #         id=id, label=terme.label, updated_at=now
    #     )

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id UPDATE t WITH {label: @label, updated_at: @now} IN Termes",
        bind_vars={"id": id, "label": terme.label, "now": now}
    )

    return {"message": "Terme modifié", "id": id, "updated_at": now}


@app.delete("/terme/{id}")
def delete_terme(id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("MATCH (t:Terme {id: $id}) DELETE t", id=id)

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id REMOVE t IN Termes",
        bind_vars={"id": id}
    )

    return {"message": f"Terme {id} supprimé"}


# ========================
# TERMES (liste) — search AVANT {id} !
# ========================
@app.get("/termes/search")
def search_terme(q: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run(
    #         "MATCH (t:Terme) WHERE toLower(t.label) CONTAINS toLower($q) RETURN t.id AS id, t.label AS label, t.created_at AS created_at, t.updated_at AS updated_at, t.statut AS statut ORDER BY t.created_at DESC",
    #         q=q
    #     )
    #     termes = [{"id": r["id"], ...} for r in result]

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute(
        "FOR t IN Termes FILTER CONTAINS(LOWER(t.label), LOWER(@q)) SORT t.created_at DESC RETURN t",
        bind_vars={"q": q}
    )
    termes = [{"id": t["id"], "label": t["label"], "created_at": t.get("created_at"), "updated_at": t.get("updated_at"), "statut": t.get("statut")} for t in cursor]

    return {"termes": termes}


@app.patch("/termes/fix-dates")
def fix_old_dates():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run(
    #         "MATCH (t:Terme) WHERE t.created_at IS NULL SET t.created_at = $now, t.statut = 'en attente'",
    #         now=now
    #     )
    #     session.run(
    #         "MATCH (t:Terme) WHERE t.statut IS NULL SET t.statut = 'en attente'"
    #     )

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute(
        "FOR t IN Termes FILTER t.created_at == null UPDATE t WITH {created_at: @now, statut: 'en attente'} IN Termes",
        bind_vars={"now": now}
    )
    db.aql.execute(
        "FOR t IN Termes FILTER t.statut == null UPDATE t WITH {statut: 'en attente'} IN Termes"
    )

    return {"message": "Dates et statuts mis à jour"}


@app.post("/termes")
def create_termes(termes: List[Terme]):
    ids = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     for t in termes:
    #         id = str(uuid.uuid4())[:8]
    #         session.run(
    #             "CREATE (t:Terme {id: $id, label: $label, created_at: $now, updated_at: $updated_at, statut: $statut})",
    #             id=id, label=t.label, now=now, updated_at=None, statut="en attente"
    #         )
    #         ids.append(id)

    # ---- ARANGODB ----
    db = get_arango_db()
    for t in termes:
        id = str(uuid.uuid4())[:8]
        db.collection("Termes").insert({
            "id": id, "label": t.label,
            "created_at": now, "updated_at": None, "statut": "en attente"
        })
        ids.append(id)

    return {"message": f"{len(termes)} termes créés", "ids": ids}


@app.get("/termes")
def get_termes():
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run(
    #         "MATCH (t:Terme) RETURN t.id AS id, t.label AS label, t.created_at AS created_at, t.updated_at AS updated_at, t.statut AS statut ORDER BY t.created_at DESC"
    #     )
    #     termes = [{"id": r["id"], ...} for r in result]

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute(
        "FOR t IN Termes SORT t.created_at DESC RETURN t"
    )
    termes = [{"id": t["id"], "label": t["label"], "created_at": t.get("created_at"), "updated_at": t.get("updated_at"), "statut": t.get("statut")} for t in cursor]

    return {"termes": termes}


@app.patch("/termes/{id}")
def update_termes(id: str, terme: TermeUpdate):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run(
    #         "MATCH (t:Terme {id: $id}) SET t.label = $label, t.updated_at = $now",
    #         id=id, label=terme.label, now=now
    #     )

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id UPDATE t WITH {label: @label, updated_at: @now} IN Termes",
        bind_vars={"id": id, "label": terme.label, "now": now}
    )

    return {"message": f"Terme {id} mis à jour"}


@app.delete("/termes/{id}")
def delete_termes(id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("MATCH (t:Terme {id: $id}) DELETE t", id=id)

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute(
        "FOR t IN Termes FILTER t.id == @id REMOVE t IN Termes",
        bind_vars={"id": id}
    )

    return {"message": f"Terme {id} supprimé"}


@app.delete("/termes")
def delete_all_termes():
    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("MATCH (t:Terme) DELETE t")

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute("FOR t IN Termes REMOVE t IN Termes")

    return {"message": "Tous les termes supprimés"}
