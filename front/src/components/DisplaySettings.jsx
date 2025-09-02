import { useEffect, useState } from 'react';

const DisplaySettings = () => {
  const [theme, setTheme] = useState('light');
  const [fontSize, setFontSize] = useState('medium');

  // Récupération des préférences sauvegardées
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const savedFontSize = localStorage.getItem("fontSize");

    if (savedTheme) {
      setTheme(savedTheme);
      document.body.setAttribute("data-theme", savedTheme);
    }

    if (savedFontSize) {
      const value = parseInt(savedFontSize);
      let sizeLabel = 'medium';
      if (value <= 14) sizeLabel = 'small';
      else if (value >= 18) sizeLabel = 'large';

      setFontSize(sizeLabel);
      document.documentElement.style.setProperty('--font-size', `${value}px`);
    } else {
      // Valeur par défaut
      document.documentElement.style.setProperty('--font-size', `16px`);
    }
  }, []);

  const handleThemeChange = (mode) => {
    setTheme(mode);
    document.body.setAttribute("data-theme", mode);
    localStorage.setItem("theme", mode);
  };

  const handleFontSizeSliderChange = (e) => {
    const value = parseInt(e.target.value);
    let sizeLabel = 'medium';
    if (value <= 14) sizeLabel = 'small';
    else if (value >= 18) sizeLabel = 'large';

    setFontSize(sizeLabel);
    document.documentElement.style.setProperty('--font-size', `${value}px`);
    localStorage.setItem("fontSize", value);
  };

  const getSliderValue = () => {
    switch (fontSize) {
      case 'small': return 14;
      case 'large': return 18;
      default: return 16;
    }
  };

  const getFontSizeLabel = () => {
    switch (fontSize) {
      case 'small': return 'Petite';
      case 'large': return 'Grande';
      default: return 'Moyenne';
    }
  };

  return (
    <div className="profil-settings">
      <h3 className="profil-label">Paramètres d'affichage</h3>

      {/* Mode sombre */}
      <div className="profil-field">
        <label htmlFor="theme-toggle">Changer le thème :</label>
        <label className="switch">
          <input
            type="checkbox"
            id="theme-toggle"
            onChange={(e) => handleThemeChange(e.target.checked ? 'dark' : 'light')}
            checked={theme === 'dark'}
          />
          <span className="slider round"></span>
        </label>
      </div>

      {/* Taille de police */}
      <div className="profil-field">
        <label htmlFor="font-size-slider">Taille de police :</label>
        <label className="slider-container">
          <input
            type="range"
            id="font-size-slider"
            min="14"
            max="18"
            step="2"
            value={getSliderValue()}
            onChange={handleFontSizeSliderChange}
          />
          <span>{getFontSizeLabel()}</span>
        </label>
      </div>
    </div>
  );
};

export default DisplaySettings;
