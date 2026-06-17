import { useState, useEffect } from "react"
import "./termes.css"
import { Link, useNavigate } from "react-router-dom"




function Termes() {

  const navigate = useNavigate()
  const [termes, setTermes] = useState([])
  const [input, setInput] = useState("")
  const [editId, setEditId] = useState(null)
  const [editLabel, setEditLabel] = useState("")
  const [search, setSearch] = useState("")

  useEffect(() => {
    fetch("http://localhost:8000/termes")
      .then(res => res.json())
      .then(data => setTermes(data.termes))
  }, [])

    function addTerme() {
    if (!input) return
    fetch("http://localhost:8000/terme", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label: input })
    })
        .then(res => res.json())
        .then(data => {
        setTermes([...termes, { 
            id: data.id, 
            label: data.label, 
            created_at: data.created_at,
            updated_at: null,
            statut : "en attente"
        }])
        setInput("")
        })
    }

  function deleteTerme(id) {
    fetch(`http://localhost:8000/terme/${id}`, { method: "DELETE" })
      .then(() => setTermes(termes.filter(t => t.id !== id)))
  }

function updateTerme(id) {
fetch(`http://localhost:8000/terme/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label: editLabel })
})
    .then(res => res.json())
    .then(data => {
    setTermes(termes.map(t => t.id === id ? { 
        ...t, 
        label: editLabel, 
        updated_at: data.updated_at 
    } : t))
    setEditId(null)
    setEditLabel("")
    })
}

  function searchTerme(q) {
    setSearch(q)
    if (q === "") {
        fetch("http://localhost:8000/termes")
        .then(res => res.json())
        .then(data => setTermes(data.termes))
    } else {
        fetch(`http://localhost:8000/termes/search?q=${q}`)
        .then(res => res.json())
        .then(data => setTermes(data.termes))
    }
}

    function deleteAll() {
        if (!window.confirm("Supprimer tous les termes ?")) return
        fetch("http://localhost:8000/termes", { method: "DELETE" })
            .then(() => setTermes([]))
        }
    function importFile(e) {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = function(ev) {
        const content = ev.target.result
        let termes = []
        if (file.name.endsWith(".json")) {
        termes = JSON.parse(content)
        } else {
        termes = content.split("\n")
            .map(l => l.trim())
            .filter(Boolean)
            .map(l => ({ label: l }))
        }
    fetch("http://localhost:8000/termes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(termes)
    })
      .then(() => {                                        // ← ici
        fetch("http://localhost:8000/termes")
          .then(res => res.json())
          .then(data => setTermes(data.termes || []))
      })  
    }
    reader.readAsText(file)
    }


return (
  <div>
    <nav className="navbar navbar-light sticky-top px-4">
      <span className="nav-logo">TAC — Thésaurus Automatisé par Curation</span>
      <div className="d-flex gap-2">
        <Link to="/"><span className="step active">Termes</span></Link>
          <Link to="/concepts"><span className="step">Concepts</span></Link>
          <Link to="/thesaurus"><span className="step">Thésaurus</span></Link>
          <Link to="/alignements"><span className="step">Alignements</span></Link>
        <span className="step">Export</span>
      </div>
    </nav>

    <div className="container-fluid main">

      <div className="mb-4">
        <h1 className="page-title">Gestion des termes</h1>
      </div>

      {/* STATS */}
    <div className="row g-3 mb-4">
    <div className="col-3">
        <div className="stat-card">
        <div className="stat-label">Total termes</div>
        <div className="stat-value text-dark">{termes.length}</div>
        </div>
    </div>
    <div className="col-3">
        <div className="stat-card">
        <div className="stat-label">En attente</div>
        <div className="stat-value color-warn">
            {termes.filter(t => t.statut === "en attente").length}
        </div>
        </div>
    </div>
    <div className="col-3">
        <div className="stat-card">
        <div className="stat-label">Validés</div>
        <div className="stat-value color-ok">
            {termes.filter(t => t.statut === "validé").length}
        </div>
        </div>
    </div>
    <div className="col-3">
        <div className="stat-card">
        <div className="stat-label">Rejetés</div>
        <div className="stat-value" style={{color: "#c0392b"}}>
            {termes.filter(t => t.statut === "rejeté").length}
        </div>
        </div>
    </div>
    </div>

      {/* SAISIE */}
      <div className="section-card mb-3">
        <div className="section-title">Saisir un terme</div>
        <div className="d-flex gap-2">
          <input
            type="text"
            className="form-control"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addTerme()}
            placeholder="Ex : arc triomphal, pilastre, mortaise…"
          />
          <button className="btn btn-accent" onClick={addTerme}>Ajouter</button>
        </div>
      </div>

      {/* IMPORT */}
      <div className="section-card mb-3">
        <div className="section-title">Importer une liste</div>
        <div className="file-zone" onClick={() => document.getElementById('file-input').click()}>
          <div className="file-icon">📂</div>
          <p className="text-muted mb-1">Glisser un fichier ici ou <strong>cliquer pour sélectionner</strong></p>
          <div className="d-flex gap-2 justify-content-center mt-2">
            <span className="fmt-tag">CSV</span>
            <span className="fmt-tag">JSON</span>
            <span className="fmt-tag">TXT</span>
          </div>
          <input type="file" id="file-input" className="d-none" accept=".csv,.json,.txt" onChange={importFile} />
        </div>
      </div>

      {/* RECHERCHE */}
      <input
        type="text"
        className="form-control mb-3"
        value={search}
        onChange={e => searchTerme(e.target.value)}
        placeholder="🔍 Rechercher un terme…"
      />

      {/* TABLEAU */}
      <div className="section-card mb-3">
        <div className="section-title">Liste des termes</div>
        <div className="table-responsive">
          <table className="table table-hover align-middle mb-0">
            <thead>
              <tr>
                <th>#ID</th>
                <th>Terme</th>
                <th>Créé le</th>
                <th>Modifié le</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {termes.map(t => (
                <tr key={t.id}>
                  <td className="id-cell">{t.id}</td>
                  <td className="fw-500">
                    {editId === t.id ? (
                      <input
                        className="form-control"
                        value={editLabel}
                        onChange={e => setEditLabel(e.target.value)}
                      />
                    ) : t.label}
                  </td>
                  <td>{t.created_at || '—'}</td>
                  <td>{t.updated_at || '—'}</td>
                  <td>
                    <span className={t.statut === "validé" ? "badge-ok" : t.statut === "rejeté" ? "badge-pend" : "badge-pend"}>
                        {t.statut || "en attente"}
                    </span>
                </td>
                  <td>
                    {editId === t.id ? (
                      <button className="btn btn-accent" onClick={() => updateTerme(t.id)}>✅ Sauvegarder</button>
                    ) : (
                      <button className="btn btn-edit-sm" onClick={() => { setEditId(t.id); setEditLabel(t.label) }}>✏️ Modifier</button>
                    )}
                    <button className="btn btn-delete-sm" onClick={() => deleteTerme(t.id)}>🗑 Supprimer</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* FOOTER PAGE */}
      <div className="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
        <span className="count-info">{termes.length} termes chargés</span>
        <button className="btn btn-accent" onClick={deleteAll}>🗑 Supprimer tout</button>
        <button className="btn btn-accent" onClick={() => navigate("/concepts")}>
            Passer à la génération →
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

export default Termes