import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import Logout from '../components/Logout';
import UserSearch from '../components/UserSearch';
import DisplaySettings from '../components/DisplaySettings';
import FriendList from '../components/FriendList';


const Profil = () => {
  const [user, setUser] = useState({ username: '', full_name: '', email: '' });
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [theme, setTheme] = useState("light");
  const [fontSize, setFontSize] = useState("medium");
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    fetch('http://localhost:8000/user/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
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
  }, []);

  const handleChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = e => {
    e.preventDefault();
    fetch('http://localhost:8000/user/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(formData),
    })
      .then(res => {
        if (!res.ok) throw new Error('Erreur lors de la mise à jour');
        return res.json();
      })
      .then(() => {
        setMessage('Profil mis à jour avec succès !');
        setMessageType('success');
        setFormData({});
        setShowForm(false);
        setTimeout(() => {
          setMessage('');
          setMessageType('');
        }, 2500);
      })
      .catch(() => {
        setMessage('Échec de la mise à jour du profil.');
        setMessageType('error');
        setTimeout(() => {
          setMessage('');
          setMessageType('');
        }, 2500);
      });
  };

  const handleDeleteAccount = () => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer votre compte ?")) return;

    fetch('http://localhost:8000/user/me', {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(res => {
        if (!res.ok) throw new Error();
        setMessage('Votre compte a été supprimé.');
        setMessageType('success');
        localStorage.removeItem('access_token');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      })
      .catch(() => {
        setMessage('Échec de la suppression du compte.');
        setMessageType('error');
        setTimeout(() => {
          setMessage('');
          setMessageType('');
        }, 2000);
      });
  };

  if (loading) return <p>Chargement...</p>;

  return (
    <>
      <NavBar />
      <h2 className="section-title">MON PROFIL</h2>
      {message && <div className={`message ${messageType}`}>{message}</div>}

      <div className="profil-main">
        {/* GAUCHE */}
        <div className="profil-left">
          <div className="profil-container">
            <span className="profil-label">Nom d'utilisateur :</span>
            <div className="profil-row"><span>{user.username}</span></div>

            <span className="profil-label">Nom complet :</span>
            <div className="profil-row"><span>{user.full_name}</span></div>

            <span className="profil-label">Email :</span>
            <div className="profil-row"><span>{user.email}</span></div>

            <button className="button-toggle-form" onClick={() => setShowForm(prev => !prev)}>
              {showForm ? 'Annuler la modification' : 'Modifier mes informations'}
            </button>

            {showForm && ( <form onSubmit={handleSubmit}> 
              <div className="profil-field"> 
                <label className="profil-label">Nouveau nom complet :</label> 
                <div className="profil-value"> 
                  <input 
                  type="text" 
                  name="full_name" 
                  placeholder={user.full_name} 
                  onChange={handleChange} 
                  style={{ flex: 1, 
                          border: 'none', 
                          outline: 'none', 
                          background: 'transparent' }} /> 
                </div> 
              </div> 
              <div className="profil-field"> 
                <label className="profil-label">Nouvel email :</label> 
                <div className="profil-value"> 
                  <input 
                  type="email" 
                  name="email" 
                  placeholder={user.email} 
                  onChange={handleChange} 
                  style={{ flex: 1, 
                          border: 'none', 
                          outline: 'none', 
                          background: 'transparent' }} /> 
                </div> 
              </div> 
              <div className="profil-field"> 
                <label className="profil-label">Nouveau mot de passe :</label> 
                <div className="profil-value"> 
                  <input 
                    type="password" 
                    name="password" 
                    placeholder="••••••••" 
                    onChange={handleChange} 
                    style={{ flex: 1, 
                            border: 'none', 
                            outline: 'none', 
                            background: 'transparent' }} /> 
                </div> 
              </div> 
              <button className="button-update" type="submit"> 
                Mettre à jour les informations 
              </button> 
                  
            </form> )}

            <button className="button-delete" onClick={handleDeleteAccount}>Supprimer mon compte</button>
          </div>
        
        </div>

        {/* DROITE */}
        <div className="profil-right">
          <UserSearch token={token} />
          <DisplaySettings
            theme={theme}
            setTheme={setTheme}
            fontSize={fontSize}
            setFontSize={setFontSize}
          />
        </div>
      </div>
      
      <FriendList />
      <Logout />
      <Footer />
    </>
  );
};

export default Profil;
