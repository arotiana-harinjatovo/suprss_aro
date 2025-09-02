

import { useNavigate } from 'react-router-dom';

function Logout() {
  const navigate = useNavigate();
  return (
    <button
        className="logout-button"
            onClick={() => {
            localStorage.removeItem('access_token');
            setTimeout(() => {
                navigate('/login');
            }, 1500);
            }}
        >
            Déconnexion
    </button>
    );
    }

export default Logout;