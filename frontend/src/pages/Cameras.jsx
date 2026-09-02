import React, { useState, useEffect } from 'react';
import { Camera, Plus, RefreshCw, Activity, CheckCircle, AlertCircle, Trash2, Edit3, X } from 'lucide-react';
import { api } from '../services/api';

export default function Cameras({ currentUser }) {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testModal, setTestModal] = useState(null);
  const [testing, setTesting] = useState(false);
  const [addModalOpen, setAddModalOpen] = useState(false);

  // New Camera Form
  const [newCam, setNewCam] = useState({
    camera_code: '',
    name: '',
    location: '',
    source_type: 'DEMO',
    rtsp_url: '',
    fps: 10.0,
    ai_enabled: true
  });

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    setLoading(true);
    try {
      const data = await api.getCameras();
      setCameras(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTestCamera = async (camId) => {
    setTesting(true);
    setTestModal({ loading: true });
    try {
      const res = await api.testCamera(camId);
      setTestModal(res);
    } catch (e) {
      setTestModal({
        status: 'ERROR',
        message: e.message,
        latency_ms: 0
      });
    } finally {
      setTesting(false);
    }
  };

  const handleCreateCamera = async (e) => {
    e.preventDefault();
    try {
      await api.createCamera(newCam);
      setAddModalOpen(false);
      loadCameras();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteCamera = async (id, code) => {
    if (!window.confirm(`Are you sure you want to delete camera ${code}?`)) return;
    try {
      await api.deleteCamera(id);
      loadCameras();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '22px' }}>Camera Network Infrastructure</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
            Database-driven configuration for 25 surveillance feeds across resort perimeter & facilities.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={loadCameras}>
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
          {currentUser.role === 'ADMIN' && (
            <button className="btn btn-primary" onClick={() => setAddModalOpen(true)}>
              <Plus size={14} />
              <span>Add Camera</span>
            </button>
          )}
        </div>
      </div>

      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Location</th>
              <th>Source Type</th>
              <th>Status</th>
              <th>AI Processing</th>
              <th>Target FPS</th>
              <th>Heartbeat</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {cameras.map((cam) => (
              <tr key={cam.id}>
                <td>
                  <span className="camera-code-tag">{cam.camera_code}</span>
                </td>
                <td style={{ fontWeight: 600 }}>{cam.name}</td>
                <td style={{ color: 'var(--text-secondary)' }}>{cam.location}</td>
                <td>
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: 'rgba(255, 255, 255, 0.05)'
                  }}>
                    {cam.source_type}
                  </span>
                </td>
                <td>
                  <span className={`status-pill status-${cam.status.toLowerCase()}`}>
                    <span className="status-dot" />
                    {cam.status}
                  </span>
                </td>
                <td>
                  <span style={{
                    color: cam.ai_enabled ? '#34d399' : '#64748b',
                    fontSize: '12.5px',
                    fontWeight: 600
                  }}>
                    {cam.ai_enabled ? '● Active' : '○ Bypassed'}
                  </span>
                </td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{cam.fps || 10} FPS</td>
                <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {cam.last_heartbeat ? new Date(cam.last_heartbeat).toLocaleTimeString() : 'Live'}
                </td>
                <td style={{ textAlign: 'right' }}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <button
                      id={`btn-test-${cam.camera_code}`}
                      className="btn btn-secondary"
                      style={{ padding: '5px 10px', fontSize: '12px' }}
                      onClick={() => handleTestCamera(cam.id)}
                    >
                      <Activity size={13} />
                      <span>Test</span>
                    </button>
                    {currentUser.role === 'ADMIN' && (
                      <button
                        className="btn btn-danger"
                        style={{ padding: '5px 8px' }}
                        onClick={() => handleDeleteCamera(cam.id, cam.camera_code)}
                        title="Delete Camera"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Test Camera Modal */}
      {testModal && (
        <div className="modal-backdrop">
          <div className="glass-panel modal-content" style={{ position: 'relative' }}>
            <button
              style={{ position: 'absolute', right: '16px', top: '16px', background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              onClick={() => setTestModal(null)}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '18px', marginBottom: '14px' }}>Camera Connection Diagnostic</h3>

            {testModal.loading ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <RefreshCw size={28} className="spin" color="#00f2fe" style={{ animation: 'spin 1s linear infinite' }} />
                <p style={{ marginTop: '12px', color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Connecting to camera stream and acquiring test frame...
                </p>
              </div>
            ) : (
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  background: testModal.status === 'ONLINE' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                  border: `1px solid ${testModal.status === 'ONLINE' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '8px',
                  marginBottom: '18px'
                }}>
                  {testModal.status === 'ONLINE' ? (
                    <CheckCircle size={20} color="#34d399" />
                  ) : (
                    <AlertCircle size={20} color="#f87171" />
                  )}
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '14px' }}>
                      Status: {testModal.status} ({testModal.latency_ms} ms)
                    </div>
                    <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>{testModal.message}</div>
                  </div>
                </div>

                {testModal.frame_preview_base64 && (
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
                      Live Snapshot Preview:
                    </div>
                    <img
                      src={testModal.frame_preview_base64}
                      alt="Camera Test Preview"
                      style={{ width: '100%', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}
                    />
                  </div>
                )}

                <div style={{ marginTop: '20px', textAlign: 'right' }}>
                  <button className="btn btn-secondary" onClick={() => setTestModal(null)}>
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Camera Modal */}
      {addModalOpen && (
        <div className="modal-backdrop">
          <div className="glass-panel modal-content" style={{ position: 'relative' }}>
            <button
              style={{ position: 'absolute', right: '16px', top: '16px', background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              onClick={() => setAddModalOpen(false)}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '18px', marginBottom: '18px' }}>Register New Surveillance Camera</h3>

            <form onSubmit={handleCreateCamera}>
              <div className="form-group">
                <label className="form-label">Camera Identifier (e.g. CAM-26)</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  placeholder="CAM-26"
                  value={newCam.camera_code}
                  onChange={(e) => setNewCam({ ...newCam, camera_code: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Camera Name</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  placeholder="e.g. Private Villa South Pathway"
                  value={newCam.name}
                  onChange={(e) => setNewCam({ ...newCam, name: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Location / Zone</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  placeholder="e.g. South Residential Sector"
                  value={newCam.location}
                  onChange={(e) => setNewCam({ ...newCam, location: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Stream Source Type</label>
                <select
                  className="form-select"
                  value={newCam.source_type}
                  onChange={(e) => setNewCam({ ...newCam, source_type: e.target.value })}
                >
                  <option value="DEMO">Synthetic Simulated Stream (Demo Mode)</option>
                  <option value="RTSP">Live IP Camera (RTSP Stream)</option>
                  <option value="VIDEO_FILE">Pre-recorded Video File (MP4/AVI)</option>
                  <option value="WEBCAM">Hardware Webcam</option>
                </select>
              </div>

              {newCam.source_type === 'RTSP' && (
                <div className="form-group">
                  <label className="form-label">RTSP Stream URL</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="rtsp://admin:secret@192.168.1.100:554/stream1"
                    value={newCam.rtsp_url}
                    onChange={(e) => setNewCam({ ...newCam, rtsp_url: e.target.value })}
                  />
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setAddModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Camera
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
