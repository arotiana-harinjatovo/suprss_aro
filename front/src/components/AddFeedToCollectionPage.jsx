import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Select from 'react-select';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';
import API_URL from '../services/api';

export default function AddFeedToCollectionPage() {
  const { collectionId } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const [feeds, setFeeds] = useState([]);
  const [selectedFeedId, setSelectedFeedId] = useState(null);

  const [articles, setArticles] = useState([]);
  const [selectedArticleId, setSelectedArticleId] = useState(null);

  const [message, setMessage] = useState({ type: '', text: '' });
  const [manualFeedUrl, setManualFeedUrl] = useState('');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    axios.get(`${API_URL}/rss/feeds/`, { headers })
      .then(res => setFeeds(res.data))
      .catch(console.error);

    axios.get(`${API_URL}/rss/articles/`, { headers })
      .then(res => setArticles(res.data))
      .catch(console.error);
  }, [navigate]);


  useEffect(() => {
    if (message.text) {
      const timer = setTimeout(() => {
        setMessage({ type: '', text: '' });
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const handleAddFeed = async () => {
  if (!selectedFeedId && !manualFeedUrl) {
    return setMessage({ type: 'error', text: "Veuillez sélectionner un flux ou entrer une URL." });
  }

  try {
    let feedIdToAdd = selectedFeedId;

    // Si une URL est entrée manuellement, créer le flux
    if (manualFeedUrl) {
      const res = await axios.post(
        `${API_URL}/rss/feeds/`,
        { 
          title: "Flux personnalisé", // requis
          url: manualFeedUrl,         // requis
          article_limit: 5,           // optionnel
          tags: [],                   // optionnel
          update_frequency: "daily",  // optionnel
          is_active: true,            // optionnel
          is_shared: false            // optionnel
        },
        { headers }
      );
      feedIdToAdd = res.data.feed.id || res.data.id;
    }

    // Ajouter le flux à la collection
    await axios.post(
      `${API_URL}/rss/collections/${collectionId}/feeds/${feedIdToAdd}`,
      {},
      { headers }
    );

    setMessage({ type: 'success', text: "Flux ajouté à la collection !" });
    setTimeout(() => {
      navigate(`/collections/${collectionId}`);
    }, 1500);
  } catch (err) {
    console.error(err);
    setMessage({ type: 'error', text: "Erreur lors de l'ajout du flux." });
  }
};



const handleAddArticle = async () => {
  if (!selectedArticleId) return setMessage({ type: 'error', text: "Veuillez sélectionner un article." });

  try {
    await axios.post(
      `${API_URL}/rss/collections/${collectionId}/articles/${selectedArticleId}`,
      {},
      { headers }
    );
    setMessage({ type: 'success', text: "Article ajouté à la collection !" });
    setTimeout(() => {
      navigate(`/collections/${collectionId}`);
    }, 1500);
  } catch (err) {
    console.error(err);
    setMessage({ type: 'error', text: "Erreur lors de l'ajout de l'article." });
  }
};

  // Format des options pour react-select
  const feedOptions = feeds.map(feed => ({
    value: feed.feed.id,
    label: feed.title
  }));

  const articleOptions = articles.map(item => ({
    value: item.article.id,
    label: item.article.title
  }));


  return (
    <>
      <NavBar />
      <main className="home-page">
        <h1 className="page-title">Ajouter un flux ou un article à la collection</h1>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        {/* Section ajout de flux */}
        <div className="form-section">
          <label htmlFor="feed-select">Sélectionnez un flux :</label>
          <Select
            id="feed-select"
            options={feedOptions}
            onChange={(selected) => setSelectedFeedId(selected.value)}
            placeholder="-- Choisir un flux --"
            styles={{
              menu: (provided) => ({
                ...provided,
                maxHeight: '300px',
                overflowY: 'auto',
              }),
              control: (provided) => ({
                ...provided,
                borderRadius: '10px',
                borderColor: '#e5e7eb',
                boxShadow: 'none',
                fontFamily: 'Quicksand, sans-serif',
              }),
            }}
          />

          <label htmlFor="feed-url" style={{ marginTop: '1rem' }}>Ou entrez une URL de flux RSS :</label>
          <input
            type="text"
            id="feed-url"
            value={manualFeedUrl}
            onChange={(e) => setManualFeedUrl(e.target.value)}
            placeholder="https://exemple.com/rss"
            className="rss-url-input"
          />

          <button className="create-button" onClick={handleAddFeed}>
            Ajouter le flux à la collection
          </button>
        </div>

        {/* Section ajout d'article */}
        <div className="form-section">
          <label htmlFor="article-select">Sélectionnez un article :</label>
          <Select
            id="article-select"
            options={articleOptions}
            onChange={(selected) => setSelectedArticleId(selected.value)}
            placeholder="-- Choisir un article --"
            styles={{
              menu: (provided) => ({
                ...provided,
                maxHeight: '300px',
                overflowY: 'auto',
              }),
              control: (provided) => ({
                ...provided,
                borderRadius: '10px',
                borderColor: '#e5e7eb',
                boxShadow: 'none',
                fontFamily: 'Quicksand, sans-serif',
              }),
            }}
          />

          <button className="create-button" onClick={handleAddArticle}>
            Ajouter l'article à la collection
          </button>
        </div>
      
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem'}}>
          <button
            className="create-button"
            style={{ width: '200px', padding: '0.75rem 2rem', fontSize: '1rem' }}
            onClick={() => navigate(`/collections`)}
          >
            Annuler
          </button>
        </div>

      </main>
      <Logout />
      <Footer />
    </>
  );
}
