import React, { useState, useEffect } from 'react';
import { Bell, AlertTriangle, CheckCircle, ShieldAlert, Download, RefreshCw, Clock } from 'lucide-react';
import { api } from '../services/api';

export default function Alerts({ currentUser }) {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts(filter);
      setAlerts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (alertId, newStatus) => {
    try {
      await api.updateAlertStatus(alertId, newStatus);
      loadAlerts();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleExport = () => {
    window.open('/api/alerts/export/csv', '_blank');
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '22px' }}>Security & Anomaly Alert Center</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
            Rule-based anomaly notifications: restricted-zone incursions, loitering, after-hours facility access.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={handleExport}>
            <Download size={14} />
            <span>Export CSV</span>
          </button>

          <button className="btn btn-secondary" onClick={loadAlerts}>
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '18px' }}>
        {['', 'NEW', 'ACKNOWLEDGED', 'RESOLVED'].map((st) => (
          <button
            key={st}
            className={`btn ${filter === st ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 14px', fontSize: '12px' }}
            onClick={() => setFilter(st)}
          >
            {st === '' ? 'All Alerts' : st}
          </button>
        ))}
      </div>

      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Target Person</th>
              <th>Location</th>
              <th>Timestamp</th>
              <th>Confidence</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                  No security alerts found matching current filter.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.id}>
                  <td>
                    <span className="status-pill status-alert">
                      <AlertTriangle size={12} />
                      {alert.alert_type}
                    </span>
                  </td>
                  <td>
                    <span className="camera-code-tag">{alert.person_code || 'UNREGISTERED'}</span>
                  </td>
                  <td>
                    <strong>{alert.camera_code}</strong> : {alert.location}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)' }}>
                    {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : ''}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#00f2fe' }}>
                    {Math.round((alert.confidence || 0.9) * 100)}%
                  </td>
                  <td>
                    <span style={{
                      fontSize: '11px',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      padding: '3px 8px',
                      borderRadius: '4px',
                      background: alert.status === 'NEW' ? 'rgba(239, 68, 68, 0.2)' : alert.status === 'ACKNOWLEDGED' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                      color: alert.status === 'NEW' ? '#f87171' : alert.status === 'ACKNOWLEDGED' ? '#fbbf24' : '#34d399'
                    }}>
                      {alert.status}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    {currentUser.role !== 'VIEWER' && (
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        {alert.status === 'NEW' && (
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '11.5px' }}
                            onClick={() => handleUpdateStatus(alert.id, 'ACKNOWLEDGED')}
                          >
                            Acknowledge
                          </button>
                        )}
                        {alert.status !== 'RESOLVED' && (
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '11.5px', color: '#34d399' }}
                            onClick={() => handleUpdateStatus(alert.id, 'RESOLVED')}
                          >
                            Resolve
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
