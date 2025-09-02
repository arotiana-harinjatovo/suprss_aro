import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';
import ArticleCard from '../components/ArticleCard';


export default function HomePage() {
  const [user, setUser] = useState(null);
  const [collections, setCollections] = useState([]);
  const [feeds, setFeeds] = useState([]);
  const [articles, setArticles] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFeedForm, setShowFeedForm] = useState(false);
  const [newFeed, setNewFeed] = useState({
    title: '',
    url: '',
    description: '',
    tags: [],
    update_frequency: 'daily',
    article_limit: 5,
    is_shared: false
  });

  // Trie par date récente des flux
  const recentFeeds = [...feeds]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 6);

  // Expansion des articles
  const [expandedArticles, setExpandedArticles] = useState({});
  const toggleExpand = (id) => {
    setExpandedArticles(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('');

  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    axios.get('http://localhost:8000/user/me', { headers })
      .then(res => setUser(res.data))
      .catch(() => navigate('/login'));

    axios.get('http://localhost:8000/rss/collections/', { headers })
      .then(res => setCollections(res.data))
      .catch(console.error);

    axios.get('http://localhost:8000/rss/feeds/', { headers })
      .then(res => setFeeds(res.data))
      .catch(console.error);

    axios.get('http://localhost:8000/rss/articles/', { headers })
      .then(res => setArticles(res.data))
      .catch(console.error);
  }, [navigate]);


  const handleCreateFeed = async (e) => {
    e.preventDefault();
    try {
  const res = await axios.post('http://localhost:8000/rss/feeds', newFeed, { headers });
  setFeeds([...feeds, res.data]);
  setNewFeed({
    title: '',
    url: '',
    description: '',
    tags: [],
    update_frequency: 'daily',
    article_limit: 5,
    is_shared: false
  });
  setShowFeedForm(false);
  setMessage("Flux RSS ajouté avec succès !");
  setMessageType("success");
} catch (err) {
  console.error(err);
  setMessage("Erreur lors de l'ajout du flux RSS.");
  setMessageType("error");
} finally {
  setTimeout(() => {
    setMessage(null);
    setMessageType('');
  }, 1500);
}

  
  
  };

  const filteredCollections = collections.filter(col =>
    col.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDeleteArticle = async (articleId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet article ?")) return;

    try {
      await axios.delete(`http://localhost:8000/rss/articles/${articleId}`, { headers });
      // Mise à jour locale : enlever l'article supprimé
      setArticles(prevArticles => prevArticles.filter(article => article.id !== articleId));
      setMessage("Article supprimé avec succès !");
      setMessageType("success");
    } catch (error) {
      console.error(error);
      setMessage("Erreur lors de la suppression de l'article.");
      setMessageType("error");
    }

    // Message temporaire
    setTimeout(() => {
      setMessage(null);
      setMessageType('');
    }, 3000);
  };

  return (
    <>
      <NavBar />
      <main className="home-page">

        <div className="welcome-card">
          <h1>Bienvenue <span>{user?.full_name || 'Utilisateur'} </span> !</h1>
          <p>Nous sommes ravis de vous retrouver. Explorez vos collections de flux RSS ci-dessous.</p>
        </div>

        {/* Collections */}
        <h2 className="section-title">Vos collections de flux RSS</h2>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Rechercher une collection..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button
            className="create-button"
            onClick={() => navigate('/collections/create')}
          >
            + Nouvelle collection
          </button>
        </div>

        <div className="home-collections-grid">
          {filteredCollections.map((col) => (
            <div key={col.id} className="home-collection-card">
              <h3 className="collection-title">{col.name}</h3>
              <p className="collection-description">{col.description}</p>
              <span>Flux: {col.feeds?.length || 0}</span>
              <span>Articles: {col.articles?.length || 0}</span>
              
              <button onClick={() => navigate(`/collections/${col.id}`)}>
                Voir le contenu
              </button>
            </div>
          ))}
          {filteredCollections.length === 0 && (
            <p className="no-results">Aucune collection trouvée.</p>
          )}
        </div>

        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}

        {/* Flux RSS */}
        <h2 className="section-title">Les derniers flux RSS</h2>

        <div  style={{ display: 'flex', gap: '1em', alignItems: 'center' }}>
          <button
            onClick={() => setShowFeedForm(!showFeedForm)}
            className="toggle-feed-form"
          >
            <span>{showFeedForm ? "" : "+"}</span> {showFeedForm ? "Annuler" : "Ajouter un flux RSS"}
          </button>

          <button
            onClick={() => navigate("/bibliotheque")}
            className="toggle-feed-form"
          >
            Voir la liste des flux
          </button>
        </div>


        {showFeedForm && (
          <form onSubmit={handleCreateFeed} className="add-feed-form">
            <input
              type="text"
              placeholder="Titre du flux"
              value={newFeed.title}
              onChange={(e) => setNewFeed({ ...newFeed, title: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="URL du flux"
              value={newFeed.url}
              onChange={(e) => setNewFeed({ ...newFeed, url: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Description"
              value={newFeed.description}
              onChange={(e) => setNewFeed({ ...newFeed, description: e.target.value })}
            />
            <input
              type="text"
              placeholder="Tags (séparés par des virgules)"
              onChange={(e) => setNewFeed({
                ...newFeed,
                tags: e.target.value.split(',').map(tag => tag.trim())
              })}
            />
            <select
              value={newFeed.update_frequency}
              onChange={(e) => setNewFeed({ ...newFeed, update_frequency: e.target.value })}
            >
              <option value="hourly">Toutes les heures</option>
              <option value="6h">Toutes les 6 heures</option>
              <option value="daily">Quotidiennement</option>
              <option value="weekly">Hebdomadaire</option>
            </select>
            <button type="submit">Ajouter le flux</button>
          </form>
        )}

        <div className="feeds-grid">
           {recentFeeds.length === 0 ? (
            <p className="no-results">Aucun flux RSS trouvé.</p>
          ) : (
            recentFeeds.map(feed => (
              <div key={feed.id} className="feed-card">
                <h3>{feed.title}</h3>
                <p>{feed.description}</p>
                
                <p className='last-updated'>
                  <strong>Dernière mise à jour :</strong> {
                      feed.last_updated
                        ? new Date(feed.last_updated).toLocaleString('fr-FR', {                           
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false,
                          })
                        : "Jamais mis à jour"
                    }</p>

              </div>
            ))
          )}
        </div>

        {/* Articles */}
        <h2 className="section-title">📰 Les dernières Nouvelles</h2>
        <div className="articles-card">
          {articles.length === 0 ? (
            <p className="no-results">Aucun article trouvé.</p>
          ) : (
            articles.map(article => (             
            <ArticleCard
              key={article.article.id}
              article={article.article}
              isExpanded={expandedArticles[article.article.id]}
              onToggleExpand={toggleExpand}
              onDelete={handleDeleteArticle}
              token={token}
              isRead={article.is_read}
              isFavorite={article.is_favorite}
            />
            ))
          )}
        </div>

      </main>
      <Logout />
      <Footer />
    </>
  );
}
