import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Row, Col, Alert } from 'react-bootstrap';
import './Settings.css';

const Settings = () => {
  const [theme, setTheme] = useState('dark');
  const [language, setLanguage] = useState('en');
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    browser: true,
  });
  const [privacy, setPrivacy] = useState('private');
  const [autoSave, setAutoSave] = useState(true);
  const [messagePreview, setMessagePreview] = useState(true);
  const [saved, setSaved] = useState(false);

  // Load settings from localStorage on component mount
  useEffect(() => {
    const loadSettings = () => {
      try {
        const savedSettings = localStorage.getItem('biomedChatSettings');
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings);
          setTheme(parsed.theme || 'dark');
          setLanguage(parsed.language || 'en');
          setNotifications(parsed.notifications || { email: true, push: false, browser: true });
          setPrivacy(parsed.privacy || 'private');
          setAutoSave(parsed.autoSave !== undefined ? parsed.autoSave : true);
          setMessagePreview(parsed.messagePreview !== undefined ? parsed.messagePreview : true);
        }
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    };

    loadSettings();
  }, []);

  // Apply theme changes immediately
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('biomedChatTheme', theme);
  }, [theme]);

  // Request notification permission if browser notifications are enabled
  useEffect(() => {
    if (notifications.browser && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, [notifications.browser]);

  const handleNotificationChange = (e) => {
    setNotifications({
      ...notifications,
      [e.target.name]: e.target.checked,
    });
  };

  const handleSave = () => {
    const settings = {
      theme,
      language,
      notifications,
      privacy,
      autoSave,
      messagePreview,
      lastUpdated: new Date().toISOString()
    };

    try {
      localStorage.setItem('biomedChatSettings', JSON.stringify(settings));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);

      // Show browser notification if enabled
      if (notifications.browser) {
        new Notification('Settings Saved', {
          body: 'Your Biomed Chat settings have been saved successfully.',
          icon: '/vite.svg'
        });
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings. Please try again.');
    }
  };

  const handleReset = () => {
    const defaultSettings = {
      theme: 'dark',
      language: 'en',
      notifications: { email: true, push: false, browser: true },
      privacy: 'private',
      autoSave: true,
      messagePreview: true
    };

    setTheme(defaultSettings.theme);
    setLanguage(defaultSettings.language);
    setNotifications(defaultSettings.notifications);
    setPrivacy(defaultSettings.privacy);
    setAutoSave(defaultSettings.autoSave);
    setMessagePreview(defaultSettings.messagePreview);

    try {
      localStorage.setItem('biomedChatSettings', JSON.stringify(defaultSettings));
    } catch (error) {
      console.error('Error resetting settings:', error);
    }
  };

  return (
    <Container className="settings-container">
      <div className="settings-header">
        <h1 className="text-gradient mb-2">Settings</h1>
        <p className="text-muted">Customize your Biomed Chat experience</p>
      </div>

      {saved && (
        <Alert variant="success" className="settings-alert">
          <i className="fas fa-check-circle me-2"></i>
          Settings saved successfully!
        </Alert>
      )}

      <Row className="settings-grid">
        <Col lg={8}>
          <Card className="settings-card">
            <Card.Header className="settings-card-header">
              <i className="fas fa-palette me-2"></i>
              Appearance
            </Card.Header>
            <Card.Body>
              <div className="setting-group">
                <label className="setting-label">Theme</label>
                <p className="setting-description">Choose your preferred color scheme</p>
                <Form.Select
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  className="modern-select"
                >
                  <option value="dark">Dark (Biomedical)</option>
                  <option value="light">Light</option>
                  <option value="auto">Auto (System)</option>
                </Form.Select>
              </div>
            </Card.Body>
          </Card>

          <Card className="settings-card">
            <Card.Header className="settings-card-header">
              <i className="fas fa-globe me-2"></i>
              Language & Region
            </Card.Header>
            <Card.Body>
              <div className="setting-group">
                <label className="setting-label">Language</label>
                <p className="setting-description">Select your preferred language</p>
                <Form.Select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="modern-select"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="it">Italian</option>
                  <option value="pt">Portuguese</option>
                </Form.Select>
              </div>
            </Card.Body>
          </Card>

          <Card className="settings-card">
            <Card.Header className="settings-card-header">
              <i className="fas fa-bell me-2"></i>
              Notifications
            </Card.Header>
            <Card.Body>
              <div className="setting-group">
                <label className="setting-label">Notification Preferences</label>
                <p className="setting-description">Choose how you want to be notified</p>
                <div className="checkbox-container">
                  <Form.Check
                    type="switch"
                    id="email-notif"
                    name="email"
                    checked={notifications.email}
                    onChange={handleNotificationChange}
                    label="Email notifications"
                    className="modern-switch"
                  />
                  <Form.Check
                    type="switch"
                    id="push-notif"
                    name="push"
                    checked={notifications.push}
                    onChange={handleNotificationChange}
                    label="Push notifications"
                    className="modern-switch"
                  />
                  <Form.Check
                    type="switch"
                    id="browser-notif"
                    name="browser"
                    checked={notifications.browser}
                    onChange={handleNotificationChange}
                    label="Browser notifications"
                    className="modern-switch"
                  />
                </div>
              </div>
            </Card.Body>
          </Card>

          <Card className="settings-card">
            <Card.Header className="settings-card-header">
              <i className="fas fa-shield-alt me-2"></i>
              Privacy & Security
            </Card.Header>
            <Card.Body>
              <div className="setting-group">
                <label className="setting-label">Data Privacy</label>
                <p className="setting-description">Control who can see your data</p>
                <div className="radio-container">
                  <Form.Check
                    type="radio"
                    name="privacy"
                    value="private"
                    checked={privacy === 'private'}
                    onChange={(e) => setPrivacy(e.target.value)}
                    label="Private - Only you can access your data"
                    className="modern-radio"
                  />
                  <Form.Check
                    type="radio"
                    name="privacy"
                    value="public"
                    checked={privacy === 'public'}
                    onChange={(e) => setPrivacy(e.target.value)}
                    label="Public - Allow anonymous usage analytics"
                    className="modern-radio"
                  />
                </div>
              </div>
            </Card.Body>
          </Card>

          <Card className="settings-card">
            <Card.Header className="settings-card-header">
              <i className="fas fa-cogs me-2"></i>
              Chat Preferences
            </Card.Header>
            <Card.Body>
              <div className="setting-group">
                <div className="checkbox-container">
                  <Form.Check
                    type="switch"
                    id="autosave"
                    checked={autoSave}
                    onChange={(e) => setAutoSave(e.target.checked)}
                    label="Auto-save conversations"
                    className="modern-switch"
                  />
                  <Form.Check
                    type="switch"
                    id="preview"
                    checked={messagePreview}
                    onChange={(e) => setMessagePreview(e.target.checked)}
                    label="Show message preview"
                    className="modern-switch"
                  />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          <Card className="settings-card sidebar-card">
            <Card.Header className="settings-card-header">
              <i className="fas fa-info-circle me-2"></i>
              Quick Info
            </Card.Header>
            <Card.Body>
              <div className="info-item">
                <h6>Current Theme</h6>
                <p className="text-muted">{theme.charAt(0).toUpperCase() + theme.slice(1)}</p>
              </div>
              <div className="info-item">
                <h6>Language</h6>
                <p className="text-muted">{language.toUpperCase()}</p>
              </div>
              <div className="info-item">
                <h6>Notifications</h6>
                <p className="text-muted">
                  {Object.values(notifications).filter(Boolean).length} enabled
                </p>
              </div>
            </Card.Body>
          </Card>

          <Card className="settings-card sidebar-card">
            <Card.Body className="text-center">
              <Button
                variant="primary"
                onClick={handleSave}
                className="w-100 mb-2 save-button"
              >
                <i className="fas fa-save me-2"></i>
                Save Settings
              </Button>
              <Button
                variant="outline-secondary"
                onClick={handleReset}
                className="w-100 reset-button"
              >
                <i className="fas fa-undo me-2"></i>
                Reset to Defaults
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Settings;
