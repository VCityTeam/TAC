import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import "./Concepts.css"

function Concepts() {

  const [termes, setTermes] = useState([])
  const [selectedTerme, setSelectedTerme] = useState(null)
  const [search, setSearch] = useState("")
  const [concept, setConcept] = useState(null)
  const [loading, setLoading] = useState(false)
  const [concepts, setConcepts] = useState([])
  const [validatedBy, setValidatedBy] = useState("")
  const [editId, setEditId] = useState(null)
  const [editConcept, setEditConcept] = useState({})
  


  useEffect(() => {
    fetch("http://localhost:8000/termes")
      .then(res => res.json())
      .then(data => setTermes(data.termes.filter(t => t.statut === "en attente")))
  }, [])

  
  useEffect(() => {
    fetch("http://localhost:8001/concepts")
      .then(res => res.json())
      .then(data => setConcepts(data.concepts))
  }, [])


const termesFiltered = termes.filter(t =>
    t.label.toLowerCase().startsWith(search.toLowerCase())
)


  function generateConcept() {
    if (!selectedTerme) return
    setLoading(true)
    setConcept(null)
    fetch(`http://localhost:8001/concepts/generate?terme_id=${selectedTerme.id}&terme_label=${encodeURIComponent(selectedTerme.label)}`)
      .then(res => res.json())
      .then(data => {
        setConcept(data)
        setLoading(false)
      })
  }


  function validateConcept() {
    console.log("=== validateConcept appelé ===")
    console.log("selectedTerme:", selectedTerme)
    console.log("concept:", concept)
    console.log("validatedBy:", validatedBy)
    if (!concept || !validatedBy) return
    fetch("http://localhost:8001/concepts/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        terme_id: selectedTerme.id,
        prefLabel: concept.prefLabel,
        definition: concept.definition,
        altLabel: concept.altLabel,
        broader: concept.broader,
        narrower: concept.narrower,
        model_id: concept.model_id,
        prompt_id: concept.prompt_id,
        iteration: concept.iteration,
        validated_by: validatedBy
      })
    })
      .then(res => res.json())
      .then(() => {
        fetch("http://localhost:8001/concepts")
          .then(res => res.json())
          .then(data => setConcepts(data.concepts))
        setTermes(termes.filter(t => t.id !== selectedTerme.id))
        setConcept(null)
        setSelectedTerme(null)
      })
  }


  function rejectConcept() {
    fetch(`http://localhost:8001/concepts/reject?terme_id=${selectedTerme.id}&iteration=${concept.iteration}`, {
      method: "POST"
    })
      .then(() => {
        setConcept(null)
      })
  }

  function deleteConcept(id) {
    if (!window.confirm("Supprimer ce concept ?")) return
    fetch(`http://localhost:8001/concepts/${id}`, { method: "DELETE" })
        .then(() => setConcepts(concepts.filter(c => c.id !== id)))
  }

    function deleteAllConcepts() {
        if (!window.confirm("Supprimer tous les concepts ?")) return
        fetch("http://localhost:8001/concepts", { method: "DELETE" })
            .then(() => setConcepts([]))
    }

    function updateConcept(id) {
    fetch(`http://localhost:8001/concepts/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editConcept)
    })
    .then(() => {
        setConcepts(concepts.map(c => c.id === id ? { ...c, ...editConcept } : c))
        setEditId(null)
        setEditConcept({})
    })
   }

   function rejectConcept() {
    fetch(`http://localhost:8001/concepts/reject?terme_id=${selectedTerme.id}&iteration=${concept.iteration}`, {
        method: "POST"
    })
    .then(() => {
        setConcepts([...concepts, { ...concept, statut: "rejeté" }])
        setConcept(null)
    })
}
  return (
    <div>
      <nav className="navbar navbar-light sticky-top px-4">
        <span className="nav-logo">TAC — Thésaurus Automatisé par Curation</span>
        <div className="d-flex gap-2">
          <Link to="/"><span className="step">Termes</span></Link>
          <Link to="/concepts"><span className="step active">Concepts</span></Link>
          <span className="step">Thésaurus</span>
          <span className="step">Alignements</span>
          <span className="step">Export</span>
        </div>
      </nav>

      <div className="container-fluid main">

        <div className="mb-4">
          <h1 className="page-title">Génération de concepts</h1>
        </div>

        {/* STATS */}
        <div className="row g-3 mb-4">
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Termes en attente</div>
              <div className="stat-value color-warn">{termes.length}</div>
            </div>
          </div>
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Concepts validés</div>
              <div className="stat-value color-ok">
                {concepts.filter(c => c.statut === "validé").length}
              </div>
            </div>
          </div>
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Total concepts</div>
              <div className="stat-value text-dark">{concepts.length}</div>
            </div>
          </div>
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Rejetés</div>
              <div className="stat-value" style={{color: "#c0392b"}}>
                {concepts.filter(c => c.statut === "rejeté").length}
              </div>
            </div>
          </div>
        </div>

        {/* SÉLECTION TERME */}
        <div className="section-card mb-3">
          <div className="section-title">Sélectionner un terme</div>
          <input
            type="text"
            className="form-control mb-2"
            placeholder="🔍 Rechercher un terme..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        <select
            className="form-control mb-3"
            value={selectedTerme ? selectedTerme.id : ""}
            onChange={e => setSelectedTerme(termes.find(t => t.id === e.target.value))}
            >
            <option value="">-- Choisir un terme --</option>
            {termesFiltered.map(t => (
                <option key={t.id} value={t.id}>{t.label}</option>
            ))}
            </select>
          <button
            className="btn btn-accent"
            onClick={generateConcept}
            disabled={!selectedTerme || loading}
          >
            {loading ? "Génération en cours..." : "▶ Générer le concept"}
          </button>
        </div>

        {/* RÉSULTAT LLM */}
        {concept && (
        <div className="section-card mb-3">
            <div className="section-title">Concept généré</div>
            <table className="table align-middle mb-3">
            <tbody>
                <tr><td className="fw-500">prefLabel</td>
                <td>{editId === "new" ? <input className="form-control" value={editConcept.prefLabel || concept.prefLabel} onChange={e => setEditConcept({...editConcept, prefLabel: e.target.value})} /> : concept.prefLabel}</td>
                </tr>
                <tr><td className="fw-500">Définition</td>
                <td>{editId === "new" ? <input className="form-control" value={editConcept.definition || concept.definition} onChange={e => setEditConcept({...editConcept, definition: e.target.value})} /> : concept.definition}</td>
                </tr>
                <tr><td className="fw-500">altLabel</td>
                <td>{editId === "new" ? <input className="form-control" value={editConcept.altLabel || concept.altLabel} onChange={e => setEditConcept({...editConcept, altLabel: e.target.value})} /> : concept.altLabel}</td>
                </tr>
                <tr><td className="fw-500">Broader</td>
                <td>{editId === "new" ? <input className="form-control" value={editConcept.broader || concept.broader} onChange={e => setEditConcept({...editConcept, broader: e.target.value})} /> : concept.broader}</td>
                </tr>
                <tr><td className="fw-500">Narrower</td>
                <td>{editId === "new" ? <input className="form-control" value={editConcept.narrower || concept.narrower} onChange={e => setEditConcept({...editConcept, narrower: e.target.value})} /> : concept.narrower}</td>
                </tr>
                <tr><td className="fw-500">Modèle</td><td>{concept.model_id}</td></tr>
                <tr><td className="fw-500">Prompt</td><td>{concept.prompt_id}</td></tr>
                <tr><td className="fw-500">Itération</td><td>{concept.iteration}</td></tr>
            </tbody>
            </table>

            <input
            type="text"
            className="form-control mb-3"
            placeholder="Votre nom complet (validateur)..."
            value={validatedBy}
            onChange={e => setValidatedBy(e.target.value)}
            />

            <div className="d-flex gap-2">
            {editId === "new" ? (
                <button className="btn btn-accent" onClick={() => {
                setConcept({...concept, ...editConcept})
                setEditId(null)
                }}>✅ Sauvegarder corrections</button>
            ) : (
                <>
                <button className="btn btn-accent" onClick={validateConcept} disabled={!validatedBy}>✅ Valider</button>
                <button className="btn btn-edit-sm" onClick={() => { setEditId("new"); setEditConcept({...concept}) }}>✏️ Corriger</button>
                <button className="btn btn-delete-sm" onClick={rejectConcept}>❌ Rejeter</button>
                </>
            )}
            </div>
        </div>
        )}

        {/* TABLEAU CONCEPTS VALIDÉS */}
        <div className="section-card mb-3">
        <div className="section-title">Concepts générés</div>
        <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
            <thead>
                <tr>
                <th>Terme</th>
                <th>prefLabel</th>
                <th>Définition</th>
                <th>altLabel</th>
                <th>Broader</th>
                <th>Narrower</th>
                <th>Modèle</th>
                <th>Prompt</th>
                <th>Itération</th>
                <th>Statut</th>
                <th>Validé par</th>
                <th>Date</th>
                <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {concepts.map(c => (
                <tr key={c.id}>
                    <td className="fw-500">{c.terme}</td>
                    <td>{c.prefLabel}</td>
                    <td>{c.definition}</td>
                    <td>{c.altLabel}</td>
                    <td>{c.broader}</td>
                    <td>{c.narrower}</td>
                    <td className="id-cell">{c.model_id}</td>
                    <td className="id-cell">{c.prompt_id}</td>
                    <td>{c.iteration}</td>
                    <td>
                    <span className={c.statut === "validé" ? "badge-ok" : "badge-pend"}>
                        {c.statut}
                    </span>
                    </td>
                    <td className="id-cell">{c.validated_by}</td>
                    <td>{c.validated_at}</td>
                    <td>
                    <button className="btn btn-edit-sm" onClick={() => { setEditId(c.id); setEditConcept({...c}) }}>✏️ Modifier</button>
                    <button className="btn btn-delete-sm" onClick={() => deleteConcept(c.id)}>🗑 Supprimer</button>
                    </td>
                </tr>
                ))}
            </tbody>
            </table>
        </div>
        </div>
        <div className="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
          <span className="count-info">{concepts.length} concepts générés</span>
        <button className="btn btn-accent" onClick={deleteAllConcepts}>
            🗑 Supprimer tout
        </button>
          <button className="btn btn-accent">
            Passer au thésaurus →
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

export default Concepts