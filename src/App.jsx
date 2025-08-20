import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
import Chat from './Chat';
import Settings from './Settings';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import './theme.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-transparent position-fixed w-100" style={{ zIndex: 1000, backdropFilter: 'blur(10px)', background: 'rgba(0, 0, 0, 0.8) !important' }}>
      <div className="container-fluid">
        <Link className="navbar-brand d-flex align-items-center" to="/">
          <div className="biomed-pulse me-2"></div>
          <span className="fw-bold text-gradient">Biomed Chat</span>
        </Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <Link className={`nav-link px-3 ${location.pathname === '/' ? 'active' : ''}`} to="/">
                <i className="fas fa-comments me-2"></i>Chat
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link px-3 ${location.pathname === '/settings' ? 'active' : ''}`} to="/settings">
                <i className="fas fa-cog me-2"></i>Settings
              </Link>
            </li>
          </ul>
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
