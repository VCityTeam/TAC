import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import "./termes.css"

function Thesaurus() {

  const [concepts, setConcepts] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [search, setSearch] = useState("")
  const [thesauriGeneres, setThesauriGeneres] = useState([])
  const [thesauri, setThesauri] = useState([])
  const [loading, setLoading] = useState(false)
  const [validatedBy, setValidatedBy] = useState("")
  const [editId, setEditId] = useState(null)
  const [editData, setEditData] = useState({})
  const [error, setError] = useState("")
  const navigate = useNavigate()



  
useEffect(() => {
    fetch("http://localhost:8001/concepts")
      .then(res => res.json())
      .then(data => {
        const valides = data.concepts.filter(c => c.statut === "validé")
        setConcepts(valides)
      })
      .catch(() => setError("Impossible de contacter le serveur de concepts (port 8001)."))

    fetch("http://localhost:8002/thesaurus")
      .then(res => res.json())
      .then(data => {
        if (!data.thesauri) { setError("Réponse inattendue du serveur thésaurus."); return }
        setThesauri(data.thesauri)
      })
      .catch(() => setError("Impossible de contacter le serveur thésaurus (port 8002). Vérifiez que Main_thesaurus.py est démarré."))
}, [])
  
  const conceptsAssocies = new Set(thesauri.flatMap(t => t.concept_ids || []))

  const conceptsFiltres = concepts.filter(c =>
    !conceptsAssocies.has(c.id) &&
    c.prefLabel.toLowerCase().startsWith(search.toLowerCase())
  )

  
  function toggleConcept(id) {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  function toggleAll() {
    if (selectedIds.length === conceptsFiltres.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(conceptsFiltres.map(c => c.id))
    }
  }

 

  function generateThesaurus() {
    if (selectedIds.length === 0) return
    setLoading(true)
    setThesauriGeneres([])
    fetch("http://localhost:8002/thesaurus/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(selectedIds)
    })
      .then(res => res.json())
      .then(data => {
        setThesauriGeneres(data.thesauri)
        setLoading(false)
      })
      .catch(err => {
        console.error("Erreur génération thésaurus :", err)
        setLoading(false)
      })
  }


  function validateThesaurus(th) {
    if (!validatedBy) return
    fetch("http://localhost:8002/thesaurus/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nom: th.nom,
        langue: th.langue,
        domaine: th.domaine,
        concept_ids: th.concept_ids,
        validated_by: validatedBy
      })
    })
      .then(res => res.json())
      .then(() => {
        fetch("http://localhost:8002/thesaurus")
          .then(res => res.json())
          .then(data => setThesauri(data.thesauri))
        setThesauriGeneres(thesauriGeneres.filter(t => t !== th))
      })
  }


  function updateThesaurus(id) {
    fetch(`http://localhost:8002/thesaurus/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(editData)
    })
      .then(() => {
        setThesauri(thesauri.map(t => t.id === id ? { ...t, ...editData } : t))
        setEditId(null)
        setEditData({})
      })
  }


  function deleteThesaurus(id) {
    if (!window.confirm("Supprimer ce thésaurus ?")) return
    fetch(`http://localhost:8002/thesaurus/${id}`, { method: "DELETE" })
      .then(() => setThesauri(thesauri.filter(t => t.id !== id)))
  }


  function deleteAll() {
    if (!window.confirm("Supprimer tous les thésauri ?")) return
    fetch("http://localhost:8002/thesaurus", { method: "DELETE" })
      .then(() => setThesauri([]))
  }


function rejectThesaurus(th) {
    fetch("http://localhost:8002/thesaurus/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nom: th.nom,
            langue: th.langue,
            domaine: th.domaine,
            concept_ids: th.concept_ids,
            validated_by: validatedBy || "—"
        })
    })
    .then(res => res.json())
    .then(() => {
        setThesauriGeneres(prev => prev.filter(t => t !== th))
        // Recharger depuis Neo4j
        fetch("http://localhost:8002/thesaurus")
            .then(res => res.json())
            .then(data => setThesauri(data.thesauri))
    })
}


  return (
    <div>
      <nav className="navbar navbar-light sticky-top px-4">
        <span className="nav-logo">TAC — Thésaurus Automatisé par Curation</span>
        <div className="d-flex gap-2">
          <Link to="/"><span className="step">Termes</span></Link>
          <Link to="/concepts"><span className="step">Concepts</span></Link>
          <Link to="/thesaurus"><span className="step active">Thésaurus</span></Link>
          <Link to="/alignements"><span className="step">Alignements</span></Link>
          <Link to="/export"><span className="step">Export</span></Link>
        </div>
      </nav>

      <div className="container-fluid main">

        <div className="mb-4">
          <h1 className="page-title">Gestion des thésauri</h1>
        </div>

        {error && (
          <div className="alert alert-danger mb-3">⚠️ {error}</div>
        )}

        {/* STATS */}
        <div className="row g-3 mb-4">
          <div className="col-4">
            <div className="stat-card">
              <div className="stat-label">Total thésauri</div>
              <div className="stat-value text-dark">{thesauri.length}</div>
            </div>
          </div>
          <div className="col-4">
            <div className="stat-card">
              <div className="stat-label">Validés</div>
              <div className="stat-value color-ok">
                {thesauri.filter(t => t.statut === "validé").length}
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="stat-card">
              <div className="stat-label">Non validés</div>
              <div className="stat-value color-warn">
                {thesauri.filter(t => t.statut !== "validé").length}
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 1 : Sélection concepts */}
        <div className="section-card mb-3">
          <div className="section-title">Sélectionner les concepts</div>
          <input
            type="text"
            className="form-control mb-2"
            placeholder="🔍 Rechercher un concept..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <div className="mb-2">
            <button className="btn btn-secondary btn-sm" onClick={toggleAll}>
              {selectedIds.length === conceptsFiltres.length ? "Tout désélectionner" : "Tout sélectionner"}
            </button>
            <span className="ms-3 count-info">{selectedIds.length} concept(s) sélectionné(s)</span>
          </div>
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-3">
              <thead>
                <tr>
                  <th style={{width: "40px"}}></th>
                  <th>prefLabel</th>
                  <th>Broader</th>
                </tr>
              </thead>
              <tbody>
                {conceptsFiltres.map(c => (
                  <tr key={c.id} onClick={() => toggleConcept(c.id)} style={{cursor: "pointer"}}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(c.id)}
                        onChange={() => toggleConcept(c.id)}
                      />
                    </td>
                    <td className="fw-500">{c.prefLabel}</td>
                    <td>{c.broader}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            className="btn btn-accent"
            onClick={generateThesaurus}
            disabled={selectedIds.length === 0 || loading}
          >
            {loading ? "Génération en cours..." : "▶ Générer les thésauri"}
          </button>
        </div>

        {/* SECTION 2 : Regroupement des concepts */}
        {thesauriGeneres.length > 0 && (
          <div className="section-card mb-3">
            <div className="section-title">Regroupement des concepts</div>
            <input
              type="text"
              className="form-control mb-3"
              placeholder="Votre nom complet (validateur)..."
              value={validatedBy}
              onChange={e => setValidatedBy(e.target.value)}
            />
            {thesauriGeneres.map((th, index) => (
              <div key={index} className="section-card mb-3">
                <div className="section-title">Thésaurus {index + 1}</div>
                <table className="table align-middle mb-3">
                  <tbody>
                    <tr>
                      <td className="fw-500">Nom</td>
                      <td>
                        <input
                          className="form-control"
                          value={th.nom}
                          onChange={e => {
                            const updated = [...thesauriGeneres]
                            updated[index].nom = e.target.value
                            setThesauriGeneres(updated)
                          }}
                        />
                      </td>
                    </tr>
                    <tr>
                      <td className="fw-500">Langue</td>
                      <td>
                        <input
                          className="form-control"
                          value={th.langue}
                          onChange={e => {
                            const updated = [...thesauriGeneres]
                            updated[index].langue = e.target.value
                            setThesauriGeneres(updated)
                          }}
                        />
                      </td>
                    </tr>
                    <tr>
                      <td className="fw-500">Domaine</td>
                      <td>
                        <input
                          className="form-control"
                          value={th.domaine}
                          onChange={e => {
                            const updated = [...thesauriGeneres]
                            updated[index].domaine = e.target.value
                            setThesauriGeneres(updated)
                          }}
                        />
                      </td>
                    </tr>
                    <tr>
                      <td className="fw-500">Concepts</td>
                      <td>{th.concepts?.map(c => c.prefLabel).join(", ")}</td>
                    </tr>
                  </tbody>
                </table>
                <div className="d-flex gap-2">
                  <button
                    className="btn btn-accent"
                    onClick={() => validateThesaurus(th)}
                    disabled={!validatedBy}
                  >
                    ✅ Valider
                  </button>
                    <button
                        className="btn btn-delete-sm"
                        onClick={() => rejectThesaurus(th)}
                    >
                        ❌ Rejeter
                    </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* SECTION 3 : Liste des thésauri */}
        <div className="section-card mb-3">
          <div className="section-title">Liste des thésauri</div>
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Langue</th>
                  <th>Domaine</th>
                  <th>Nb concepts</th>
                  <th>Termes</th>
                  <th>IDs Concepts</th>
                  <th>Statut</th>
                  <th>Validé par</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {thesauri.map(t => (
                  <tr key={t.id}>
                    <td className="fw-500">
                      {editId === t.id ?
                        <input className="form-control" value={editData.nom} onChange={e => setEditData({...editData, nom: e.target.value})} />
                        : t.nom}
                    </td>
                    <td>
                      {editId === t.id ?
                        <input className="form-control" value={editData.langue} onChange={e => setEditData({...editData, langue: e.target.value})} />
                        : t.langue}
                    </td>
                    <td>
                      {editId === t.id ?
                        <input className="form-control" value={editData.domaine} onChange={e => setEditData({...editData, domaine: e.target.value})} />
                        : t.domaine}
                    </td>
                    <td>{t.nb_concepts}</td>
                    <td className="id-cell">{t.termes?.join(", ")}</td>
                    <td className="id-cell">{t.concept_ids?.join(", ")}</td>
                    <td>
                      <span className={t.statut === "validé" ? "badge-ok" : "badge-pend"}>
                        {t.statut}
                      </span>
                    </td>
                    <td className="id-cell">{t.validated_by}</td>
                    <td>{t.validated_at}</td>
                    <td>
                      {editId === t.id ? (
                        <button className="btn btn-accent" onClick={() => updateThesaurus(t.id)}>✅ Sauvegarder</button>
                      ) : (
                        <button className="btn btn-edit-sm" onClick={() => { setEditId(t.id); setEditData({nom: t.nom, langue: t.langue, domaine: t.domaine}) }}>✏️ Modifier</button>
                      )}
                      <button className="btn btn-delete-sm" onClick={() => deleteThesaurus(t.id)}>🗑 Supprimer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
          <span className="count-info">{thesauri.length} thésauri</span>
          <button className="btn btn-accent" onClick={deleteAll}>🗑 Supprimer tout</button>
          <button className="btn btn-accent" onClick={() => navigate("/alignements")}>
            Passer aux alignements →
          </button>
        </div>

      </div>

      <footer>
        <span>TAC — Fondation des Sciences du Patrimoine × LIRIS</span>
        <span>v1.0.0 — 2026</span>
      </footer>
    </div>
  )
}

export default Thesaurus