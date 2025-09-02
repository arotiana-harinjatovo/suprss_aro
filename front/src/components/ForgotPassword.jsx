import { useState } from 'react';
import API_URL from '../services/api';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${API_URL}/user/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l’envoi du lien de réinitialisation.');
      }

      setMessage('Un lien de réinitialisation a été envoyé à votre adresse email.');
      setMessageType('success');
    } catch (err) {
      setMessage(err.message);
      setMessageType('error');
    }
  };

  return (
    <>
      <Header />
      <nav className="nav-bar">
        <ul className="nav-list">
          <li>
            <Link to="/" className="nav-link">Accueil</Link>
          </li>
        </ul>
      </nav>
      
      <main className="register-container">
        <h2>Mot de passe oublié</h2>

        {message && <p className={`message ${messageType}`}>{message}</p>}

        <form className="register-form" onSubmit={handleSubmit}>
          <label>
            Adresse email :
            <input
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <button type="submit">Envoyer le lien</button>
        </form>

        <p className="message">
          <Link to="/login">Retour à la connexion</Link>
        </p>
      </main>
      <Footer />
    </>
  );
}

export default ForgotPassword;
