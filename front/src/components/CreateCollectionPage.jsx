// src/pages/CreateCollectionPage.jsx
import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import API_URL from '../services/api';
import NavBar from './NavBar';
import Footer from './Footer';
import Logout from './Logout';

export default function CreateCollectionPage() {
  const [newCollection, setNewCollection] = useState({ name: '', description: '' });
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const handleCreateCollection = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/rss/collections/`, newCollection, { headers });
      navigate('/collections');
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la création de la collection.");
    }
  };

  return (
    <>
      <NavBar />
      <main className="home-page">
        <h1 className="page-title">Créer une nouvelle collection</h1>

        <div className="form-section">
          <form onSubmit={handleCreateCollection}>
            <div className="form-group">
              <label htmlFor="collection-name">Nom de la collection</label>
              <input
                id="collection-name"
                type="text"
                placeholder="Nom de la collection"
                value={newCollection.name}
                onChange={(e) =>
                  setNewCollection({ ...newCollection, name: e.target.value })
                }
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="collection-description">Description</label>
              <input
                id="collection-description"
                type="text"
                placeholder="Description"
                value={newCollection.description}
                onChange={(e) =>
                  setNewCollection({ ...newCollection, description: e.target.value })
                }
                className="form-input"
              />
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem' }}>
              <button
                type="submit"
                className="create-button"
              >
                Créer la collection
              </button>

              <button
                type="button"
                className="create-button"
                style={{ width: '175px', padding: '0.75rem 2rem', fontSize: '1rem' }}
                onClick={() => navigate('/collections')}
              >
                Annuler
              </button>
            </div>

          </form>
        </div>
      </main>
      
      <Logout />
      <Footer />
    </>
  );
}
