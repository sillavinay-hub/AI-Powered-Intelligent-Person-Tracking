import React from 'react';
import { 
  ShieldAlert, 
  Camera, 
  Users, 
  MapPin, 
  Search, 
  Bell, 
  BarChart3, 
  FlaskConical, 
  Settings, 
  LogOut, 
  LayoutGrid 
} from 'lucide-react';

export default function Header({ currentTab, setTab, currentUser, onLogout }) {
  const navLinks = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
    { id: 'cameras', label: '25 Cameras', icon: Camera },
    { id: 'persons', label: 'Persons', icon: Users },
    { id: 'map', label: 'Resort Map', icon: MapPin },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'experiments', label: 'Experiments', icon: FlaskConical },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="app-header">
      <div className="brand-container">
        <div className="brand-badge">
          <ShieldAlert size={22} color="#070a13" strokeWidth={2.5} />
        </div>
        <div>
          <h1 className="brand-title" style={{ margin: 0, fontSize: '19px', lineHeight: 1.2 }}>ResortVision AI</h1>
          <div className="brand-subtitle">Intelligent Multi-Camera Tracking</div>
        </div>
      </div>

      <nav className="nav-links">
        {navLinks.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setTab(item.id)}
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="user-pill">
          <div className="status-dot" style={{ background: '#10b981', boxShadow: '0 0 8px #10b981' }} />
          <span style={{ fontSize: '13px', fontWeight: 600 }}>{currentUser.username}</span>
          <span className={`role-badge role-${currentUser.role}`}>{currentUser.role}</span>
        </div>

        <button 
          id="btn-logout"
          className="btn btn-secondary" 
          style={{ padding: '7px 12px', fontSize: '12px' }}
          onClick={onLogout}
          title="Sign Out"
        >
          <LogOut size={14} />
          <span>Exit</span>
        </button>
      </div>
    </header>
  );
}
