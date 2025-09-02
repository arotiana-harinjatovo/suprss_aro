import React, { useState, useEffect } from 'react';
import { Trash2 } from 'lucide-react';
import CommentSection from './CommentSection';

const API_URL = 'http://localhost:8000';

function CollectionArticles({ articles, currentUser, handleDeleteArticle, collectionId }) {
  const token = localStorage.getItem('access_token');

  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };

  const [comments, setComments] = useState({});
  const [commentInputs, setCommentInputs] = useState({});
  const [expandedComments, setExpandedComments] = useState({});
  const [userPermissions, setUserPermissions] = useState(null);

  // Charger les commentaires à l’affichage
  useEffect(() => {
    async function fetchComments() {
      try {
        const result = {};
        for (const article of articles) {
          const res = await fetch(`${API_URL}/comments/article/${article.id}`, {
            headers,
          });
          const data = await res.json();

          result[article.id] = data.map((c) => ({
            ...c,
            createdAt: new Date(c.created_at),
          }));
        }
        setComments(result);
      } catch (err) {
        console.error('Erreur chargement commentaires:', err);
      }
    }

    if (articles.length > 0) {
      fetchComments();
    }
  }, [articles]);

  // Récupérer les permissions utilisateur sur la collection
  useEffect(() => {
    async function fetchPermissions() {
      if (!token || !collectionId) return;

      try {
        const res = await fetch(`${API_URL}/collections/${collectionId}/permissions`, {
          headers,
        });
        if (!res.ok) throw new Error("Erreur récupération permissions");
        const data = await res.json();
        setUserPermissions(data);
      } catch (error) {
        console.error("Erreur chargement permissions :", error);
      }
    }

    fetchPermissions();
  }, [token, collectionId]);

  // Ajouter un commentaire
  const handleAddComment = async (articleId) => {
    const text = commentInputs[articleId]?.trim();
    if (!text || !token) return;

    try {
      const res = await fetch(`${API_URL}/comments/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ text, article_id: articleId }),
      });

      if (!res.ok) throw new Error('Erreur ajout commentaire');

      const newComment = await res.json();
      newComment.createdAt = new Date(newComment.created_at);

      setComments((prev) => ({
        ...prev,
        [articleId]: [newComment, ...(prev[articleId] || [])],
      }));

      setCommentInputs((prev) => ({ ...prev, [articleId]: '' }));
    } catch (err) {
      console.error('Erreur ajout commentaire:', err);
    }
  };

  // Supprimer un commentaire
  const handleDeleteComment = async (articleId, commentId) => {
    if (!token) return;

    try {
      const res = await fetch(`${API_URL}/comments/${commentId}`, {
        method: 'DELETE',
        headers,
      });

      if (!res.ok) throw new Error('Erreur suppression commentaire');

      setComments((prev) => ({
        ...prev,
        [articleId]: prev[articleId].filter((comment) => comment.id !== commentId),
      }));
    } catch (err) {
      console.error('Erreur suppression commentaire:', err);
    }
  };

  const handleInputChange = (articleId, value) => {
    setCommentInputs((prev) => ({ ...prev, [articleId]: value }));
  };

  return (
    <section className="section">
      <h2
        className="section-title"
        style={{ fontFamily: 'Quicksand, sans-serif', color: '#4f46e5' }}
      >
        Articles de la collection
      </h2>

      {articles.length === 0 ? (
        <p className="no-results">Aucun article dans cette collection.</p>
      ) : (
        <ul className="article-list">
          {articles.map((article) => (
            <li key={article.id} className="article-item">
              <div className="article-content">
                <a
                  href={article.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="article-list-title"
                >
                  {article.title}
                </a>

                <p className="article-summary">
                  <span
                    dangerouslySetInnerHTML={{
                      __html: article.summary.split('Au sommaire :')[0].trim(),
                    }}
                  />
                </p>

                <small className="article-date">
                  Publié le :{' '}
                  {article.published_at
                    ? new Date(article.published_at).toLocaleDateString()
                    : 'Date inconnue'}
                </small>

                {/* Zone commentaires */}
                <CommentSection
                  article={article}
                  comments={comments}
                  commentInputs={commentInputs}
                  handleInputChange={handleInputChange}
                  handleAddComment={handleAddComment}
                  currentUser={currentUser}
                  handleDeleteComment={handleDeleteComment}
                />
              </div>

              {currentUser?.is_creator &&  (
                <button
                  className="delete-icon"
                  onClick={() => handleDeleteArticle(article.id)}
                  title="Supprimer l'article"
                >
                  <Trash2 size={20} color="red" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default CollectionArticles;
