import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      localStorage.setItem("access_token", token);

      setTimeout(() => {
        navigate("/home");
      }, 100);
    } else {
      navigate("/login");
    }
  }, [navigate]);

  return <p>Connexion en cours...</p>; // ← Ce return est essentiel
}

export default LoginCallback;
