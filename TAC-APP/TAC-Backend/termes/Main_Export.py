import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from DataBase import get_arango_db

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, SKOS, DC
import uuid
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/export/generate")
def generate_export(thesaurus_id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run("""
    #         MATCH (th:Thesaurus {id: $id})
    #         RETURN th.id AS id, th.nom AS nom, th.description AS description
    #     """, id=thesaurus_id)
    #     th = result.single()
    #     if not th:
    #         raise HTTPException(status_code=404, detail="Thésaurus non trouvé")
    #     result = session.run("""
    #         MATCH (c:Concept)-[:APPARTIENT_A]->(th:Thesaurus {id: $id})
    #         RETURN c.id AS id, c.prefLabel AS prefLabel, c.altLabel AS altLabel,
    #                c.definition AS definition, c.broader AS broader,
    #                c.narrower AS narrower, c.related AS related
    #     """, id=thesaurus_id)
    #     concepts = [dict(r) for r in result]

    # ---- ARANGODB ----
    db = get_arango_db()
    th_cursor = db.aql.execute(
        "FOR th IN Thesauri FILTER th.id == @id RETURN th",
        bind_vars={"id": thesaurus_id}
    )
    th_list = list(th_cursor)
    if not th_list:
        raise HTTPException(status_code=404, detail="Thésaurus non trouvé")
    th = th_list[0]

    c_cursor = db.aql.execute("""
        FOR th IN Thesauri FILTER th.id == @id
          FOR c IN 1..1 INBOUND th ConceptThesaurus
          RETURN {
            id: c.id, prefLabel: c.prefLabel, altLabel: c.altLabel,
            definition: c.definition, broader: c.broader,
            narrower: c.narrower, related: c.related
          }
    """, bind_vars={"id": thesaurus_id})
    concepts = list(c_cursor)

    # Construire le graphe RDF
    g = Graph()
    BASE = Namespace(f"http://tac.fsp.fr/thesaurus/{thesaurus_id}/")
    g.bind("skos", SKOS)
    g.bind("dc", DC)
    g.bind("tac", BASE)

    scheme_uri = URIRef(f"http://tac.fsp.fr/thesaurus/{thesaurus_id}")
    g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add((scheme_uri, DC.title, Literal(th["nom"], lang="fr")))
    if th.get("description"):
        g.add((scheme_uri, DC.description, Literal(th["description"], lang="fr")))

    for c in concepts:
        concept_uri = BASE[c["id"]]
        g.add((concept_uri, RDF.type, SKOS.Concept))
        g.add((concept_uri, SKOS.inScheme, scheme_uri))

        if c["prefLabel"]:
            g.add((concept_uri, SKOS.prefLabel, Literal(c["prefLabel"], lang="fr")))

        if c["definition"]:
            g.add((concept_uri, SKOS.definition, Literal(c["definition"], lang="fr")))

        if c["altLabel"]:
            labels = c["altLabel"] if isinstance(c["altLabel"], list) else [c["altLabel"]]
            for label in labels:
                if label:
                    g.add((concept_uri, SKOS.altLabel, Literal(label.strip(), lang="fr")))

        if c["broader"]:
            g.add((concept_uri, SKOS.broader, Literal(c["broader"], lang="fr")))

        if c["narrower"]:
            narrowers = c["narrower"] if isinstance(c["narrower"], list) else [c["narrower"]]
            for n in narrowers:
                if n:
                    g.add((concept_uri, SKOS.narrower, Literal(n.strip(), lang="fr")))

        if c.get("related"):
            relateds = c["related"] if isinstance(c["related"], list) else [c["related"]]
            for r in relateds:
                if r:
                    g.add((concept_uri, SKOS.related, Literal(r.strip(), lang="fr")))

    contenu_ttl = g.serialize(format="turtle")

    export_id = str(uuid.uuid4())[:8]
    date_creation = datetime.now().isoformat()

    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("""
    #         MATCH (th:Thesaurus {id: $thesaurus_id})
    #         CREATE (e:Export {
    #             id: $export_id, nom: $nom, contenu_ttl: $contenu_ttl,
    #             format: 'turtle', statut: 'généré',
    #             date_creation: $date_creation, envoye_opentheso: false
    #         })
    #         CREATE (th)-[:HAS_EXPORT]->(e)
    #     """, thesaurus_id=thesaurus_id, export_id=export_id,
    #         nom=f"Export_{th['nom']}_{date_creation[:10]}",
    #         contenu_ttl=contenu_ttl, date_creation=date_creation)

    # ---- ARANGODB ----
    e_meta = db.collection("Exports").insert({
        "id": export_id,
        "nom": f"Export_{th['nom']}_{date_creation[:10]}",
        "contenu_ttl": contenu_ttl,
        "format": "turtle", "statut": "généré",
        "date_creation": date_creation, "envoye_opentheso": False
    })
    db.collection("ThesaurusExport").insert({"_from": th["_id"], "_to": e_meta["_id"]})

    return {
        "id": export_id,
        "nom": f"Export_{th['nom']}_{date_creation[:10]}",
        "contenu_ttl": contenu_ttl,
        "statut": "généré",
        "date_creation": date_creation
    }


@app.get("/export")
def get_exports():
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run("""
    #         MATCH (th:Thesaurus)-[:HAS_EXPORT]->(e:Export)
    #         RETURN e.id AS id, e.nom AS nom, e.statut AS statut, e.format AS format,
    #                e.date_creation AS date_creation, e.envoye_opentheso AS envoye_opentheso,
    #                th.nom AS thesaurus_nom
    #         ORDER BY e.date_creation DESC
    #     """)
    #     exports = [dict(r) for r in result]

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute("""
        FOR th IN Thesauri
          FOR e IN 1..1 OUTBOUND th ThesaurusExport
          SORT e.date_creation DESC
          RETURN {
            id: e.id, nom: e.nom, statut: e.statut, format: e.format,
            date_creation: e.date_creation, envoye_opentheso: e.envoye_opentheso,
            thesaurus_nom: th.nom
          }
    """)
    exports = list(cursor)

    return {"exports": exports}


@app.get("/export/{export_id}")
def get_export(export_id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run("""
    #         MATCH (th:Thesaurus)-[:HAS_EXPORT]->(e:Export {id: $id})
    #         RETURN e.id AS id, e.nom AS nom, e.contenu_ttl AS contenu_ttl,
    #                e.statut AS statut, e.format AS format,
    #                e.date_creation AS date_creation, e.envoye_opentheso AS envoye_opentheso,
    #                th.nom AS thesaurus_nom, th.id AS thesaurus_id
    #     """, id=export_id)
    #     export = result.single()
    #     if not export:
    #         raise HTTPException(status_code=404, detail="Export non trouvé")

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute("""
        FOR th IN Thesauri
          FOR e IN 1..1 OUTBOUND th ThesaurusExport
          FILTER e.id == @id
          RETURN {
            id: e.id, nom: e.nom, contenu_ttl: e.contenu_ttl,
            statut: e.statut, format: e.format,
            date_creation: e.date_creation, envoye_opentheso: e.envoye_opentheso,
            thesaurus_nom: th.nom, thesaurus_id: th.id
          }
    """, bind_vars={"id": export_id})
    exports = list(cursor)
    if not exports:
        raise HTTPException(status_code=404, detail="Export non trouvé")

    return exports[0]


@app.get("/export/{export_id}/download")
def download_export(export_id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run("""
    #         MATCH (th:Thesaurus)-[:HAS_EXPORT]->(e:Export {id: $id})
    #         RETURN e.contenu_ttl AS contenu_ttl, e.nom AS nom
    #     """, id=export_id)
    #     export = result.single()
    #     if not export:
    #         raise HTTPException(status_code=404, detail="Export non trouvé")

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute(
        "FOR e IN Exports FILTER e.id == @id RETURN {contenu_ttl: e.contenu_ttl, nom: e.nom}",
        bind_vars={"id": export_id}
    )
    exports = list(cursor)
    if not exports:
        raise HTTPException(status_code=404, detail="Export non trouvé")
    export = exports[0]

    filename = f"{export['nom']}.ttl"
    ascii_fallback = filename.encode("ascii", "ignore").decode("ascii") or "export.ttl"
    encoded_filename = quote(filename)

    return Response(
        content=export["contenu_ttl"],
        media_type="text/turtle",
        headers={
            "Content-Disposition": f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded_filename}"
        }
    )


@app.put("/export/{export_id}")
def update_export(export_id: str, contenu_ttl: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     result = session.run("""
    #         MATCH (e:Export {id: $id})
    #         SET e.contenu_ttl = $contenu_ttl, e.statut = 'modifié', e.date_modification = $date
    #         RETURN e.id AS id
    #     """, id=export_id, contenu_ttl=contenu_ttl, date=datetime.now().isoformat())
    #     if not result.single():
    #         raise HTTPException(status_code=404, detail="Export non trouvé")

    # ---- ARANGODB ----
    db = get_arango_db()
    cursor = db.aql.execute("FOR e IN Exports FILTER e.id == @id RETURN e", bind_vars={"id": export_id})
    if not list(cursor):
        raise HTTPException(status_code=404, detail="Export non trouvé")
    db.aql.execute("""
        FOR e IN Exports FILTER e.id == @id
          UPDATE e WITH {contenu_ttl: @contenu_ttl, statut: 'modifié', date_modification: @date} IN Exports
    """, bind_vars={"id": export_id, "contenu_ttl": contenu_ttl, "date": datetime.now().isoformat()})

    return {"message": "Export mis à jour"}


@app.delete("/export/{export_id}")
def delete_export(export_id: str):
    # ---- NEO4J ----
    # with get_session() as session:
    #     session.run("MATCH (e:Export {id: $id}) DETACH DELETE e", id=export_id)

    # ---- ARANGODB ----
    db = get_arango_db()
    db.aql.execute("""
        FOR e IN Exports FILTER e.id == @id
          FOR edge IN ThesaurusExport FILTER edge._to == e._id
          REMOVE edge IN ThesaurusExport
    """, bind_vars={"id": export_id})
    db.aql.execute("FOR e IN Exports FILTER e.id == @id REMOVE e IN Exports", bind_vars={"id": export_id})

    return {"message": "Export supprimé"}


# ─────────────────────────────────────────
# 7. Envoyer vers Opentheso
# ──────────────────────────────────────
