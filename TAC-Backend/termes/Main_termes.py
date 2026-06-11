import sys
sys.path.append("../")
from DataBase import get_session
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

# ========================
# MODÈLES
# ========================
class Terme(BaseModel):
    label: str

class TermeUpdate(BaseModel):
    label: Optional[str] = None

# ========================
# TERME (un seul)
# ========================
@app.post("/terme")
def create_terme(terme: Terme):
    with get_session() as session:
        id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run(
            "CREATE (t:Terme {id: $id, label: $label, created_at: $created_at, updated_at: $updated_at, statut: $statut})",
            id=id, label=terme.label, created_at=now, updated_at=None, statut="en attente"
        )
    return {"message": "Terme créé", "id": id, "label": terme.label, "created_at": now, "statut": "en attente"}

@app.get("/terme/{id}")
def get_terme(id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (t:Terme {id: $id}) RETURN t.id AS id, t.label AS label, t.created_at AS created_at, t.updated_at AS updated_at, t.statut AS statut ORDER BY t.created_at DESC",
            id=id
        )
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Terme non trouvé")
    return {"id": record["id"], "label": record["label"], "created_at": record["created_at"], "updated_at": record["updated_at"], "statut": record["statut"]}

@app.patch("/terme/{id}")
def update_terme(id: str, terme: TermeUpdate):
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run(
            "MATCH (t:Terme {id: $id}) SET t.label = $label, t.updated_at = $updated_at",
            id=id, label=terme.label, updated_at=now
        )
    return {"message": "Terme modifié", "id": id, "updated_at": now}

@app.delete("/terme/{id}")
def delete_terme(id: str):
    with get_session() as session:
        session.run("MATCH (t:Terme {id: $id}) DELETE t", id=id)
    return {"message": f"Terme {id} supprimé"}

# ========================
# TERMES (liste) — search AVANT {id} !
# ========================
@app.get("/termes/search")
def search_terme(q: str):
    with get_session() as session:
        result = session.run(
            "MATCH (t:Terme) WHERE toLower(t.label) CONTAINS toLower($q) RETURN t.id AS id, t.label AS label, t.created_at AS created_at, t.updated_at AS updated_at, t.statut AS statut ORDER BY t.created_at DESC",
            q=q
        )
        termes = [{"id": r["id"], "label": r["label"], "created_at": r["created_at"], "updated_at": r["updated_at"], "statut": r["statut"]} for r in result]
    return {"termes": termes}

@app.patch("/termes/fix-dates")
def fix_old_dates():
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run(
            "MATCH (t:Terme) WHERE t.created_at IS NULL SET t.created_at = $now, t.statut = 'en attente'",
            now=now
        )
        session.run(
            "MATCH (t:Terme) WHERE t.statut IS NULL SET t.statut = 'en attente'"
        )
    return {"message": "Dates et statuts mis à jour"}

@app.post("/termes")
def create_termes(termes: List[Terme]):
    with get_session() as session:
        ids = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for t in termes:
            id = str(uuid.uuid4())[:8]
            session.run(
                "CREATE (t:Terme {id: $id, label: $label, created_at: $now, updated_at: $updated_at, statut: $statut})",
                id=id, label=t.label, now=now, updated_at=None, statut="en attente"
            )
            ids.append(id)
    return {"message": f"{len(termes)} termes créés", "ids": ids}

@app.get("/termes")
def get_termes():
    with get_session() as session:
        result = session.run(
            "MATCH (t:Terme) RETURN t.id AS id, t.label AS label, t.created_at AS created_at, t.updated_at AS updated_at, t.statut AS statut ORDER BY t.created_at DESC"
        )
        termes = [{"id": r["id"], "label": r["label"], "created_at": r["created_at"], "updated_at": r["updated_at"], "statut": r["statut"]} for r in result]
    return {"termes": termes}

@app.patch("/termes/{id}")
def update_termes(id: str, terme: TermeUpdate):
    with get_session() as session:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        session.run(
            "MATCH (t:Terme {id: $id}) SET t.label = $label, t.updated_at = $now",
            id=id, label=terme.label, now=now
        )
    return {"message": f"Terme {id} mis à jour"}

@app.delete("/termes/{id}")
def delete_termes(id: str):
    with get_session() as session:
        session.run("MATCH (t:Terme {id: $id}) DELETE t", id=id)
    return {"message": f"Terme {id} supprimé"}

@app.delete("/termes")
def delete_all_termes():
    with get_session() as session:
        session.run("MATCH (t:Terme) DELETE t")
    return {"message": "Tous les termes supprimés"}