import { useState, useEffect, useRef } from "react";
import axios from "axios";

const CollectionChat = ({ collectionId, accessToken, currentUserId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(false); // 👈 nouveau
  const socketRef = useRef(null);

  useEffect(() => {
    if (!collectionId || !accessToken) return;

    let isMounted = true;

    axios
      .get(`http://localhost:8000/ws/collections/${collectionId}/messages`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        if (isMounted) {
          setMessages(res.data);
          console.log("📥 Messages chargés :", res.data);
        }
      })
      .catch((err) => {
        console.error("❌ Erreur lors du chargement des messages :", err);
      });

    return () => {
      isMounted = false;
    };
  }, [collectionId, accessToken]);

  useEffect(() => {
    if (!collectionId || !accessToken) return;

    const ws = new WebSocket(
      `ws://localhost:8000/ws/collections/${collectionId}/chat?token=${accessToken}`
    );
    socketRef.current = ws;

    ws.onopen = () => {
      console.log(`✅ WebSocket connecté à la collection ${collectionId}`);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.info) {
        console.log("ℹ️ Message d’accueil :", message.info);
      } else if (!message.error) {
        setMessages((prev) => [...prev, message]);

 
        if (!isOpen && message.user_id !== currentUserId) {
          setHasNewMessage(true);
        }

        console.log("📩 Message reçu :", message.content);
      } else {
        console.warn("⚠️ Erreur dans le message :", message.error);
      }
    };

    ws.onerror = (error) => {
      console.error("❌ Erreur WebSocket :", error);
    };

    ws.onclose = (event) => {
      console.warn("⚠️ WebSocket fermé :", event);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
        console.log("🔌 WebSocket fermé proprement.");
      }
      socketRef.current = null;
    };
  }, [collectionId, accessToken, isOpen]);

  const sendMessage = () => {
    const socket = socketRef.current;
    if (input.trim() !== "" && socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ content: input }));
      setInput("");
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setHasNewMessage(false); 
  };

  return (
    <div className="collection-chat-container">
      <div className="collection-chat-bubble" onClick={toggleChat}>
        💬
        {hasNewMessage && <span className="collection-chat-notification-badge">●</span>} 
      </div>

      {isOpen && (
        <div className="collection-chat-box">
          <div className="collection-chat-header">Discussion</div>
          <div className="collection-chat-messages">
            {messages.map((msg, index) => {
              const isCurrentUser = msg.user_id === currentUserId;
              return (
                <div
                  key={`${msg.user_id}-${msg.timestamp || index}`}
                  className={`collection-chat-message ${
                    isCurrentUser ? "current-user" : "other-user"
                  }`}
                >
                  <strong>{msg.user_name || msg.user_id} </strong> {msg.content}
                  <span className="collection-chat-timestamp">
                    {msg.timestamp &&
                      new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="collection-chat-input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              className="collection-chat-input"
              placeholder="Écrire un message..."
            />
            <button onClick={sendMessage} className="collection-chat-send-button">
              Envoyer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollectionChat;
