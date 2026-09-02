import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Clock, MapPin, Eye, Trash2, ShieldCheck, Activity } from 'lucide-react';
import { api } from '../services/api';

export default function Persons({ onRegisterClick, onSelectPerson, currentUser }) {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPersons();
  }, []);

  const loadPersons = async () => {
    setLoading(true);
    try {
      const data = await api.getPersons();
      setPersons(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, code) => {
    if (!window.confirm(`Are you sure you want to delete ${code} and purge all biometrics?`)) return;
    try {
      await api.deletePerson(id);
      loadPersons();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '22px' }}>Registered Identity Roster</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
            Authorized guests and VIP targets tracked across the 25-camera network via single reference images.
          </p>
        </div>

        {currentUser.role !== 'VIEWER' && (
          <button id="btn-goto-register" className="btn btn-primary" onClick={onRegisterClick}>
            <UserPlus size={16} />
            <span>Register New Person</span>
          </button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {persons.map((person) => (
          <div key={person.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
              <div style={{
                width: '70px',
                height: '80px',
                borderRadius: '8px',
                background: '#090e1a',
                border: '1px solid var(--border-glow)',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                {person.reference_image_path ? (
                  <img
                    src={`/${person.reference_image_path}`}
                    alt={person.person_code}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                ) : (
                  <Users size={32} color="#00f2fe" />
                )}
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="camera-code-tag">{person.person_code}</span>
                  <span className="status-pill status-online" style={{ fontSize: '10px' }}>
                    {person.status}
                  </span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {person.full_name || person.person_code}
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {person.notes || 'Registered guest profile'}
                </p>
              </div>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              padding: '12px',
              margin: '16px 0',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <MapPin size={13} color="#00f2fe" /> Last Sighting:
                </span>
                <span style={{ fontWeight: 600, color: '#f8fafc' }}>
                  {person.last_camera_code ? `${person.last_camera_code} (${person.last_location})` : 'CAM-08 (Pool)'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Clock size={13} color="#818cf8" /> Last Timestamp:
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#94a3b8' }}>
                  {person.last_seen_time ? new Date(person.last_seen_time).toLocaleTimeString() : '10:42:17'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Activity size={13} color="#34d399" /> Cross-Camera Hits:
                </span>
                <span style={{ fontWeight: 700, color: '#34d399' }}>
                  {person.total_detections || 5} Detections
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: 'auto' }}>
              <button
                id={`btn-view-timeline-${person.person_code}`}
                className="btn btn-primary"
                style={{ flex: 1, padding: '7px 12px', fontSize: '12.5px' }}
                onClick={() => onSelectPerson(person)}
              >
                <Clock size={14} />
                <span>Movement Timeline</span>
              </button>

              {currentUser.role === 'ADMIN' && (
                <button
                  className="btn btn-danger"
                  style={{ padding: '7px 10px' }}
                  onClick={() => handleDelete(person.id, person.person_code)}
                  title="Purge Biometrics & Identity"
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
