import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import API_URL from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';

function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\-])[A-Za-z\d@$!%*?&\-]{8,}$/;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!passwordRegex.test(newPassword)) {
      setMessage("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.");
      setMessageType("error");
      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage("Les mots de passe ne correspondent pas.");
      setMessageType("error");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/user/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Échec de la réinitialisation du mot de passe.");
      }

      setMessage("Mot de passe réinitialisé avec succès.");
      setMessageType("success");

      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err) {
      setMessage(err.message);
      setMessageType("error");
    }
  };

  // Efface le message après 2 secondes s’il est de type erreur
  useEffect(() => {
    if (message && messageType === "error") {
      const timer = setTimeout(() => {
        setMessage('');
        setMessageType('');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [message, messageType]);

  return (
    <>
      <Header />
      <main className="register-container">
        <h2>Réinitialiser le mot de passe</h2>

        {message && (
          <p className={`message ${messageType}`}>
            {message}
          </p>
        )}

        <form className="register-form" onSubmit={handleSubmit}>
          <label>
            Nouveau mot de passe :
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </label>
          <label>
            Confirmer le mot de passe :
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </label>
          <button type="submit">Réinitialiser</button>
        </form>

        <p className="message">
          <Link to="/login">Retour à la connexion</Link>
        </p>
      </main>
      <Footer />
    </>
  );
}

export default ResetPassword;
