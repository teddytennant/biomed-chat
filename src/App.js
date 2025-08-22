import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
import Chat from './Chat';
import Settings from './Settings';

import './index.css';
import './theme.css';
import './App.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link className="nav-brand" to="/">
          <span>Biomed Chat</span>
        </Link>
        <div className="nav-links">
          <Link className={`nav-link ${location.pathname === '/' ? 'active' : ''}`} to="/">
            Chat
          </Link>
          <Link className={`nav-link ${location.pathname === '/settings' ? 'active' : ''}`} to="/settings">
            Settings
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
