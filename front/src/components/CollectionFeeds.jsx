import { Trash2 } from 'lucide-react';

function CollectionFeed({ feeds = [], isCreator, handleDeleteFeed }) {
  return (
    <section className="section">
      <h2 className="section-title">Flux RSS de la collection</h2>

      {feeds.length === 0 ? (
        <p className="no-results">Aucun flux RSS dans cette collection.</p>
      ) : (
        <ul className="collection-feed-list">
          {feeds.map(({ title, rss_feed, added_at, added_by }) => {
            if (!rss_feed) return null;

            return (
              <li key={rss_feed.id} className="collection-feed-item">
                <div>
                  <strong>{title || "Sans nom"}</strong>
                  <br />
                  <a href={rss_feed.url} target="_blank" rel="noopener noreferrer">
                    {rss_feed.url}
                  </a>
                  <br />
                  <small>
                    Date d'ajout :{" "}
                    {added_at ? new Date(added_at).toLocaleDateString() : "Inconnue"}
                  </small>
                  <br />
                  <small>
                    Ajouté par : {added_by?.username || "Utilisateur inconnu"}
                  </small>
                </div>
                {isCreator && (
                  <button
                    className="delete-icon"
                    title="Supprimer le flux"
                    onClick={() => handleDeleteFeed(rss_feed.id)}
                  >
                    <Trash2 size={20} color="red" />
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

export default CollectionFeed;
