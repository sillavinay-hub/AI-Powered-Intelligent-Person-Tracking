import React, { useState } from 'react';
import { Shield, Lock, User, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login(username, password);
      onLoginSuccess(data);
    } catch (err) {
      setError(err.message || 'Invalid credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickRole = (user, pass) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px'
    }}>
      <div className="glass-panel glass-panel-accent" style={{ width: '100%', maxWidth: '440px', padding: '36px' }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            display: 'inline-flex',
            padding: '14px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)',
            boxShadow: '0 0 25px rgba(0, 242, 254, 0.4)',
            marginBottom: '16px'
          }}>
            <Shield size={32} color="#070a13" strokeWidth={2.5} />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 800 }}>ResortVision AI</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px', marginTop: '4px' }}>
            Intelligent Multi-Camera Person Tracking & Analytics
          </p>
        </div>

        {error && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 14px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#f87171',
            fontSize: '13px',
            marginBottom: '20px'
          }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <div style={{ position: 'relative' }}>
              <input
                id="input-username"
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                style={{ paddingLeft: '38px' }}
              />
              <User size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '13px' }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                id="input-password"
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ paddingLeft: '38px' }}
              />
              <Lock size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '13px' }} />
            </div>
          </div>

          <button
            id="btn-login-submit"
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '12px', marginTop: '10px', fontSize: '14.5px' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Access Platform'}
          </button>
        </form>

        <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', textAlign: 'center', marginBottom: '10px' }}>
            Quick Demo Role Selector
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '12px', padding: '7px 4px' }}
              onClick={() => handleQuickRole('admin', 'admin123')}
            >
              Admin
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '12px', padding: '7px 4px' }}
              onClick={() => handleQuickRole('operator', 'operator123')}
            >
              Operator
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '12px', padding: '7px 4px' }}
              onClick={() => handleQuickRole('viewer', 'viewer123')}
            >
              Viewer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
