import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Pencil } from "lucide-react";
import API_URL from '../services/api';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';
import CollectionArticles from '../components/CollectionArticles';
import CollectionFeeds from '../components/CollectionFeeds';
import CollectionChat from '../components/CollectionChat';

export default function CollectionIdPage() {
  const { collectionId } = useParams();
  const navigate = useNavigate();

  const [collectionName, setCollectionName] = useState('');
  const [collectionDescription, setCollectionDescription] = useState('');
  const [permissions, setPermissions] = useState([]);

  const [currentUser, setCurrentUser] = useState(null);
  const [currentUserPermissions, setCurrentUserPermissions] = useState({
    is_creator: false,
    can_add_feed: false,
    can_comment: false,
    can_read: false,
  });

  const [feeds, setFeeds] = useState([]);
  const [articles, setArticles] = useState([]);
  const [friends, setFriends] = useState([]);

  const [deletingFeedId, setDeletingFeedId] = useState(null);
  const [deletingArticleId, setDeletingArticleId] = useState(null);

  const [inviteUserId, setInviteUserId] = useState('');
  const [inviteRole, setInviteRole] = useState('editor');

  const [userRole, setUserRole] = useState(null);

  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');

  const [updatingUserId, setUpdatingUserId] = useState(null);
  const [deletingUserId, setDeletingUserId] = useState(null);

  const [showEditModal, setShowEditModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');

  const collection_message = {
    id: collectionId,
    name: collectionName,
    description: collectionDescription,
  };


  const token = localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  // Affiche un message temporaire
  const showMessage = (text, type = 'info') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('info');
    }, 3000);
  };

  const truncate = (str, maxLength) =>
    str.length > maxLength ? str.slice(0, maxLength) + '…' : str;

  const fetchPermissions = () => {
    axios
      .get(`${API_URL}/rss/collections/${collectionId}/permissions`, { headers })
      .then(res => setPermissions(res.data))
      .catch(console.error);
  };

  const fetchCollectionData = () => {
    axios.get(`${API_URL}/rss/collections/${collectionId}`, { headers })
      .then(res => {
        setCollectionName(res.data.name);
        setCollectionDescription(res.data.description || '');
        setNewName(res.data.name);
        setNewDescription(res.data.description || '');
        setCurrentUserPermissions(res.data.current_user_permissions || {});
        setFeeds(res.data.feeds || []);
        setArticles(res.data.articles || []);
        setUserRole(res.data.current_user_permissions?.role || null);
      })
      .catch(console.error);
  };

  useEffect(() => {
    fetchCollectionData();
    fetchPermissions();

    axios.get(`${API_URL}/followers/accepted`, { headers })
      .then(res => setFriends(res.data))
      .catch(console.error);
  }, [collectionId]);

  
  useEffect(() => {
    axios.get(`${API_URL}/user/me`, { headers })
      .then(res => {
        setCurrentUser(res.data);
        console.log("✅ Utilisateur connecté :", res.data);
      })
      .catch(err => console.error("❌ Erreur lors de la récupération de l'utilisateur :", err));
  }, []);


  const handleInvite = () => {
    if (!inviteUserId) return;
    axios.post(
      `${API_URL}/rss/collections/${collectionId}/invite/${inviteUserId}`,
      { role: inviteRole },
      { headers }
    )
      .then(res => {
        showMessage(res.data.message, res.data.status);
        setInviteUserId('');
        fetchPermissions();
      })
      .catch(err => {
        console.error(err);
        showMessage("Erreur lors de l'invitation.", "error");
      });
  };

  const handleDeleteCollection = async () => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cette collection ?")) return;
    try {
      await axios.delete(`${API_URL}/rss/collections/${collectionId}`, { headers });
      navigate('/collections');
    } catch (error) {
      console.error("Erreur lors de la suppression :", error);
      showMessage("Erreur lors de la suppression de la collection", "error");
    }
  };

  const handleRemoveMember = async (userId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce membre ?")) return;
    setDeletingUserId(userId);
    try {
      await axios.delete(`${API_URL}/rss/collections/${collectionId}/members/${userId}`, { headers });
      showMessage("Membre supprimé avec succès", "success");
      fetchPermissions();
    } catch (error) {
      console.error(error);
      showMessage("Erreur lors de la suppression du membre", "error");
    } finally {
      setDeletingUserId(null);
    }
  };

  const handlePermissionChange = async (userId, field, value) => {
    setUpdatingUserId(userId);
    const updatedUser = permissions.find(p => p.user_id === userId);
    if (!updatedUser) return;

    const updatedPermissions = {
      can_add_feed: field === 'can_add_feed' ? value : updatedUser.can_add_feed,
      can_read: field === 'can_read' ? value : updatedUser.can_read,
      can_comment: field === 'can_comment' ? value : updatedUser.can_comment,
    };

    try {
      await axios.put(
        `${API_URL}/rss/collections/${collectionId}/permissions/${userId}`,
        updatedPermissions,
        { headers }
      );
      showMessage("Permissions mises à jour", "success");
      fetchPermissions();
    } catch (err) {
      console.error(err);
      showMessage("Erreur lors de la mise à jour des permissions", "error");
    } finally {
      setUpdatingUserId(null);
    }
  };

  const handleUpdateCollection = async () => {
    const updatedName = newName.trim() || collectionName;
    const updatedDescription = newDescription.trim() || collectionDescription;

    try {
      await axios.put(
        `${API_URL}/rss/collections/${collectionId}/edit`,
        { name: updatedName, description: updatedDescription },
        { headers }
      );
      setCollectionName(updatedName);
      setCollectionDescription(updatedDescription);
      showMessage("Collection mise à jour", "success");
      setShowEditModal(false);
    } catch (error) {
      console.error(error);
      showMessage("Erreur lors de la mise à jour", "error");
    }
  };

  const handleDeleteArticle = async (articleId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet article ?")) return;

    setDeletingArticleId(articleId);
    try {
      await axios.delete(`${API_URL}/rss/collections/${collectionId}/articles/${articleId}`, { headers });
      // Recharge les articles
      const response = await axios.get(`${API_URL}/rss/collections/${collectionId}`, { headers });
      setArticles(response.data.articles || []);
      showMessage("Article supprimé avec succès", "success");
    } catch (error) {
      console.error("Erreur lors de la suppression :", error);
      showMessage("Erreur lors de la suppression de l'article", "error");
    } finally {
      setDeletingArticleId(null);
    }
  };

  const handleDeleteFeed = async (feedId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce flux RSS ?")) return;

    setDeletingFeedId(feedId);
    try {
      await axios.delete(`${API_URL}/rss/collections/${collectionId}/feeds/${feedId}`, { headers });
      // Recharge les feeds
      const response = await axios.get(`${API_URL}/rss/collections/${collectionId}`, { headers });
      setFeeds(response.data.feeds || []);
      showMessage("Flux RSS supprimé avec succès", "success");
    } catch (error) {
      console.error("Erreur lors de la suppression :", error);
      showMessage("Erreur lors de la suppression du flux RSS", "error");
    } finally {
      setDeletingFeedId(null);
    }
  };

  const handleLeaveCollection = async () => {
    try {
      const response = await fetch(`${API_URL}/rss/collections/${collectionId}/leave`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        showMessage("Vous avez quitté la collection", "success");
        setTimeout(() => {
          navigate("/collections");
        }, 2000);
      } else {
        const error = await response.json();
        showMessage(`Erreur : ${error.detail}`, "error");
      }
    } catch (err) {
      console.error("Erreur lors de la sortie de la collection :", err);
      showMessage("Erreur lors de la sortie de la collection", "error");
    }
  };


  return (
    <>
      <NavBar />
      <main className="home-page">
        <div>
          <h1 className="collection-title">{collectionName}</h1>
          {currentUserPermissions?.is_creator && (
            <>
              <p className="collection-badge collection-badge-creator">
                Vous êtes le créateur de cette collection
              </p>
              <button
                onClick={() => setShowEditModal(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                  color: '#555',
                  marginLeft: '20px',
                  marginTop: 'auto'
                }}
                title="Modifier la collection"
              >
                <Pencil />
              </button>
            </>
          )}
        </div>

        {showEditModal && (
          <div className="edit-modal">
            <h3>Modifier la collection</h3>
            <div className="edit-form-row">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Nom de la collection"
              />
              <textarea
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Description"
              />
              <div className="edit-buttons">
                <button className="btn-save" onClick={handleUpdateCollection}>Enregistrer</button>
                <button className="btn-cancel" onClick={() => setShowEditModal(false)}>Annuler</button>
              </div>
            </div>
          </div>
        )}

        <div className="container">

          {/* Permissions des membres */}
          <section className="section">
            <h2 className="section-title">Permissions des membres</h2>
            <div className="table-container">
              <table className="permissions-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Ajout de flux</th>
                    <th>Lecture</th>
                    <th>Commentaire</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {permissions.map((perm) => (
                    <tr key={perm.user_id}>
                      <td>{perm.user_name || perm.user_id}</td>
                      <td>
                        <input
                          type="checkbox"
                          checked={perm.can_add_feed}
                          disabled={!currentUserPermissions.is_creator || perm.is_creator || updatingUserId === perm.user_id}
                          onChange={e => handlePermissionChange(perm.user_id, 'can_add_feed', e.target.checked)}
                        />
                      </td>
                      <td>
                        <input
                          type="checkbox"
                          checked={perm.can_read}
                          disabled={!currentUserPermissions.is_creator || perm.is_creator || updatingUserId === perm.user_id}
                          onChange={e => handlePermissionChange(perm.user_id, 'can_read', e.target.checked)}
                        />
                      </td>
                      <td>
                        <input
                          type="checkbox"
                          checked={perm.can_comment}
                          disabled={!currentUserPermissions.is_creator || perm.is_creator || updatingUserId === perm.user_id}
                          onChange={e => handlePermissionChange(perm.user_id, 'can_comment', e.target.checked)}
                        />
                      </td>
                      <td>
                        <button
                          disabled={!currentUserPermissions.is_creator || perm.is_creator || deletingUserId === perm.user_id}
                          onClick={() => handleRemoveMember(perm.user_id)}
                          title={perm.is_creator ? "Le créateur ne peut pas être supprimé" : "Retirer le membre"}
                          className="table-button-delete"
                        >
                          {deletingUserId === perm.user_id ? "Suppression..." : "Retirer"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Message d'info / erreur */}
          {message && (
            <div className={`message ${messageType}`}>
              {message}
            </div>
          )}

          {/* Invitation d’un ami */}
          {currentUserPermissions?.is_creator && (
            <section className="section">
              <h2 className="section-title">Inviter un ami dans la collection</h2>
              <form onSubmit={(e) => { e.preventDefault(); handleInvite(); }} className="invite-form">
                <div className="invite-row">
                  <select
                    className="select-user"
                    value={inviteUserId}
                    onChange={(e) => setInviteUserId(e.target.value)}
                    required
                  >
                    <option value="" disabled>-- Sélectionner un ami --</option>
                    {friends.map(friend => (
                      <option key={friend.id} value={friend.id}>
                        {friend.username
                          ? `${truncate(friend.username, 20)} (${truncate(friend.email, 25)})`
                          : truncate(friend.email, 40)}
                      </option>
                    ))}
                  </select>

                  <select
                    className="select-role"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                  >
                    <option value="editor">Éditeur</option>
                    <option value="viewer">Lecteur</option>
                  </select>
                </div>

                <button type="submit" className="invite-button">Inviter</button>
              </form>
            </section>
          )}

          {/* Flux RSS */}
          <CollectionFeeds
            feeds={feeds}
            isCreator={currentUserPermissions?.is_creator}
            handleDeleteFeed={handleDeleteFeed}
          />

          {/* Articles */}
          <CollectionArticles
            articles={articles}
            currentUser={currentUserPermissions}  
            handleDeleteArticle={handleDeleteArticle}
          />

        </div>

        {/* Boutons bas de page */}
        <div>
          {currentUserPermissions?.is_creator && (
            <button className="button-delete" onClick={handleDeleteCollection}>
              Supprimer la collection
            </button>
          )}
          <div>
            {userRole !== "creator" && (
              <button className="button-delete" onClick={handleLeaveCollection} >
                Quitter la Collection
              </button>
            )}
            <button className="create-button" onClick={() => navigate('/collections')}>
            ↞ Retour à la liste des collections
          </button>
          </div>          
        </div>
      </main>
      
      {currentUser?.id && (
        <CollectionChat
          collectionId={collection_message.id}
          accessToken={token}
          currentUserId={currentUser.id}
        />
      )}

      <Logout />
      <Footer />
    </>
  );
}
