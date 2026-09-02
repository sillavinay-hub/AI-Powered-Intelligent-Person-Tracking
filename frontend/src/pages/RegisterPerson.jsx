import React, { useState } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, Shield, ArrowLeft, Image as ImageIcon } from 'lucide-react';
import { api } from '../services/api';

export default function RegisterPerson({ onBack, onRegistered }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [personCode, setPersonCode] = useState('P002');
  const [fullName, setFullName] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please upload a reference image.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('person_code', personCode);
    formData.append('full_name', fullName || personCode);
    formData.append('notes', notes);

    try {
      const res = await api.registerPerson(formData);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '780px', margin: '0 auto' }}>
      <button className="btn btn-secondary" onClick={onBack} style={{ marginBottom: '20px' }}>
        <ArrowLeft size={14} />
        <span>Back to Persons</span>
      </button>

      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '22px' }}>Single Reference Image Registration</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
            Primary Research Setting: Registers an authorized target using a single reference portrait.
            The AI engine extracts 512-D ArcFace biometrics and OSNet ReID features for cross-camera matching.
          </p>
        </div>

        {error && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#f87171',
            fontSize: '13.5px',
            marginBottom: '20px'
          }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {result ? (
          <div style={{
            padding: '24px',
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '12px',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#34d399', marginBottom: '14px' }}>
              <CheckCircle size={24} />
              <h3 style={{ fontSize: '18px', color: '#34d399' }}>Registration Successful!</h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '13.5px' }}>
              <div><strong>Person ID:</strong> <span className="camera-code-tag">{result.person_code}</span></div>
              <div><strong>Name:</strong> {result.full_name}</div>
              <div><strong>Face Biometric:</strong> {result.face_detected ? 'Extracted & Stored' : 'None'}</div>
              <div><strong>Face Quality Score:</strong> <span style={{ color: '#00f2fe', fontWeight: 700 }}>{int(result.face_quality_score * 100)}%</span></div>
              <div><strong>ReID Embedding:</strong> {result.reid_extracted ? '512-D Vector Built' : 'Pending'}</div>
              <div><strong>Status:</strong> <span className="status-pill status-online">ACTIVE</span></div>
            </div>

            <div style={{ marginTop: '20px' }}>
              <button
                className="btn btn-primary"
                onClick={() => onRegistered && onRegistered(result)}
              >
                View Movement Timeline
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              {/* Image Upload Area */}
              <div>
                <label className="form-label">Upload Reference Image</label>
                <div style={{
                  border: '2px dashed var(--border-subtle)',
                  borderRadius: '12px',
                  padding: '24px',
                  textAlign: 'center',
                  background: 'rgba(15, 23, 42, 0.4)',
                  cursor: 'pointer',
                  position: 'relative'
                }}>
                  <input
                    id="input-ref-image"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    style={{
                      position: 'absolute',
                      inset: 0,
                      opacity: 0,
                      cursor: 'pointer',
                      width: '100%',
                      height: '100%'
                    }}
                  />
                  {preview ? (
                    <div>
                      <img
                        src={preview}
                        alt="Reference Preview"
                        style={{ maxHeight: '200px', maxWidth: '100%', borderRadius: '8px', border: '1px solid var(--border-glow)' }}
                      />
                      <div style={{ fontSize: '12px', color: 'var(--accent-cyan)', marginTop: '8px' }}>
                        Click to change photo
                      </div>
                    </div>
                  ) : (
                    <div>
                      <UploadCloud size={40} color="#00f2fe" style={{ margin: '0 auto 12px auto' }} />
                      <div style={{ fontSize: '14px', fontWeight: 600 }}>Click or Drag Portrait Photo</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                        High-resolution JPG/PNG image
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Form Metadata */}
              <div>
                <div className="form-group">
                  <label className="form-label">Person Identifier Code</label>
                  <input
                    id="input-person-code"
                    type="text"
                    className="form-input"
                    required
                    value={personCode}
                    onChange={(e) => setPersonCode(e.target.value.toUpperCase())}
                    placeholder="P002"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Full Name / Internal Label</label>
                  <input
                    id="input-full-name"
                    type="text"
                    className="form-input"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. VIP Guest Sarah Jenkins"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Notes & Authorization Details</label>
                  <textarea
                    className="form-textarea"
                    rows={3}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Special authorization notes or suite assignment"
                  />
                </div>

                <button
                  id="btn-register-submit"
                  type="submit"
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '12px', marginTop: '10px' }}
                  disabled={loading}
                >
                  {loading ? 'Analyzing Biometrics & Registering...' : 'Register Person & Activate Tracking'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

function int(val) {
  return Math.round(val || 0);
}
