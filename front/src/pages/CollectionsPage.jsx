import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import API_URL from '../services/api';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';

export default function CollectionsPage() {
  const [collections, setCollections] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    axios.get(`${API_URL}/rss/collections/`, { headers })
        .then(res => {
          console.log('Collections API response:', res.data);  // Vérifie la structure ici
          setCollections(res.data);
        })
      .catch(console.error);
  }, [navigate]);

  const filteredCollections = collections.filter(col =>
    col.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <NavBar />
      <main className="home-page">
        <h1 className="page-title">Mes collections de flux RSS</h1>
        
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

        <div className="collections-grid">
          {filteredCollections.map((col) => (
            <div key={col.id} className="collection-card">
              <h3 className='collection-title'>{col.name}</h3>
              <p>{col.description}</p>
              <button onClick={() => navigate(`/collections/${col.id}`)}>
                Voir le contenu
              </button>

               {(col.current_user_permissions?.role === "creator" || col.current_user_permissions?.role === "editor" || col.current_user_permissions?.can_add_feed) && (
                  <button onClick={() => navigate(`/collections/${col.id}/add-feed`)}>
                    + Ajouter un flux / article
                  </button>
                )}
            </div>
          ))}

          {filteredCollections.length === 0 && (
            <p className='no-results'>Aucune collection trouvée.</p>
          )}
        </div>
      </main>
      <Logout />
      <Footer />
    </>
  );
}
