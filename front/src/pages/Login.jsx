
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import API_URL from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';

function Login() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const navigate = useNavigate();
  

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', identifier);
    formData.append('password', password);

    try {
      const response = await fetch(`${API_URL}/user/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Nom d’utilisateur ou mot de passe incorrect');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      setMessage('Connexion réussie !');
      setMessageType('success');

      setTimeout(() => {
        navigate('/home');
      }, 1000);
    } catch (err) {
      setMessage(err.message);
      setMessageType('error');
    }
  };
  

const handleGoogleLogin = async () => {
  window.location.href = `${API_URL}/auth/google`;
};

const handleGithubLogin = async () => {
  window.location.href = `${API_URL}/auth/github`;
};

const handleMicrosoftLogin = async () => {
  window.location.href = `${API_URL}/auth/microsoft`;
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
        <h2>Connexion</h2>

        {message && <p className={`message ${messageType}`}>{message}</p>}

        <form className="register-form" onSubmit={handleSubmit}>
          <label>
            Nom d'utilisateur ou Email :
            <input
              type="text"
              name="identifier"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
            />
          </label>
          <label>
            Mot de passe :
            <input
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          <button type="submit">Se connecter</button>
        </form>
        
        <div className="oauth-login-section">
          <button
            type="button"
            className="oauth-login-button"
            onClick={handleGoogleLogin}
          >
            <img
              src="images/google-logo.png"
              alt="Google logo"
              style={{ width: "20px", marginRight: "8px" }}
            />
            <span>Connexion Google</span>
          </button>

          <button
            type="button"
            className="oauth-login-button"
            onClick={handleGithubLogin}
          >
            <img
              src="images/github-logo.png"
              alt="GitHub logo"
              style={{ width: "20px", marginRight: "8px" }}
            />
            <span>Connexion GitHub</span>
          </button>

          <button
            type="button"
            className="oauth-login-button"
            onClick={handleMicrosoftLogin}
          >
            <img
              src="images/microsoft-logo.webp"
              alt="Microsoft logo"
              style={{ width: "20px", marginRight: "8px" }}
            />
            <span>Connexion Microsoft</span>
          </button>
        </div>

        <p className="message">
          Pas encore de compte ? <Link to="/register">Inscrivez-vous ici</Link>
        </p>
        <p>
          <Link to="/forgot-password">Mot de passe oublié ?</Link>
        </p>
      </main>

      <Footer />
    </>
  );
}

export default Login;
