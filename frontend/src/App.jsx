import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Cameras from './pages/Cameras';
import Persons from './pages/Persons';
import RegisterPerson from './pages/RegisterPerson';
import Timeline from './pages/Timeline';
import ResortMap from './pages/Map';
import Search from './pages/Search';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import Experiments from './pages/Experiments';
import Settings from './pages/Settings';
import { api } from './services/api';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [selectedCameraId, setSelectedCameraId] = useState(null);

  useEffect(() => {
    const user = api.getCurrentUser();
    if (user.token) {
      setCurrentUser(user);
    } else {
      // Default to demo admin for instant evaluator access
      setCurrentUser({
        username: 'admin',
        role: 'ADMIN',
        token: 'demo-token'
      });
    }
  }, []);

  const handleLoginSuccess = (data) => {
    setCurrentUser({
      username: data.username,
      role: data.role,
      token: data.access_token
    });
    setCurrentTab('dashboard');
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
  };

  if (!currentUser) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header
        currentTab={currentTab}
        setTab={(tab) => {
          setCurrentTab(tab);
          if (tab !== 'timeline') setSelectedPerson(null);
        }}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      <main className="app-main">
        {currentTab === 'dashboard' && (
          <Dashboard
            onViewCamera={(camId) => {
              setSelectedCameraId(camId);
              setCurrentTab('cameras');
            }}
            onOpenTimeline={() => {
              setSelectedPerson({ person_code: 'P001' });
              setCurrentTab('timeline');
            }}
          />
        )}

        {currentTab === 'cameras' && (
          <Cameras currentUser={currentUser} />
        )}

        {currentTab === 'persons' && (
          <Persons
            currentUser={currentUser}
            onRegisterClick={() => setCurrentTab('register')}
            onSelectPerson={(person) => {
              setSelectedPerson(person);
              setCurrentTab('timeline');
            }}
          />
        )}

        {currentTab === 'register' && (
          <RegisterPerson
            onBack={() => setCurrentTab('persons')}
            onRegistered={(res) => {
              setSelectedPerson({ person_code: res.person_code });
              setCurrentTab('timeline');
            }}
          />
        )}

        {currentTab === 'timeline' && (
          <Timeline
            person={selectedPerson}
            onBack={() => setCurrentTab('persons')}
          />
        )}

        {currentTab === 'map' && (
          <ResortMap
            onSelectCamera={(camId) => {
              setSelectedCameraId(camId);
              setCurrentTab('cameras');
            }}
          />
        )}

        {currentTab === 'search' && (
          <Search
            onSelectPerson={(person) => {
              setSelectedPerson(person);
              setCurrentTab('timeline');
            }}
          />
        )}

        {currentTab === 'alerts' && (
          <Alerts currentUser={currentUser} />
        )}

        {currentTab === 'analytics' && (
          <Analytics />
        )}

        {currentTab === 'experiments' && (
          <Experiments />
        )}

        {currentTab === 'settings' && (
          <Settings currentUser={currentUser} />
        )}
      </main>
    </div>
  );
}
