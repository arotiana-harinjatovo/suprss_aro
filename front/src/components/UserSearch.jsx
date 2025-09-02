import { useState } from 'react';
import {
  sendFriendRequest,
  followUser,
  removeFriend,
  unfollowUser
} from '../services/FollowersAPI';

const UserSearch = ({ token, currentUserId }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setMessage("Veuillez entrer un nom d'utilisateur ou un email.");
      setMessageType('info');
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/user/search?query=${encodeURIComponent(searchQuery)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error();

      const data = await response.json();
      const filteredResults = data.filter(user => user.id !== currentUserId);
      setSearchResults(filteredResults);
      setMessage(`${filteredResults.length} utilisateur(s) trouvé(s).`);
      setMessageType('success');
      console.log("Résultats de recherche :", filteredResults);
    } catch (error) {
      setMessage("Erreur lors de la recherche.");
      setMessageType('error');
    }
  };

  const handleAction = async (actionFn, userId, successMsg) => {
    try {
      await actionFn(userId);
      setMessage(successMsg);
      setMessageType('success');

      // Mise à jour locale
      setSearchResults(prev =>
        prev.map(user =>
          user.id === userId
            ? {
                ...user,
                is_friend: successMsg.includes("ami") ? true : user.is_friend,
                is_following: successMsg.includes("suivi") ? true : user.is_following
              }
            : user
        )
      );
    } catch (err) {
      const errorMessage =
        err?.response?.data?.detail || "Une erreur est survenue.";
      setMessage(errorMessage);
      setMessageType('error');
    }
  };

  return (
    <div className="profil-container">
      <h3 className="profil-label">Rechercher des utilisateurs</h3>

      <div className="profil-field">
        <input
          type="text"
          placeholder="Nom d'utilisateur ou email"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        <button onClick={handleSearch} style={{ marginTop: '0.5rem' }}>
          Rechercher
        </button>
      </div>

      {message && (
        <p className={`message ${messageType}`} style={{ marginTop: '1rem' }}>
          {message}
        </p>
      )}

      {searchResults.length > 0 && (
        <div className="profil-results">
          {searchResults.map(user => (
            <div key={user.id} className="profil-result-item">
              <p className="texte-limite">
                <strong>{user.username}</strong> ({user.email})
              </p>
              <div className="profil-social-buttons">
                {/* Ajouter en ami */}
                {user.friendship_status === "pending" ? (
                  <button className="btn-muted" disabled>
                    Demande en attente
                  </button>
                ) : (
                  <button
                    className={user.is_friend ? "btn-muted" : "btn-active"}
                    onClick={() =>
                      handleAction(
                        (id) => sendFriendRequest(id, token),
                        user.id,
                        "Demande d'ami envoyée."
                      )
                    }
                    disabled={user.is_friend}
                  >
                    {user.is_friend ? "Déjà ami" : "Ajouter en ami"}
                  </button>
                )}

                {/* Suivre */}
                <button
                  className={user.is_following ? "btn-muted" : "btn-active"}
                  onClick={() =>
                    handleAction(
                      (id) => followUser(id, token),
                      user.id,
                      "Utilisateur suivi."
                    )
                  }
                  disabled={user.is_following} // désactivé si déjà suivi
                >
                  {user.is_following ? "Déjà suivi" : "Suivre"}
                </button>

                {/* Supprimer ami */}
                  {user.is_friend && user.friendship_id && (
                    <button
                      className="btn-warning"
                      onClick={() =>
                        handleAction(
                          (id) => removeFriend(id, token),
                          user.friendship_id,
                          "Ami supprimé."
                        )
                      }
                    >
                      Supprimer ami
                    </button>
                  )}

                  {/* Se désabonner */}
                  {user.is_following && user.follow_id && (
                    <button
                      className="btn-warning"
                      onClick={() =>
                        handleAction(
                          (id) => unfollowUser(id, token),
                          user.follow_id,
                          "Désabonnement effectué."
                        )
                      }
                    >
                      Se désabonner
                    </button>
                  )}

              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UserSearch;
