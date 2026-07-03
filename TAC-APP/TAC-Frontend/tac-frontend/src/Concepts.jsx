import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import "./termes.css"

function Concepts() {

  const [termes, setTermes] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [search, setSearch] = useState("")
  const [generatedConcepts, setGeneratedConcepts] = useState([])
  const [loading, setLoading] = useState(false)
  const [concepts, setConcepts] = useState([])
  const [validatedBy, setValidatedBy] = useState("")
  const [editId, setEditId] = useState(null)
  const [editConcept, setEditConcept] = useState({})
  const [showPrompt, setShowPrompt] = useState(false)
  const [promptText, setPromptText] = useState("")
  const [defaultPromptText, setDefaultPromptText] = useState("")
  const [error, setError] = useState("")
  const [showManuelForm, setShowManuelForm] = useState(false)
  const [manuelForm, setManuelForm] = useState({ terme: "", prefLabel: "", definition: "", altLabel: "", broader: "", narrower: "", validated_by: "" })
  const [manuelError, setManuelError] = useState("")
  const [manuelSuccess, setManuelSuccess] = useState("")
  const navigate = useNavigate()



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

  function toggleTerme(id) {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  function togglePromptEditor() {
    if (!showPrompt && !defaultPromptText) {
      fetch("http://localhost:8001/concepts/prompt")
        .then(res => res.json())
        .then(data => {
          setDefaultPromptText(data.prompt_template)
          setPromptText(data.prompt_template)
        })
    }
    setShowPrompt(!showPrompt)
  }

  function resetPrompt() {
    setPromptText(defaultPromptText)
  }

  function generateConcepts() {
    if (selectedIds.length === 0) return
    setLoading(true)
    setGeneratedConcepts([])
    setError("")
    const termesPayload = termes
      .filter(t => selectedIds.includes(t.id))
      .map(t => ({ id: t.id, label: t.label }))
    const isCustomPrompt = promptText && promptText !== defaultPromptText

    fetch("http://localhost:8001/concepts/generate-batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        termes: termesPayload,
        prompt_template: isCustomPrompt ? promptText : null
      })
    })
      .then(res => res.json().then(data => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) {
          setError(data.detail || "Erreur lors de la génération des concepts.")
        } else {
          setGeneratedConcepts(data.concepts || [])
        }
        setLoading(false)
      })
      .catch(() => {
        setError("Impossible de contacter le serveur de concepts.")
        setLoading(false)
      })
  }


  function validateGeneratedConcept(c) {
    if (!validatedBy) return
    fetch("http://localhost:8001/concepts/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...c, validated_by: validatedBy })
    })
      .then(() => {
        setGeneratedConcepts(prev => prev.filter(g => g !== c))
        setTermes(prev => prev.filter(t => t.id !== c.terme_id))
        setSelectedIds(prev => prev.filter(id => id !== c.terme_id))
        fetch("http://localhost:8001/concepts")
          .then(res => res.json())
          .then(data => setConcepts(data.concepts))
      })
  }


  function rejectGeneratedConcept(c) {
    fetch("http://localhost:8001/concepts/reject", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(c)
    })
      .then(() => {
        setGeneratedConcepts(prev => prev.filter(g => g !== c))
        fetch("http://localhost:8001/concepts")
          .then(res => res.json())
          .then(data => setConcepts(data.concepts))
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
        body: JSON.stringify({
            prefLabel: editConcept.prefLabel,
            definition: editConcept.definition,
            altLabel: editConcept.altLabel,
            broader: editConcept.broader,
            narrower: editConcept.narrower,
        })
    })
    .then(() => {
        setConcepts(concepts.map(c => c.id === id ? { ...c, ...editConcept } : c))
        setEditId(null)
        setEditConcept({})
    })
   }

  function createConceptManuel(e) {
    e.preventDefault()
    setManuelError("")
    setManuelSuccess("")
    if (!manuelForm.terme.trim()) { setManuelError("Le nom du terme est obligatoire."); return }
    if (!manuelForm.validated_by.trim()) { setManuelError("Le nom du validateur est obligatoire."); return }
    fetch("http://localhost:8001/concepts/manuel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(manuelForm)
    })
      .then(res => res.json().then(data => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) { setManuelError(data.detail || "Erreur lors de la création."); return }
        setManuelSuccess("Concept créé avec succès.")
        setManuelForm({ terme: "", prefLabel: "", definition: "", altLabel: "", broader: "", narrower: "", validated_by: "" })
        fetch("http://localhost:8001/concepts")
          .then(res => res.json())
          .then(data => setConcepts(data.concepts))
      })
      .catch(() => setManuelError("Impossible de contacter le serveur."))
  }

  return (
    <div>
      <nav className="navbar navbar-light sticky-top px-4">
        <span className="nav-logo">TAC — Thésaurus Automatisé par Curation</span>
        <div className="d-flex gap-2">
          <Link to="/"><span className="step">Termes</span></Link>
          <Link to="/concepts"><span className="step active">Concepts</span></Link>
          <Link to="/thesaurus"><span className="step">Thésaurus</span></Link>
          <Link to="/alignements"><span className="step">Alignements</span></Link>
          <Link to="/export"><span className="step">Export</span></Link>
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

        {/* SÉLECTION TERMES */}
        <div className="section-card mb-3">
          <div className="section-title">Sélectionner un ou plusieurs termes</div>
          <input
            type="text"
            className="form-control mb-2"
            placeholder="🔍 Rechercher un terme..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <div className="mb-3" style={{ maxHeight: "220px", overflowY: "auto", border: "1px solid var(--border)", borderRadius: "8px", padding: "8px" }}>
            {termesFiltered.length === 0 ? (
              <div className="text-muted px-2 py-1">Aucun terme trouvé</div>
            ) : (
              termesFiltered.map(t => (
                <label key={t.id} className="d-flex align-items-center gap-2 px-2 py-1" style={{ cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(t.id)}
                    onChange={() => toggleTerme(t.id)}
                  />
                  {t.label}
                </label>
              ))
            )}
          </div>

          <div className="d-flex gap-2 mb-3">
            <button
              className="btn btn-accent"
              onClick={generateConcepts}
              disabled={selectedIds.length === 0 || loading}
            >
              {loading ? "Génération en cours..." : `▶ Générer ${selectedIds.length > 1 ? `les ${selectedIds.length} concepts` : "le concept"}`}
            </button>
            <button className="btn btn-edit-sm" onClick={togglePromptEditor}>
              📝 {showPrompt ? "Masquer le prompt" : "Modifier le prompt"}
            </button>
          </div>

          {showPrompt && (
            <div className="mb-2">
              <textarea
                className="form-control"
                style={{ fontFamily: "monospace", fontSize: "12px", height: "260px" }}
                value={promptText}
                onChange={e => setPromptText(e.target.value)}
              />
              <div className="d-flex gap-2 mt-2">
                <button className="btn btn-edit-sm" onClick={resetPrompt}>↺ Réinitialiser au prompt par défaut</button>
              </div>
              <div className="text-muted" style={{ fontSize: "12px", marginTop: "4px" }}>
                Utilise <code>{"{terme}"}</code> comme emplacement du terme — ce prompt n'est utilisé que pour cette génération.
              </div>
            </div>
          )}

          {error && (
            <div className="alert alert-danger mt-2">⚠️ {error}</div>
          )}
        </div>

        {/* RÉSULTATS GÉNÉRÉS */}
        {generatedConcepts.length > 0 && (
        <div className="section-card mb-3">
            <div className="section-title">Concepts générés</div>
            <input
            type="text"
            className="form-control mb-3"
            placeholder="Votre nom complet (validateur)..."
            value={validatedBy}
            onChange={e => setValidatedBy(e.target.value)}
            />
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Terme</th>
                    <th>Définition</th>
                    <th>altLabel</th>
                    <th>Broader</th>
                    <th>Narrower</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {generatedConcepts.map((c, i) => (
                    <tr key={i}>
                      <td className="fw-500">{c.prefLabel}</td>
                      <td>{c.definition}</td>
                      <td>{c.altLabel}</td>
                      <td>{c.broader}</td>
                      <td>{c.narrower}</td>
                      <td>
                        <button className="btn btn-accent btn-sm me-1" onClick={() => validateGeneratedConcept(c)} disabled={!validatedBy}>
                          ✅ Valider
                        </button>
                        <button className="btn btn-delete-sm" onClick={() => rejectGeneratedConcept(c)}>
                          ❌ Rejeter
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
        </div>
        )}

        {/* AJOUT MANUEL D'UN CONCEPT */}
        <div className="section-card mb-3">
          <div className="d-flex justify-content-between align-items-center">
            <div className="section-title mb-0">Ajouter un concept manuellement</div>
            <button className="btn btn-edit-sm" onClick={() => { setShowManuelForm(!showManuelForm); setManuelError(""); setManuelSuccess("") }}>
              {showManuelForm ? "▲ Masquer" : "➕ Nouveau concept"}
            </button>
          </div>

          {showManuelForm && (
            <form onSubmit={createConceptManuel} className="mt-3">
              <div className="row g-2">
                <div className="col-md-4">
                  <label className="form-label fw-bold">Terme (nom) <span className="text-danger">*</span></label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Ex : Peinture"
                    value={manuelForm.terme}
                    onChange={e => setManuelForm({ ...manuelForm, terme: e.target.value })}
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">prefLabel</label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Étiquette préférée (optionnel)"
                    value={manuelForm.prefLabel}
                    onChange={e => setManuelForm({ ...manuelForm, prefLabel: e.target.value })}
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">altLabel</label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Synonymes (optionnel)"
                    value={manuelForm.altLabel}
                    onChange={e => setManuelForm({ ...manuelForm, altLabel: e.target.value })}
                  />
                </div>
                <div className="col-md-12">
                  <label className="form-label">Définition</label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Définition du concept (optionnel)"
                    value={manuelForm.definition}
                    onChange={e => setManuelForm({ ...manuelForm, definition: e.target.value })}
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Broader (concept parent)</label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Concept plus large (optionnel)"
                    value={manuelForm.broader}
                    onChange={e => setManuelForm({ ...manuelForm, broader: e.target.value })}
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Narrower (concepts enfants)</label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Concepts plus spécifiques (optionnel)"
                    value={manuelForm.narrower}
                    onChange={e => setManuelForm({ ...manuelForm, narrower: e.target.value })}
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label fw-bold">Validé par <span className="text-danger">*</span></label>
                  <input
                    className="form-control form-control-sm"
                    placeholder="Votre nom complet"
                    value={manuelForm.validated_by}
                    onChange={e => setManuelForm({ ...manuelForm, validated_by: e.target.value })}
                  />
                </div>
              </div>
              {manuelError && <div className="alert alert-danger mt-2 py-1">⚠️ {manuelError}</div>}
              {manuelSuccess && <div className="alert alert-success mt-2 py-1">✅ {manuelSuccess}</div>}
              <div className="mt-3">
                <button type="submit" className="btn btn-accent">➕ Créer le concept</button>
              </div>
            </form>
          )}
        </div>

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
                    <td>
                    {editId === c.id
                        ? <input className="form-control form-control-sm" value={editConcept.prefLabel || ""} onChange={e => setEditConcept({...editConcept, prefLabel: e.target.value})} />
                        : c.prefLabel}
                    </td>
                    <td>
                    {editId === c.id
                        ? <input className="form-control form-control-sm" value={editConcept.definition || ""} onChange={e => setEditConcept({...editConcept, definition: e.target.value})} />
                        : c.definition}
                    </td>
                    <td>
                    {editId === c.id
                        ? <input className="form-control form-control-sm" value={editConcept.altLabel || ""} onChange={e => setEditConcept({...editConcept, altLabel: e.target.value})} />
                        : c.altLabel}
                    </td>
                    <td>
                    {editId === c.id
                        ? <input className="form-control form-control-sm" value={editConcept.broader || ""} onChange={e => setEditConcept({...editConcept, broader: e.target.value})} />
                        : c.broader}
                    </td>
                    <td>
                    {editId === c.id
                        ? <input className="form-control form-control-sm" value={editConcept.narrower || ""} onChange={e => setEditConcept({...editConcept, narrower: e.target.value})} />
                        : c.narrower}
                    </td>
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
                    {editId === c.id ? (
                        <>
                        <button className="btn btn-accent btn-sm me-1" onClick={() => updateConcept(c.id)}>💾 Sauvegarder</button>
                        <button className="btn btn-edit-sm" onClick={() => { setEditId(null); setEditConcept({}) }}>✖ Annuler</button>
                        </>
                    ) : (
                        <>
                        <button className="btn btn-edit-sm" onClick={() => { setEditId(c.id); setEditConcept({...c}) }}>✏️ Modifier</button>
                        <button className="btn btn-delete-sm" onClick={() => deleteConcept(c.id)}>🗑 Supprimer</button>
                        </>
                    )}
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
          <button className="btn btn-accent" onClick={() => navigate("/thesaurus")}>
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
