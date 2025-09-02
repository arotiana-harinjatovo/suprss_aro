import { useState } from 'react';

function CommentSection({
  article,
  comments,
  commentInputs,
  handleInputChange,
  handleAddComment,
  currentUser,
  handleDeleteComment,
}) {
  const [expanded, setExpanded] = useState(false);
  const allComments = comments[article.id] || [];
  const visibleComments = expanded ? allComments : allComments.slice(0, 2);
  const canComment = currentUser?.can_comment || currentUser?.is_creator;
  return (
    <div className="comments-section">
      <ul>
        {visibleComments.map((comment) => {

  return (
    <li key={comment.id} className="comment-item">
      <strong>{comment.user.username}</strong>
      <p className="comment-text">{comment.text}</p>

      <div className="comment-meta">
        <small className="comment-date">
          {new Date(comment.createdAt).toLocaleString()}
        </small>

        {currentUser?.user_id === comment.user.id && (
          <button
            onClick={() => handleDeleteComment(article.id, comment.id)}
            className="delete-comment-button"
          >
            Supprimer
          </button>
        )}
      </div>
    </li>
  );
})}
      </ul>

      {/* Bouton "Voir plus" */}
      {allComments.length > 2 && !expanded && (
        <button onClick={() => setExpanded(true)} className="expand-comment-button">
          Voir plus
        </button>
      )}

      {/* Zone de saisie + bouton Commenter */}
      {(currentUser?.can_comment || currentUser?.is_creator) && (
        <div className="comment-input-wrapper">
          <textarea
            placeholder="Écrire un commentaire..."
            value={commentInputs[article.id] || ''}
            onChange={(e) => handleInputChange(article.id, e.target.value)}
            rows={2}
          />
          <button onClick={() => handleAddComment(article.id)}>Commenter</button>
        </div>
      )}
    </div>
  );
}

export default CommentSection;
