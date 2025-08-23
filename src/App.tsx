import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
import Chat from './Chat.tsx';
import Settings from './Settings.tsx';

import './index.css';
import './theme.css';
import './App.css';

function MinimalHeader() {
  return (
    <header className="minimal-header">
      <div className="header-content">
        <h1 className="header-title">Biomed Chat</h1>
      </div>
    </header>
  );
}

function App() {
  return (
    <Router>
      <div className="fixed-layout">
        <MinimalHeader />
        <main className="content-area">
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
