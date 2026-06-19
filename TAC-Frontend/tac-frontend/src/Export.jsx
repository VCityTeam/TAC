import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import "./termes.css"

const API = "http://localhost:8005"

export default function Export() {
  const [thesauri, setThesauri] = useState([])
  const [exports, setExports] = useState([])
  const [selectedThesaurus, setSelectedThesaurus] = useState("")
  const [loading, setLoading] = useState(false)
  const [exportActif, setExportActif] = useState(null)
  const [message, setMessage] = useState("")

  useEffect(() => {
    fetch("http://localhost:8002/thesaurus")
      .then(res => res.json())
      .then(data => setThesauri(data["thesauri"] || []))
  }, [])

  const loadExports = () => {
    fetch(`${API}/export`)
      .then(res => res.json())
      .then(data => setExports(data["exports"] || []))
  }

  useEffect(() => { loadExports() }, [])

  const genererExport = () => {
    if (!selectedThesaurus) return setMessage("⚠️ Sélectionne un thésaurus")
    setLoading(true)
    setMessage("")
    fetch(`${API}/export/generate?thesaurus_id=${selectedThesaurus}`, { method: "POST" })
      .then(res => res.json())
      .then(data => {
        setExportActif(data)
        setMessage("✅ Export SKOS généré avec succès !")
        loadExports()
      })
      .catch(() => setMessage("❌ Erreur lors de la génération"))
      .finally(() => setLoading(false))
  }

  const telecharger = (exportId, nom) => {
    fetch(`${API}/export/${exportId}/download`)
      .then(res => res.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `${nom}.ttl`
        a.click()
        window.URL.revokeObjectURL(url)
      })
  }

  const voirExport = (exportId) => {
    fetch(`${API}/export/${exportId}`)
      .then(res => res.json())
      .then(data => setExportActif(data))
  }

  const envoyerOpentheso = (exportId) => {
    fetch(`${API}/export/${exportId}/opentheso`, { method: "POST" })
      .then(res => res.json())
      .then(() => {
        setMessage("✅ Envoyé vers Opentheso !")
        loadExports()
      })
      .catch(() => setMessage("❌ Erreur Opentheso"))
  }

  const supprimerExport = (exportId) => {
    if (!window.confirm("Supprimer cet export ?")) return
    fetch(`${API}/export/${exportId}`, { method: "DELETE" })
      .then(() => {
        setMessage("🗑️ Export supprimé")
        loadExports()
        if (exportActif?.id === exportId) setExportActif(null)
      })
  }

  const totalExports = exports.length
  const exportsGeneres = exports.filter(e => e.statut === "généré").length
  const exportsModifies = exports.filter(e => e.statut === "modifié").length
  const exportsEnvoyes = exports.filter(e => e.statut === "envoyé Opentheso").length

  return (
    <div>
      {/* ── NAVBAR ── */}
      <nav className="navbar navbar-light sticky-top px-4">
        <span className="nav-logo">TAC — Thésaurus Automatisé par Curation</span>
        <div className="d-flex gap-2">
          <Link to="/"><span className="step">Termes</span></Link>
          <Link to="/concepts"><span className="step">Concepts</span></Link>
          <Link to="/thesaurus"><span className="step">Thésaurus</span></Link>
          <Link to="/alignements"><span className="step">Alignements</span></Link>
          <Link to="/export"><span className="step active">Export</span></Link>
        </div>
      </nav>

      <div className="container-fluid main">

        {/* ── TITRE ── */}
        <div className="mb-4">
          <h1 className="page-title">Export SKOS</h1>
        </div>

        {/* ── STATS ── */}
        <div className="row g-3 mb-4">
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Total exports</div>
              <div className="stat-value text-dark">{totalExports}</div>
            </div>
          </div>
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Générés</div>
              <div className="stat-value" style={{ color: "#1e3a6e" }}>{exportsGeneres}</div>
            </div>
          </div>
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Modifiés</div>
              <div className="stat-value color-warn">{exportsModifies}</div>
            </div>
          </div>
          <div className="col-3">
            <div className="stat-card">
              <div className="stat-label">Envoyés Opentheso</div>
              <div className="stat-value color-ok">{exportsEnvoyes}</div>
            </div>
          </div>
        </div>

        {message && (
          <div className={`alert ${message.startsWith("❌") ? "alert-danger" : "alert-success"} mb-4`}>
            {message}
          </div>
        )}

        {/* ── GÉNÉRATION ── */}
        <div className="card mb-4">
          <div className="card-header" style={{ backgroundColor: "#1e3a6e", color: "white" }}>
            Générer un export SKOS
          </div>
          <div className="card-body">
            <div className="row align-items-end">
              <div className="col-md-6">
                <label className="form-label">Sélectionner un thésaurus TAC</label>
                <select
                  className="form-control"
                  value={selectedThesaurus}
                  onChange={e => setSelectedThesaurus(e.target.value)}>
                  <option value="">-- Choisir un thésaurus --</option>
                  {thesauri.map(t => (
                    <option key={t.id} value={t.id}>{t.nom}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-3">
                <button
                  className="btn w-100"
                  style={{ backgroundColor: "#1e3a6e", color: "white" }}
                  onClick={genererExport}
                  disabled={loading}>
                  {loading ? "Génération..." : "🔄 Générer SKOS"}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── TABLEAU EXPORTS ── */}
        <div className="card mb-4">
          <div className="card-header" style={{ backgroundColor: "#1e3a6e", color: "white" }}>
            📋 Exports générés
          </div>
          <div className="card-body p-0">
            <table className="table table-hover mb-0">
              <thead style={{ backgroundColor: "#f0f4ff" }}>
                <tr>
                  <th>Thésaurus</th>
                  <th>Nom</th>
                  <th>Date de création</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {exports.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center text-muted py-3">
                      Aucun export généré
                    </td>
                  </tr>
                ) : (
                  exports.map(e => (
                    <tr key={e.id}>
                      <td>{e.thesaurus_nom}</td>
                      <td>{e.nom}</td>
                      <td>{e.date_creation?.slice(0, 10)}</td>
                      <td>
                        <span className={`badge ${
                          e.statut === "envoyé Opentheso" ? "bg-success" :
                          e.statut === "modifié" ? "bg-warning text-dark" : "bg-primary"
                        }`}>
                          {e.statut}
                        </span>
                      </td>
                      <td>
                        <button
                          className="btn btn-sm btn-outline-primary me-1"
                          onClick={() => voirExport(e.id)}>
                          👁️ Voir
                        </button>
                        <button
                          className="btn btn-sm btn-outline-success me-1"
                          onClick={() => telecharger(e.id, e.nom)}>
                          ⬇️ .ttl
                        </button>
                        <button
                          className="btn btn-sm btn-outline-warning me-1"
                          onClick={() => envoyerOpentheso(e.id)}
                          disabled={e.envoye_opentheso}>
                          🚀 Opentheso
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => supprimerExport(e.id)}>
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── VISUALISATION SKOS ── */}
        {exportActif && (
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center"
              style={{ backgroundColor: "#1e3a6e", color: "white" }}>
              <span>📄 {exportActif.nom}</span>
              <div>
                <button
                  className="btn btn-sm btn-light me-2"
                  onClick={() => telecharger(exportActif.id, exportActif.nom)}>
                  ⬇️ Télécharger
                </button>
                <button
                  className="btn btn-sm btn-outline-light"
                  onClick={() => setExportActif(null)}>
                  ✕ Fermer
                </button>
              </div>
            </div>
            <div className="card-body p-0">
              <textarea
                className="form-control"
                style={{
                  fontFamily: "monospace",
                  fontSize: "13px",
                  height: "400px",
                  border: "none",
                  borderRadius: 0,
                  backgroundColor: "#1e1e1e",
                  color: "#d4d4d4",
                  padding: "16px"
                }}
                value={exportActif.contenu_ttl || ""}
                onChange={e => setExportActif({ ...exportActif, contenu_ttl: e.target.value })}
              />
            </div>
            <div className="card-footer d-flex justify-content-between align-items-center">
              <span className="text-muted">Thésaurus : {exportActif.thesaurus_nom}</span>
              <div>
                <button
                  className="btn btn-sm me-2"
                  style={{ backgroundColor: "#1e3a6e", color: "white" }}
                  onClick={() => {
                    fetch(`${API}/export/${exportActif.id}?contenu_ttl=${encodeURIComponent(exportActif.contenu_ttl)}`, {
                      method: "PUT"
                    }).then(() => {
                      setMessage("✅ Modifications sauvegardées")
                      loadExports()
                    })
                  }}>
                  💾 Sauvegarder
                </button>
                <button
                  className="btn btn-sm btn-outline-warning"
                  onClick={() => envoyerOpentheso(exportActif.id)}>
                  🚀 Envoyer vers Opentheso
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}