import { useEffect, useState } from 'react';
import axios from 'axios';
import API_URL from '../services/api';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';
import ArticleCard from '../components/ArticleCard';

export default function ArticleListPage() {
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const [articles, setArticles] = useState([]);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('');
  const [expandedArticles, setExpandedArticles] = useState({});
  const [filter, setFilter] = useState('all'); // 'all', 'read', 'favorite'

  useEffect(() => {
    if (!token) {
      alert("Utilisateur non authentifié.");
      return;
    }

    axios.get( `${API_URL}/rss/articles`, { headers })
      .then(res => setArticles(res.data))
      .catch(err => {
        console.error(err);
        setMessage("Erreur lors du chargement des articles.");
        setMessageType("error");
      });
  }, [token]);

  const toggleExpand = (id) => {
    setExpandedArticles(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleDeleteArticle = (articleId) => {
    if (confirm("Voulez-vous vraiment supprimer cet article ?")) {
      axios.delete(`${API_URL}/users/articles/${articleId}`, { headers })
        .then(() => {
          setArticles(prev => prev.filter(a => a.article.id !== articleId));
          setMessage("Article supprimé.");
          setMessageType("success");
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

  const filteredArticles = articles.filter(assoc => {
    if (filter === 'read') return assoc.is_read;
    if (filter === 'favorite') return assoc.is_favorite;
    return assoc.is_read || assoc.is_favorite;
  });

  return (
    <>
      <NavBar />
      <main className="home-page">
        <h1>Mes articles lus ou favoris</h1>

        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}

        <div className="filter-buttons">
            <button
                className={`filter-button ${filter === 'all' ? 'active' : ''}`}
                onClick={() => setFilter('all')}
            >
                Tous
            </button>
            <button
                className={`filter-button ${filter === 'read' ? 'active' : ''}`}
                onClick={() => setFilter('read')}
            >
                Lus
            </button>
            <button
                className={`filter-button ${filter === 'favorite' ? 'active' : ''}`}
                onClick={() => setFilter('favorite')}
            >
                Favoris
            </button>
        </div>


        <div className="articles-card">
          {filteredArticles.length === 0 ? (
            <p className="no-results">Aucun article correspondant.</p>
          ) : (
            filteredArticles.map(association => (
              <ArticleCard
                key={association.article.id}
                article={association.article}
                isRead={association.is_read}
                isFavorite={association.is_favorite}
                isExpanded={expandedArticles[association.article.id]}
                onToggleExpand={toggleExpand}
                onDelete={handleDeleteArticle}
                token={token}
              />
            ))
          )}
        </div>
      </main>
      <Footer />
      <Logout />
    </>
  );
}
