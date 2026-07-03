import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import "./termes.css"

function Alignements() {

  const navigate = useNavigate()
  const [thesauriTac, setThesauriTac] = useState([])
  const [thesauriArango, setThesauriArango] = useState([])
  const [selectedTac, setSelectedTac] = useState(null)
  const [selectedArango, setSelectedArango] = useState("")
  const [alignementsGeneres, setAlignementsGeneres] = useState([])
  const [alignements, setAlignements] = useState([])
  const [loading, setLoading] = useState(false)
  const [validatedBy, setValidatedBy] = useState("")
  const [editId, setEditId] = useState(null)
  const [editData, setEditData] = useState({})
  const [refresh, setRefresh] = useState(0)
  const [showPrompt, setShowPrompt] = useState(false)
  const [promptText, setPromptText] = useState("")
  const [defaultPromptText, setDefaultPromptText] = useState("")
  const [error, setError] = useState("")

  useEffect(() => {
    fetch("http://localhost:8002/thesaurus")
      .then(res => res.json())
      .then(data => setThesauriTac(data["thesauri"].filter(t => t.statut === "validé")))
  }, [])

  useEffect(() => {
    fetch("http://localhost:8004/alignements/arango/thesauri")
      .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.detail || `Erreur ${res.status}`) })
        return res.json()
      })
      .then(data => setThesauriArango(data["thesauri"] || []))
      .catch(err => setError(`ArangoDB inaccessible : ${err.message}. Vérifiez qu'ArangoDB tourne sur le port 8529.`))
  }, [])


  useEffect(() => {
    fetch("http://localhost:8004/alignements")
      .then(res => res.json())
      .then(data => setAlignements(data.alignements || []))
  }, [refresh])


  function togglePromptEditor() {
    if (!showPrompt && !defaultPromptText) {
      fetch("http://localhost:8004/alignements/prompt")
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

  function generateAlignements() {
    if (!selectedTac || !selectedArango) return
    setLoading(true)
    setAlignementsGeneres([])
    setError("")
    const isCustomPrompt = promptText && promptText !== defaultPromptText
    fetch("http://localhost:8004/alignements/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        thesaurus_tac_id: selectedTac.id,
        thesaurus_arango_nom: selectedArango,
        prompt_template: isCustomPrompt ? promptText : null
      })
    })
      .then(res => res.json().then(data => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) {
          setError(data.detail || "Erreur lors de la génération des alignements.")
        } else {
          setAlignementsGeneres(data.alignements || [])
        }
        setLoading(false)
      })
      .catch(err => {
         console.error("Erreur generation :", err)
         setError("Impossible de contacter le serveur d'alignements.")
         setLoading(false)
      })
  }


  function validateAlignement(a) {
    if (!validatedBy) return
    fetch("http://localhost:8004/alignements/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...a, validated_by: validatedBy, statut: "validé" })
    })
      .then(() => {
        setAlignementsGeneres(alignementsGeneres.filter(al => al !== a))
        setRefresh(prev => prev + 1)
      })
  }


  function rejectAlignement(a) {
    fetch("http://localhost:8004/alignements/reject", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...a, validated_by: validatedBy || "—", statut: "rejeté" })
    })
      .then(() => {
        setAlignementsGeneres(alignementsGeneres.filter(al => al !== a))
        setRefresh(prev => prev + 1)
      })
  }


  function updateAlignement(id) {
    fetch(`http://localhost:8004/alignements/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(editData)
    })
      .then(() => {
        setAlignements(alignements.map(a => a.id === id ? { ...a, ...editData } : a))
        setEditId(null)
        setEditData({})
      })
  }

 
  function deleteAlignement(id) {
    if (!window.confirm("Supprimer cet alignement ?")) return
    fetch(`http://localhost:8004/alignements/${id}`, { method: "DELETE" })
      .then(() => setAlignements(alignements.filter(a => a.id !== id)))
  }


  function deleteAll() {
    if (!window.confirm("Supprimer tous les alignements ?")) return
    fetch("http://localhost:8004/alignements", { method: "DELETE" })
      .then(() => setAlignements([]))
  }

  return (
    <div>
      <nav className="navbar navbar-light sticky-top px-4">
        <span className="nav-logo">TAC — Thésaurus Automatisé par Curation</span>
        <div className="d-flex gap-2">
          <Link to="/"><span className="step">Termes</span></Link>
          <Link to="/concepts"><span className="step">Concepts</span></Link>
          <Link to="/thesaurus"><span className="step">Thésaurus</span></Link>
          <Link to="/alignements"><span className="step active">Alignements</span></Link>
          <Link to="/export"><span className="step">Export</span></Link>
        </div>
      </nav>

      <div className="container-fluid main">

        <div className="mb-4">
          <h1 className="page-title">Gestion des alignements</h1>
        </div>

        {/* STATS */}
        <div className="row g-3 mb-4">
          <div className="col-4">
            <div className="stat-card">
              <div className="stat-label">Total alignements</div>
              <div className="stat-value text-dark">{alignements.length}</div>
            </div>
          </div>
          <div className="col-4">
            <div className="stat-card">
              <div className="stat-label">Validés</div>
              <div className="stat-value color-ok">
                {alignements.filter(a => a.statut === "validé").length}
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="stat-card">

              <div className="stat-label">Rejetés</div>
              <div className="stat-value" style={{color: "#c0392b"}}>
                {alignements.filter(a => a.statut === "rejeté").length}
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 1 : Sélection */}
        <div className="section-card mb-3">
          <div className="section-title">Sélectionner les thésauri</div>
          <div className="row g-3 mb-3">
            <div className="col-6">
              <label className="form-label fw-500">Thésaurus TAC</label>
              <select
                className="form-control"
                onChange={e => setSelectedTac(thesauriTac.find(t => t.id === e.target.value))}
              >
                <option value="">-- Choisir un thésaurus TAC --</option>
                {thesauriTac.map(t => (
                  <option key={t.id} value={t.id}>{t.nom}</option>
                ))}
              </select>
            </div>
            <div className="col-6">
              <label className="form-label fw-500">Thésaurus externe (ArangoDB)</label>
              <select
                className="form-control"
                onChange={e => setSelectedArango(e.target.value)}>
                <option value="">-- Choisir un thésaurus externe --</option>
                {thesauriArango.map((t, i) => (
                  <option key={i} value={t['title']}>{t['title']}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="d-flex gap-2 mb-3">
            <button
              className="btn btn-accent"
              onClick={generateAlignements}
              disabled={!selectedTac || !selectedArango || loading}
            >
              {loading ? "Génération en cours..." : "▶ Générer les alignements"}
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
                Utilise <code>{"{tac_text}"}</code>, <code>{"{arango_text}"}</code> et <code>{"{thesaurus_arango_nom}"}</code> comme emplacements — ce prompt n'est utilisé que pour cette génération.
              </div>
            </div>
          )}

          {error && (
            <div className="alert alert-danger mt-2">⚠️ {error}</div>
          )}
        </div>

        {/* SECTION 2 : Alignements générés */}
        {alignementsGeneres.length > 0 && (
          <div className="section-card mb-3">
            <div className="section-title">Alignements générés</div>
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
                    <th>Thésaurus </th>
                    <th>Concept</th>
                    <th>Type d'alignement</th>
                    <th>Thésaurus externe</th>
                    <th>Concept externe</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {alignementsGeneres.map((a, i) => (
                    <tr key={i}>
                      <td>{a.thesaurus_tac_nom}</td>
                      <td className="fw-500">{a.concept_tac_label}</td>
                      <td>
                        <span className={a.type_alignement === "exactMatch" ? "badge-ok" : a.type_alignement === "noMatch" ? "badge-src" : "badge-pend"}>
                          {a.type_alignement}
                        </span>
                      </td>
                      <td>{a.thesaurus_arango_nom}</td>
                      <td>{a.concept_externe_label}</td>
                      <td>
                        <button className="btn btn-accent btn-sm me-1" onClick={() => validateAlignement(a)} disabled={!validatedBy}>
                          ✅ Valider
                        </button>
                        <button className="btn btn-delete-sm" onClick={() => rejectAlignement(a)}>
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

        {/* SECTION 3 : Liste alignements */}
        <div className="section-card mb-3">
          <div className="section-title">Liste des alignements</div>
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead>
                <tr>
                  <th>Thésaurus </th>
                  <th>Concept </th>
                  <th>Type d'alignement</th>
                  <th>Thésaurus externe</th>
                  <th>Concept externe</th>
                  <th>Statut</th>
                  <th>Validé par</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alignements.map(a => (
                  <tr key={a.id}>
                    <td>{a.thesaurus_tac_nom}</td>
                    <td className="fw-500">{a.concept_tac_label}</td>
                    <td>
                      {editId === a.id ? (
                        <select className="form-control" value={editData.type_alignement} onChange={e => setEditData({...editData, type_alignement: e.target.value})}>
                          <option value="exactMatch">exactMatch</option>
                          <option value="closeMatch">closeMatch</option>
                          <option value="noMatch">noMatch</option>
                        </select>
                      ) : (
                        <span className={a.type_alignement === "exactMatch" ? "badge-ok" : a.type_alignement === "noMatch" ? "badge-src" : "badge-pend"}>
                          {a.type_alignement}
                        </span>
                      )}
                    </td>
                    <td>{a.thesaurus_arango_nom}</td>
                    <td>{a.concept_externe_label}</td>
                    <td>
                      <span className={a.statut === "validé" ? "badge-ok" : "badge-pend"}>
                        {a.statut}
                      </span>
                    </td>
                    <td className="id-cell">{a.validated_by}</td>
                    <td>{a.validated_at}</td>
                    <td>
                      {editId === a.id ? (
                        <button className="btn btn-accent" onClick={() => updateAlignement(a.id)}>✅ Sauvegarder</button>
                      ) : (
                        <button className="btn btn-edit-sm" onClick={() => { setEditId(a.id); setEditData({type_alignement: a.type_alignement, uri_externe: a.uri_externe}) }}>✏️ Modifier</button>
                      )}
                      <button className="btn btn-delete-sm" onClick={() => deleteAlignement(a.id)}>🗑 Supprimer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
          <span className="count-info">{alignements.length} alignements</span>
          <button className="btn btn-accent" onClick={deleteAll}>🗑 Supprimer tout</button>
          <button className="btn btn-accent" onClick={() => navigate("/export")}>
            Passer à l'export →
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

export default Alignements