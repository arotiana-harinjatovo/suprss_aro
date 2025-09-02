import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Register from './pages/Register'; 
import Login from './pages/Login';
import HomePage from './pages/HomePage';
import Profile from './pages/Profile';
import CollectionsPage from './pages/CollectionsPage';
import CreateCollectionPage from './components/CreateCollectionPage';
import AddFeedToCollectionPage from './components/AddFeedToCollectionPage';
import CollectionIdPage from './pages/CollectionIdPage';
import ForgotPassword from './components/ForgotPassword';
import LoginCallBack from './components/LoginCallBack';
import ResetPassword from './components/ResetPassword';
import Notifications from './components/Notifications';
import FriendList from './components/FriendList';
import FeedEditPage from './pages/FeedEditPage';
import FeedsListPage from './pages/FeedsListPage';
import ArticleListPage from './pages/ArticleListPage';



function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profil" element={<Profile />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/bibliotheque" element={<FeedsListPage />} />
        <Route path="/favoris" element={<ArticleListPage />} />
        <Route path="/collections" element={<CollectionsPage />} />
        <Route path="/collections/create" element={<CreateCollectionPage />} />
        <Route path="/collections/:collectionId/add-feed" element={<AddFeedToCollectionPage />} />
        <Route path="/collections/:collectionId" element={<CollectionIdPage />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/auth/:provider/callback" element={<LoginCallBack />} />
        <Route path="/followers/notifications" element={<Notifications />} />
        <Route path="/feeds/:feedId/edit" element={<FeedEditPage />} />
        <Route path="/followers/accepted" element={<FriendList />} />
      </Routes>
    </Router>
  );
}

export default App;
