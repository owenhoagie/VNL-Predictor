import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import './NavBar.css';

export default function NavBar() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-logo" onClick={() => setMenuOpen(false)}>
          <span className="navbar-mark" aria-hidden="true">V</span>
          <span className="navbar-wordmark">
            <strong>VNL</strong>
            <small>Data Lab</small>
          </span>
        </Link>
        <button
          className="navbar-hamburger"
          onClick={() => setMenuOpen((open) => !open)}
          aria-controls="primary-navigation"
          aria-expanded={menuOpen}
          aria-label="Toggle menu"
        >
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </button>
        <div id="primary-navigation" className={`navbar-links${menuOpen ? ' open' : ''}`}>
          <Link to="/" className={location.pathname === '/' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Home</Link>
          <Link to="/visualize" className={location.pathname === '/visualize' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Explore</Link>
          <Link to="/lookup" className={location.pathname === '/lookup' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Players</Link>
          <Link to="/predict" className={location.pathname === '/predict' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Predict</Link>
        </div>
      </div>
    </nav>
  );
}
