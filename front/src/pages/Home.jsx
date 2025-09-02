
import { useNavigate } from 'react-router-dom';
import Header from "../components/Header";
import Footer from "../components/Footer";

function Home() {
  const navigate = useNavigate();

  return (
    <>
      <Header />
      <nav>
        <ul>
          <li><a href="#" onClick={() => navigate('/register')}>S’inscrire</a></li>
          <li><a href="#" onClick={() => navigate('/login')}>Se connecter</a></li>
        </ul>
      </nav>
      <main>
        <h2 style={{ textAlign: 'center', marginTop: '40px' }}>Bienvenue sur SUPRSS !</h2>
        <p className="custom-font" style={{ textAlign: 'justify' }}>Vos flux RSS ont bossé dur pendant que vous étiez absent. Résultat ? Une sélection aux petits oignons rien que pour vous. Bonne lecture, et n’oubliez pas : ici, c’est l’info qui vient à vous !</p>
      </main>

      <Footer />
    </>
  );
}

export default Home;
