import React from 'react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <h1>Customer Support AI</h1>
          <p className="subtitle">AI-Powered Response Generator using Semantic Search & LLM</p>
        </div>
        <div className="tag-section">
          <span className="tech-tag">Pinecone Vector DB</span>
          <span className="tech-tag">Sarvam AI</span>
          <span className="tech-tag">Semantic Search</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
