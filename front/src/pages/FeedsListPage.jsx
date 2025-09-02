import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';

export default function FeedListPage() {

  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const [feeds, setFeeds] = useState([]);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('');
  
  const [exportFormat, setExportFormat] = useState("json");
  const [importFile, setImportFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("Aucun fichier choisi");




  useEffect(() => {
    if (!token) {
      alert("Utilisateur non authentifié.");
      navigate("/login");
      return;
    }

    axios.get('http://localhost:8000/rss/feeds', { headers })
      .then(res => setFeeds(res.data))
      .catch(err => {
        console.error(err);
        setMessage("Erreur lors du chargement des flux.");
        setMessageType("error");
      });
  }, [token, navigate]);

  const handleDelete = (feedId) => {
    if (confirm("Voulez-vous vraiment supprimer ce flux ?")) {
      axios.delete(`http://localhost:8000/rss/feeds/${feedId}`, { headers })
        .then(() => {
          setMessage("Flux supprimé.");
          setMessageType("success");
          // Supprimer le flux localement sans recharger
          setFeeds(prevFeeds => prevFeeds.filter(feed => feed.id !== feedId));
          setTimeout(() => {
            setMessage(null);
            setMessageType('');
          }, 2000); 
        })
        .catch(err => {
          console.error(err);
          setMessage("Erreur lors de la suppression.");
          setMessageType("error");
          setTimeout(() => {
            setMessage(null);
            setMessageType('');
          }, 2000); 
        });
    }
  };

  const handleExport = () => {
    axios.get(`http://localhost:8000/rss/export?format=${exportFormat}`, {
      headers,
      responseType: 'blob' // important pour télécharger le fichier
    })
    .then(res => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rss_export.${exportFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch(err => {
      console.error(err);
      setMessage("Erreur lors de l'exportation.");
      setMessageType("error");
      setTimeout(() => {
        setMessage(null);
        setMessageType('');
        }, 2000); 
    });
  };

  const handleImport = () => {
    if (!importFile) {   
      setMessage("Veuillez sélectionner un fichier à importer.");
      setMessageType("error");
      setTimeout(() => {
        setMessage(null);
        setMessageType('');
      }, 2000);
      return;
    }

    const formData = new FormData();
    formData.append("file", importFile);

    axios.post("http://localhost:8000/rss/import", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data"
      }
    })
    .then(res => {
      
      const { message, imported, skipped } = res.data;

      // Actualisation de la page après l'importation
      window.location.reload();
    })
    .catch(err => {
      console.error(err);
      setMessage("Erreur lors de l'importation.");
      setMessageType("error");
      setTimeout(() => {
        setMessage(null);
        setMessageType('');
      }, 2000);
    });
  };


  return (
    <>
      <NavBar />
      <main className='home-page'>
        <h1>Mes flux RSS</h1>

        <div className="export-import-container">
          {/* Exporter les flux RSS */}
          <div className="export-section">
            <h2 className="section-export-title">Exporter mes flux RSS</h2>

            <div className="export-controls">
              <label htmlFor="export-format" className="export-label">Choisir le format :</label>
              <select
                id="export-format"
                className="export-select"
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
              >
                <option value="json">JSON (.json)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="opml">OPML (.opml)</option>
              </select>

              <button className="export-button" onClick={handleExport}>
                Télécharger l’export
              </button>
            </div>
          </div>

          {/* Importer des flux RSS */}
          <div className="export-section">
            <h2 className="section-export-title">Importer des flux RSS</h2>

            <div className="export-controls">
              <label htmlFor="import-file" className="export-label">Choisir un fichier :</label>
              <input
                type="file"
                id="import-file"
                accept=".json,.csv,.opml"
                className="hidden-file-input"
                onChange={(e) => {
                  setImportFile(e.target.files[0]);
                  setSelectedFileName(e.target.files[0]?.name || "Aucun fichier choisi");
                }}
              />

              <label htmlFor="import-file" className="custom-file-label">
                {selectedFileName || "Aucun fichier choisi"}
              </label>

              <button className="export-button" onClick={handleImport}>
                Importer les flux
              </button>
            </div>
          </div>
        </div>

        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}

        <div className="feed-list">
          {feeds.length === 0 ? (
            <p className="no-results">Aucun flux disponible.</p>
          ) : (
            feeds.map(feed => (
              <div key={feed.feed?.id} className="feed-list-item">
                <h4>{feed.title}</h4>
                <p>Description : {feed.description}</p>
                <p><strong>URL :</strong> {feed.feed?.url || "Non disponible"}</p>
                <p><strong>Tags :</strong> {feed.tags?.join(', ')}</p>
                <p>
                  <strong>Dernière mise à jour :</strong> {
                  feed.last_updated
                    ? new Date(feed.last_updated).toLocaleString('fr-FR', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                    : "Jamais mis à jour"
                }</p>
                <button onClick={() => navigate(`/feeds/${feed.feed.id}/edit`)}>
                  Modifier les informations
                </button>
                
                {feed.feed?.id && (
                  <button onClick={() => handleDelete(feed.feed.id)}>
                    Supprimer le flux
                  </button>
                )}

              </div>
            ))
          )}
        </div>
      </main>
      <Footer />
      <Logout />
    </>
  );
}
