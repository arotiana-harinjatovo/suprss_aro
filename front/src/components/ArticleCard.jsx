import { ChevronUp, ChevronDown } from "lucide-react";
import { useState } from "react";
import axios from "axios";
import API_URL from '../services/api';

export default function ArticleCard({ article, isExpanded, onToggleExpand, onDelete, token, isRead: initialIsRead, isFavorite: initialIsFavorite}) {
  const [isRead, setIsRead] = useState(initialIsRead);
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite);

  const markAsRead = async () => {
    try {
      await axios.put(`${API_URL}/users/articles/${article.id}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsRead(true);
    } catch (error) {
      console.error("Erreur lors du marquage comme lu :", error);
    }
  };

  const toggleFavorite = async () => {
    try {
      await axios.put(`${API_URL}/users/articles/${article.id}/favorite`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsFavorite(prev => !prev);
    } catch (error) {
      console.error("Erreur lors du marquage comme favori :", error);
    }
  };

  return (
    <div className={`article-card ${isExpanded ? 'expanded' : ''}`}>
      <h3 className="article-title">{article.title}</h3>

      <p className="article-description">
        <strong>Résumé :</strong>{" "}
        <span
          dangerouslySetInnerHTML={{
            __html: article.summary.split("Au sommaire :")[0].trim(),
          }}
        />
      </p>

      <div className="article-actions">

        <div className="article-footer-actions">
            <button onClick={markAsRead} disabled={isRead} className="status-button">
                {isRead ? "✓ Lu" : "• Marquer comme lu"}
            </button>

            <button onClick={toggleFavorite} className="status-button">
                {isFavorite ? "★ Retirer des favoris" : "☆ Ajouter aux favoris"}
            </button>
        </div>

        <a
          href={article.link}
          target="_blank"
          rel="noopener noreferrer"
          className="read-article-button"
          onClick={markAsRead}
        >
          Lire l'article
        </a>

        <button
          onClick={() => onDelete(article.id)}
          className="delete-article-button"
        >
          Supprimer
        </button>
      </div>

      <button className="expand-btn" onClick={() => onToggleExpand(article.id)}>
        {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>
    </div>
  );
}
