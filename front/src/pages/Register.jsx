import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import '../styles/index.css'; // Assure-toi que ce fichier contient les styles .message

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    full_name: '',
    email: '',
    password: '',
    confirm_password: '', 
  });

  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' ou 'error'

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\-])[A-Za-z\d@$!%*?&\-]{8,}$/;
                              // à implémenter au moment de la production

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!passwordRegex.test(formData.password)) {
      setMessage("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.");
      setMessageType("error");
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setMessage("Les mots de passe ne correspondent pas.");
      setMessageType("error");
      return;
    }

    const urlEncodedData = new URLSearchParams();
    urlEncodedData.append("username", formData.username);
    urlEncodedData.append("full_name", formData.full_name);
    urlEncodedData.append("email", formData.email);
    urlEncodedData.append("password", formData.password);

    try {
      const response = await fetch("http://localhost:8000/user/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: urlEncodedData.toString(),
      });

      if (response.ok) {
        setMessage("Inscription réussie !");
        setMessageType("success");
        setTimeout(() => navigate('/login'), 2500); // Redirection après 2.5s
      } else {
        const errorData = await response.json();
        console.log("Erreur reçue :", errorData);
        setMessage(`${errorData.detail || "Inscription échouée."}`);
        setMessageType("error");
      }
    } catch (error) {
      setMessage("Erreur de connexion au serveur.");
      setMessageType("error");
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
        <h2>Inscription</h2>

        {message && <p className={`message ${messageType}`}>{message}</p>}

        <form onSubmit={handleSubmit} className="register-form">
          <label>
            Nom d'utilisateur :
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Nom complet :
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Email :
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Mot de passe :
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Confirmer le mot de passe :
            <input
              type="password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
            />
          </label>
          <button type="submit">Créer un compte</button>
        </form>

        <p>
          Vous avez déjà un compte ? <Link to="/login">Connectez-vous ici</Link>
        </p>
      </main>

      <Footer />
    </>
  );
}

export default Register;
