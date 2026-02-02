import React, { useState } from 'react';
import { AuthProvider, useAuth } from './utils/AuthContext';
import AuthPage from './components/AuthPage';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import History from './components/HistoryPage';

const AppContent = () => {
  const { user, loading } = useAuth();
  const [page, setPage] = useState('dashboard');

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0a0f14' }}>
        <span style={{ color: '#5a6a7d', fontSize: '.85rem' }}>Initializing…</span>
      </div>
    );
  }

  if (!user) return <AuthPage />;

  return (
    <div className="app-shell">
      <Navbar page={page} setPage={setPage} />
      <main className="main-content">
        {page === 'dashboard' && <Dashboard />}
        {page === 'history'   && <History />}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <span style={styles.footerText}>
          ChemViz &mdash; Chemical Equipment Parameter Visualizer &nbsp;|&nbsp; Built with React + Django
        </span>
      </footer>
    </div>
  );
};

const App = () => (
  <AuthProvider>
    <AppContent />
  </AuthProvider>
);

const styles = {
  footer: {
    borderTop: '1px solid rgba(255,255,255,.06)',
    padding: '14px 24px',
    textAlign: 'center',
  },
  footerText: {
    color: '#3a4a5c',
    fontSize: '.72rem',
  },
};

export default App;
