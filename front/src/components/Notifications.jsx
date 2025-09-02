import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API_URL from '../services/api';
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import Logout from "../components/Logout";
import { acceptFriendRequest } from '../services/FollowersAPI';

const Notification = () => {
  const [notifications, setNotifications] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    fetch(`${API_URL}/followers/notifications`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => setNotifications(data))
      .catch((err) => {
        console.error("Erreur lors du chargement des notifications :", err);
        setMessage("Impossible de charger les notifications.");
        setMessageType("error");
      });
  }, [token, navigate]);

  const markAsRead = async (id) => {
    try {
      await fetch(`${API_URL}/followers/notifications/${id}/read`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error("Erreur lors du marquage comme lu :", err);
    }
  };

  const deleteNotification = async (id) => {
    try {
      await fetch(`${API_URL}/followers/notifications/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      console.error("Erreur lors de la suppression :", err);
    }
  };

  
  const acceptRequest = async (friendshipId, notificationId) => {
    try {
      await acceptFriendRequest(friendshipId, token);

      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, status: "accepted" } : n
        )
      );

      setMessage("Demande acceptée !");
      setMessageType("success");
    } catch {
      setMessage("Échec de l'acceptation.");
      setMessageType("error");
    } finally {
      setTimeout(() => {
        setMessage('');
        setMessageType('');
      }, 2000);
    }
  };

  return (
    <>
      <NavBar />
      <h2 className="notification-title">MES NOTIFICATIONS</h2>
      {message && <div className={`message ${messageType}`}>{message}</div>}

      <div className="notification-page">
        {notifications.length === 0 ? (
          <p className="no-results">Aucune notification.</p>
        ) : (
          <ul className="notification-list">
            {notifications.map((n) => (
              <li
                key={n.id}
                className={`notification-item ${n.is_read ? "read" : "unread"}`}
              >
                <div className="notification-content">
                  <span>{n.message}</span>
                  <div>
                    <small>{new Date(n.timestamp).toLocaleString()}</small>
                  </div>
                  <div className="notification-status">
                    Statut : {n.is_read ? "Lue" : "Non lue"} | Type : {n.type}
                  </div>
                </div>

                <div className="notification-actions">
                  {!n.is_read && (
                    <button
                      className="notif-btn read-btn"
                      onClick={() => markAsRead(n.id)}
                    >
                      Marquer comme lue
                    </button>
                  )}

                  {n.type === "friend_request" && (
                    n.friendship_status === "accepted" ? (
                      <button className="notif-btn" disabled>
                        Amis
                      </button>
                    ) :  n.friendship_id ? (
                      <button
                        className="notif-btn accept-btn"
                        onClick={() => acceptRequest(n.friendship_id, n.id)}
                      >
                        Accepter la demande
                      </button>
                    ) : (
                      <button className="notif-btn" disabled>
                        ID manquant
                      </button>
                    ) 
                  )}

                  <button
                    className="notif-btn delete-btn"
                    onClick={() => deleteNotification(n.id)}
                  >
                    Supprimer
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <Logout />
      <Footer />
    </>
  );
};

export default Notification;
