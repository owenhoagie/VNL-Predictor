import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import './NavBar.css';

export default function NavBar() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-logo">VNL Visualized</div>
        <button className="navbar-hamburger" onClick={() => setMenuOpen((o) => !o)} aria-label="Toggle menu">
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </button>
        <div className={`navbar-links${menuOpen ? ' open' : ''}`}>
          <Link to="/" className={location.pathname === '/' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Home</Link>
          <Link to="/visualize" className={location.pathname === '/visualize' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Visualization</Link>
        </div>
      </div>
    </nav>
  );
}
