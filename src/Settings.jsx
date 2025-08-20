import React, { useState } from 'react';
import './Settings.css';

const Settings = () => {
  const [theme, setTheme] = useState('light');
  const [language, setLanguage] = useState('en');
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
  });
  const [privacy, setPrivacy] = useState('private');

  const handleNotificationChange = (e) => {
    setNotifications({
      ...notifications,
      [e.target.name]: e.target.checked,
    });
  };

  return (
    <div className={`settings-container ${theme}`}>
      <h2>Settings</h2>
      <div className="setting-item">
        <label>Theme:</label>
        <select value={theme} onChange={(e) => setTheme(e.target.value)}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
      <div className="setting-item">
        <label>Language:</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>
      </div>
      <div className="setting-item">
        <label>Notifications:</label>
        <div className="checkbox-group">
          <input
            type="checkbox"
            name="email"
            checked={notifications.email}
            onChange={handleNotificationChange}
          />
          <label>Email</label>
        </div>
        <div className="checkbox-group">
          <input
            type="checkbox"
            name="push"
            checked={notifications.push}
            onChange={handleNotificationChange}
          />
          <label>Push Notifications</label>
        </div>
      </div>
      <div className="setting-item">
        <label>Data Privacy:</label>
        <div className="radio-group">
          <input
            type="radio"
            name="privacy"
            value="private"
            checked={privacy === 'private'}
            onChange={(e) => setPrivacy(e.target.value)}
          />
          <label>Private</label>
        </div>
        <div className="radio-group">
          <input
            type="radio"
            name="privacy"
            value="public"
            checked={privacy === 'public'}
            onChange={(e) => setPrivacy(e.target.value)}
          />
          <label>Public</label>
        </div>
      </div>
    </div>
  );
};

export default Settings;
