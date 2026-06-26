from rdflib.namespace import SKOS, DCTERMS

def label_1(uri):
    labels = list(g.objects(uri, SKOS.prefLabel))
    return str(labels[0]) if labels else str(uri)


def titre_fr(t):
    labels = t.get("labels", [])           
    for l in labels:
        if l.get("lang") == "fr":
            return l.get("title", t["idTheso"])

    if labels:
        return labels[0].get("title", t["idTheso"])
    return t["idTheso"]


def label(g, uri):
    labels = list(g.objects(uri, SKOS.prefLabel))
    return str(labels[0]) if labels else str(uri)


def extraire_concept(g, c):
    return {
        "id": str(g.value(c, DCTERMS.identifier) or c),
        "uri": str(c),
        "prefLabel": label(g, c),
        "altLabel":    [str(x) for x in g.objects(c, SKOS.altLabel)],
        "definition":  [str(x) for x in g.objects(c, SKOS.definition)],
        "scopeNote":   [str(x) for x in g.objects(c, SKOS.scopeNote)],
        "note":        [str(x) for x in g.objects(c, SKOS.note)],
        "example":     [str(x) for x in g.objects(c, SKOS.example)],
        "historyNote": [str(x) for x in g.objects(c, SKOS.historyNote)],
        "broader":     [label(g, p) for p in g.objects(c, SKOS.broader)],
        "narrower":    [label(g, e) for e in g.objects(c, SKOS.narrower)],
        "isTopConcept": bool(list(g.objects(c, SKOS.topConceptOf))),
    }


def a_attribut_complet(concept):
    return any(concept[k] for k in
               ["definition", "scopeNote", "note", "example", "historyNote", "altLabel"])


def meta_thesaurus(tid):
    """Métadonnées du thésaurus : id, titres par langue, langues dispo."""
    t = meta_par_id.get(tid, {})
    labels = t.get("labels", [])
    return {
        "idTheso": tid,
        "type": t.get("type", ""),
        "titres": {l.get("lang"): l.get("title") for l in labels if l.get("lang")},
        "langues": [l.get("lang") for l in labels if l.get("lang")],
    }


def est_complet(c):
    return all(c.get(a) for a in ["prefLabel", "altLabel", "definition", "broader", "narrower"])


def nettoyer(c):
    return {
        "id": c["id"],
        "uri": c["uri"],
        "prefLabel": c["prefLabel"],
        "altLabel": c["altLabel"],
        "definition": c["definition"],
        "broader": c["broader"],
        "narrower": c["narrower"],
        "isTopConcept": c["isTopConcept"],
    } 