
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import API_URL from '../services/api';

const FriendList = () => {
  const [friends, setFriends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');

    axios.get(`${API_URL}/followers/accepted`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(response => {
        const data = Array.isArray(response.data) ? response.data : [];
        setFriends(data);
        setLoading(false);
      })
      .catch(error => {
        setError('Erreur lors du chargement des amis.');
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Chargement...</p>;
  if (error) return <p>{error}</p>;

  return (
    
    <div className="profil-friendlist">
        <div className="profil-friendlist-container">
            <h3>Liste d'amis</h3>
            {friends.length === 0 ? (
              <p className="no-results">Aucun ami pour l’instant.</p>
            ) : (
              <ul className="friend-list">
                {friends.map(friend => (
                  <li key={friend.id} className="friend-item">
                    <div className="friend-name">
                      Nom d'utilisateur : <strong>{friend.username}</strong>
                    </div>
                    <div className="friend-fullname">Nom complet : {friend.full_name}</div>
                    <div className="friend-email">Email : {friend.email}</div>
                  </li>
                ))}
              </ul>
            )}
        </div>
    </div>
  );
};

export default FriendList;
