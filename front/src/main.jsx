import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './styles/index.css'; // CCS Global



const savedTheme = localStorage.getItem('theme') || 'light';
document.body.setAttribute('data-theme', savedTheme);


const savedFontSize = localStorage.getItem('fontSize');
if (savedFontSize) {
  document.documentElement.style.setProperty('--font-size', `${savedFontSize}px`);
} else {
  document.documentElement.style.setProperty('--font-size', `16px`);
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
