import React, { useState } from 'react';
import { useAuth } from '../utils/AuthContext';

const AuthPage = () => {
  const { login, register } = useAuth();
  const [tab, setTab] = useState('login');       // 'login' | 'register'
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'login') {
        await login(form.username, form.password);
      } else {
        await register(form.username, form.email, form.password);
      }
    } catch (err) {
      const msg = err.response?.data;
      if (typeof msg === 'object') {
        setError(Object.values(msg).flat().join(' '));
      } else {
        setError('Something went wrong. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      {/* Background decoration */}
      <div style={styles.bgCircle1} />
      <div style={styles.bgCircle2} />

      <div style={styles.container}>
        {/* Logo */}
        <div style={styles.logo}>
          <svg width="40" height="40" viewBox="0 0 26 26" fill="none">
            <rect x="1" y="8" width="6" height="16" rx="2" fill="#00c8a0"/>
            <rect x="10" y="4" width="6" height="20" rx="2" fill="#3b82f6"/>
            <rect x="19" y="1" width="6" height="23" rx="2" fill="#a78bfa"/>
          </svg>
        </div>
        <h1 style={styles.title}>
          Chem<span style={{ color: '#00c8a0' }}>Viz</span>
        </h1>
        <p style={styles.subtitle}>Chemical Equipment Parameter Visualizer</p>

        {/* Tab switcher */}
        <div style={styles.tabs}>
          {['login', 'register'].map(t => (
            <button
              key={t}
              style={{ ...styles.tab, ...(tab === t ? styles.tabActive : {}) }}
              onClick={() => { setTab(t); setError(''); }}
            >
              {t === 'login' ? 'Sign In' : 'Register'}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && <div style={styles.errorBox}>{error}</div>}

        {/* Form */}
        <form onSubmit={submit} style={styles.form}>
          <label style={styles.label}>Username</label>
          <input className="input" name="username" value={form.username} onChange={handle} placeholder="your_username" required />

          {tab === 'register' && (
            <>
              <label style={styles.label} style2={styles.labelMt}>Email</label>
              <input className="input" name="email" type="email" value={form.email} onChange={handle} placeholder="you@example.com" style={{ marginTop: 10 }} />
            </>
          )}

          <label style={{ ...styles.label, marginTop: 10 }}>Password</label>
          <input className="input" name="password" type="password" value={form.password} onChange={handle} placeholder="••••••••" required minLength={6} />

          <button className="btn btn-primary" type="submit" disabled={loading} style={styles.submitBtn}>
            {loading ? 'Please wait…' : (tab === 'login' ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <p style={styles.footer}>
          {tab === 'login' ? "Don't have an account? " : "Already have an account? "}
          <span style={styles.switchLink} onClick={() => { setTab(tab === 'login' ? 'register' : 'login'); setError(''); }}>
            {tab === 'login' ? 'Register' : 'Sign In'}
          </span>
        </p>
      </div>
    </div>
  );
};

const styles = {
  wrapper: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#0a0f14',
    position: 'relative',
    overflow: 'hidden',
    padding: 24,
  },
  bgCircle1: {
    position: 'absolute',
    width: 500,
    height: 500,
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(0,200,160,.08) 0%, transparent 70%)',
    top: '-20%',
    left: '-15%',
    pointerEvents: 'none',
  },
  bgCircle2: {
    position: 'absolute',
    width: 400,
    height: 400,
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(59,130,246,.06) 0%, transparent 70%)',
    bottom: '-15%',
    right: '-10%',
    pointerEvents: 'none',
  },
  container: {
    width: '100%',
    maxWidth: 420,
    background: '#161e2a',
    border: '1px solid rgba(255,255,255,.07)',
    borderRadius: 16,
    padding: '36px 32px 28px',
    position: 'relative',
    zIndex: 1,
    boxShadow: '0 8px 40px rgba(0,0,0,.4)',
  },
  logo: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: 8,
  },
  title: {
    textAlign: 'center',
    fontSize: '1.8rem',
    color: '#e8ecf0',
    letterSpacing: '-0.03em',
  },
  subtitle: {
    textAlign: 'center',
    color: '#5a6a7d',
    fontSize: '.8rem',
    marginBottom: 24,
  },
  tabs: {
    display: 'flex',
    background: '#1a2332',
    borderRadius: 8,
    padding: 3,
    marginBottom: 20,
    gap: 4,
  },
  tab: {
    flex: 1,
    padding: '8px 0',
    border: 'none',
    background: 'transparent',
    color: '#5a6a7d',
    fontSize: '.85rem',
    fontWeight: 500,
    borderRadius: 6,
    cursor: 'pointer',
    transition: 'all .2s',
    fontFamily: 'Inter, sans-serif',
  },
  tabActive: {
    background: '#161e2a',
    color: '#e8ecf0',
    boxShadow: '0 1px 6px rgba(0,0,0,.3)',
  },
  errorBox: {
    background: 'rgba(239,68,68,.12)',
    border: '1px solid rgba(239,68,68,.3)',
    borderRadius: 6,
    padding: '8px 12px',
    color: '#ef4444',
    fontSize: '.82rem',
    marginBottom: 14,
    lineHeight: 1.4,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  label: {
    color: '#8a9bb0',
    fontSize: '.78rem',
    fontWeight: 500,
    marginTop: 10,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  submitBtn: {
    marginTop: 20,
    width: '100%',
    justifyContent: 'center',
    padding: '11px 0',
    fontSize: '.9rem',
  },
  footer: {
    textAlign: 'center',
    color: '#5a6a7d',
    fontSize: '.8rem',
    marginTop: 20,
  },
  switchLink: {
    color: '#00c8a0',
    cursor: 'pointer',
    fontWeight: 500,
  },
};

export default AuthPage;
