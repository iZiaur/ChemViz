import React, { useState } from 'react';
import { useAuth } from '../utils/AuthContext';

const Navbar = ({ page, setPage }) => {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const navLinks = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'history',   label: 'History' },
  ];

  return (
    <nav style={styles.nav}>
      <div style={styles.navInner}>
        {/* Brand */}
        <div style={styles.brand} onClick={() => setPage('dashboard')} role="button" tabIndex={0}>
          <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
            <rect x="1" y="8" width="6" height="16" rx="2" fill="#00c8a0"/>
            <rect x="10" y="4" width="6" height="20" rx="2" fill="#3b82f6"/>
            <rect x="19" y="1" width="6" height="23" rx="2" fill="#a78bfa"/>
          </svg>
          <span style={styles.brandName}>Chem<span style={{ color: '#00c8a0' }}>Viz</span></span>
        </div>

        {/* Desktop Links */}
        <div style={styles.links}>
          {navLinks.map(l => (
            <button
              key={l.key}
              className="btn btn-secondary btn-sm"
              style={{ ...(page === l.key ? styles.linkActive : {}) }}
              onClick={() => setPage(l.key)}
            >
              {l.label}
            </button>
          ))}
        </div>

        {/* User / hamburger */}
        <div style={styles.userArea}>
          {user && (
            <div style={styles.userBadge}>
              <span style={styles.avatar}>{user.username[0].toUpperCase()}</span>
              <span style={styles.username}>{user.username}</span>
              <button className="btn btn-secondary btn-sm" onClick={logout}>Logout</button>
            </div>
          )}
          <button className="btn btn-secondary btn-sm" style={styles.hamburger} onClick={() => setMenuOpen(!menuOpen)}>
            ☰
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div style={styles.mobileMenu}>
          {navLinks.map(l => (
            <button key={l.key} className="btn btn-secondary" onClick={() => { setPage(l.key); setMenuOpen(false); }}>
              {l.label}
            </button>
          ))}
          {user && <button className="btn btn-danger" onClick={logout}>Logout</button>}
        </div>
      )}
    </nav>
  );
};

const styles = {
  nav: {
    background: '#111820',
    borderBottom: '1px solid rgba(255,255,255,.07)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  navInner: {
    maxWidth: 1280,
    margin: '0 auto',
    padding: '0 24px',
    height: 58,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 16,
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    cursor: 'pointer',
    userSelect: 'none',
  },
  brandName: {
    fontSize: '1.2rem',
    fontWeight: 700,
    color: '#e8ecf0',
    letterSpacing: '-0.03em',
  },
  links: {
    display: 'flex',
    gap: 8,
  },
  linkActive: {
    borderColor: 'rgba(0,200,160,.4)',
    color: '#00c8a0',
  },
  userArea: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  userBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: '50%',
    background: 'rgba(0,200,160,.2)',
    color: '#00c8a0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '.8rem',
    fontWeight: 600,
  },
  username: {
    color: '#8a9bb0',
    fontSize: '.8rem',
  },
  hamburger: {
    display: 'none',
  },
  mobileMenu: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    padding: '12px 24px 16px',
    borderTop: '1px solid rgba(255,255,255,.07)',
  },
};

export default Navbar;
