import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';

export default function FeedEditPage() {
  const { feedId } = useParams();
  const navigate = useNavigate();
  const [feed, setFeed] = useState(null);
  const [formData, setFormData] = useState({ title: '', url: '', description: '', tags: [] });
  const [message, setMessage] = useState(null); // message à afficher
  const [messageType, setMessageType] = useState(''); // success ou error
  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    axios.get(`http://localhost:8000/rss/feeds/${feedId}`, { headers })
      .then(res => {
        setFeed(res.data);
        setFormData({
          title: res.data.title,
          description: res.data.description,
          url: res.data.url,
          tags: res.data.tags || []
        });
      })
      .catch(err => {
        console.error(err);
        setMessage("Erreur lors du chargement du flux.");
        setMessageType("error");
      });
  }, [feedId]);

  const handleUpdate = (e) => {
    e.preventDefault();

    axios.put(`http://localhost:8000/rss/feeds/${feedId}`, formData, { headers })
      .then(() => {
        setMessage("Flux mis à jour !");
        setMessageType("success");
        setTimeout(() => {
          navigate("/bibliotheque");
        }, 1000); // délai pour laisser le message visible
      })
      .catch(err => {
        console.error(err);
        setMessage("Erreur lors de la mise à jour.");
        setMessageType("error");
      });
  };

  if (!feed) return <p>Chargement...</p>;

  return (
    <>
      <NavBar />
      <main className='home-page'>
        <div>
          <h1>Modifier le flux RSS</h1>

          {message && (
            <div className={`message ${messageType}`}>
              {message}
            </div>
          )}

          <form className='add-feed-form' onSubmit={handleUpdate}>
            <label>Titre</label>
            <input
              type="text"
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
            />
            <label>URL</label>
            <input
              type="text"
              value={formData.url}
              onChange={e => setFormData({ ...formData, url: e.target.value })}
            />
            <label>Description</label>
            <input
              type="text"
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
            />
            <label>Tags (séparés par des virgules)</label>
            <input
              type="text"
              value={formData.tags.join(', ')}
              onChange={e => setFormData({ ...formData, tags: e.target.value.split(',').map(tag => tag.trim()) })}
            />

            <div style={{ marginTop: '1em' }}>
              <button type="submit" className='button-update'>
                Enregistrer les modifications
              </button>
            </div>
          </form>

          <button onClick={() => navigate("/bibliotheque")} className='toggle-feed-form'>
            Retour à la liste des flux
          </button>
        </div>
      </main>
      <Logout />
      <Footer />
    </>
  );
}
