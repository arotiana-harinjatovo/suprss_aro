import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '/images/Logo_SUPRSS.jpg';
import '../styles/nav_bar.css';

export default function NavBar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    fetch('http://localhost:8000/user/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => {
        if (!res.ok) throw new Error('Erreur utilisateur');
        return res.json();
      })
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        navigate('/login');
      });

    fetch('http://localhost:8000/followers/notifications', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => {
        if (!res.ok) throw new Error('Erreur notifications');
        return res.json();
      })
      .then(data => {
        setNotifications(data);
        const unread = data.filter(n => !n.is_read).length;
        setUnreadCount(unread);
      })
      .catch(err => {
        console.error('Erreur lors du chargement des notifications :', err);
      });
  }, [token, navigate]);

  useEffect(() => {
    const fetchResults = async () => {
      if (query.trim().length > 0) {
        try {
          const response = await fetch(`http://localhost:8000/rss/search?q=${encodeURIComponent(query)}`);
          const data = await response.json();
          const { articles, collections } = data;

          const combined = [
            ...articles.map(a => ({ ...a, type: 'article' })),
            ...collections.map(c => ({ ...c, type: 'collection' }))
          ];

          setResults(combined);
          setShowDropdown(true);
        } catch (error) {
          console.error('Erreur lors de la recherche :', error);
        }
      } else {
        setShowDropdown(false);
      }
    };

    fetchResults();
  }, [query]);

  const handleSelect = (item) => {
    setQuery('');
    setShowDropdown(false);
    if (item.type === 'article') {
      window.open(item.link, '_blank');
    } else {
      navigate(`/collections/${item.id}`);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch('http://localhost:8000/followers/notifications/mark_all_read', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Erreur lors du marquage des notifications');

      const updated = notifications.map(n => ({ ...n, is_read: true }));
      setNotifications(updated);
      setUnreadCount(0);
    } catch (error) {
      console.error('Erreur lors du marquage des notifications comme lues :', error);
    }
  };

  const toggleNotifications = () => {
    const newState = !showNotifications;
    setShowNotifications(newState);
    if (newState) {
      markAllAsRead();
    }
  };

  if (loading) return null;

  return (
    <>
      <nav className="navbar">
        <div className="navbar-left">
          <img
            src={logo}
            alt="SUPRSS Logo"
            className="logo-image"
            onClick={() => navigate('/home')}
          />
          <span className="suprss-title">SUPRSS</span>
        </div>

        <div className="navbar-center">
          <div className="search-container">
            <input
              type="text"
              className="search-bar"
              placeholder="Rechercher un article, une collection..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            />
            <i className="fas fa-search search-icon"></i>
          </div>
        </div>

        <div className="navbar-right">
          <i className="fas fa-user-circle" title="Profil" onClick={() => navigate('/profil')} />
          <i className="fas fa-home" title="Accueil" onClick={() => navigate('/home')} />
          <i className="fas fa-layer-group" title="Collections" onClick={() => navigate('/collections')} />
          <i className="fas fa-star" title="Favoris" onClick={() => navigate('/favoris')} />

          <div className="notification-icon" onClick={toggleNotifications}>
            <i className="fas fa-bell" title="Notifications" />
            {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
          </div>

          {showNotifications && (
            <div className="notification-dropdown">
              <h4 style={{ textAlign: 'center', fontWeight: 'bold', marginBottom: '0.5rem', color: '#9671a3', borderBottom: '1px solid #eee', paddingBottom: '5px' }}>
                Notifications
              </h4>
              {notifications.length === 0 ? (
                <p className="no-notif">Aucune notification.</p>
              ) : (
                <>
                  {notifications.map((notif, index) => (
                    <div key={index} className={`notification-item ${notif.is_read ? 'read' : 'unread'}`}>
                      <p>{notif.message || notif.content || "Notification sans message"}</p>
                      <small>{new Date(notif.timestamp).toLocaleString()}</small>
                    </div>
                  ))}
                  <div className="see-all" onClick={() => navigate('/followers/notifications')}>
                    Voir tout
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </nav>

      {/* Dropdown en dehors de la navbar */}
      {showDropdown && results.length > 0 && (
        <div className="dropdown-wrapper">
          <ul className="search-dropdown">
            {results.map((item) => (
              <li key={`${item.type}-${item.id}`} onClick={() => handleSelect(item)}>
                <div className="dropdown-item">
                  <strong>{item.title}</strong>
                  {item.type === 'article' && (
                    <div className="dropdown-meta">
                      <span className="feed-name">{item.feed_name}</span>
                      <span className="tags">
                        {item.tags?.map((tag, i) => (
                          <span key={i} className="tag">{tag}</span>
                        ))}
                      </span>
                    </div>
                  )}
                  <span className="type-tag">({item.type})</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
