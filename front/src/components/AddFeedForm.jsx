import { useState } from 'react';
import axios from 'axios';
import API_URL from '../services/api';

export default function AddFeedForm({ collectionId }) {
  const [url, setUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    try {
      await axios.post(`${API_URL}/rss/collections/${collectionId}/feeds`, {
        url
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Flux ajouté !');
      setUrl('');
    } catch (err) {
      console.error(err);
      alert('Erreur lors de l’ajout du flux.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="add-feed-form">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="URL du flux RSS"
        required
      />
      <button type="submit">Ajouter</button>
    </form>
  );
}
