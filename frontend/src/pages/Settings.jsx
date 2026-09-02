import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Sliders, Save, RefreshCw, CheckCircle, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export default function Settings({ currentUser }) {
  const [weights, setWeights] = useState({
    w_face: 0.40,
    w_reid: 0.35,
    w_temp: 0.15,
    w_cam: 0.10
  });
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWeights();
  }, []);

  const loadWeights = async () => {
    try {
      const res = await api.getFusionWeights();
      setWeights({
        w_face: res.w_face,
        w_reid: res.w_reid,
        w_temp: res.w_temp,
        w_cam: res.w_cam
      });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleWeightChange = (key, val) => {
    setWeights({ ...weights, [key]: parseFloat(val) });
    setSaved(false);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await api.updateFusionWeights(weights);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert(err.message);
    }
  };

  const sumWeights = weights.w_face + weights.w_reid + weights.w_temp + weights.w_cam;

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '22px' }}>System Configuration & Fusion Parameters</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
          Tune multimodal weighting coefficients and privacy controls for cross-camera identity association.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '32px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '17px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="#00f2fe" />
            <span>Multimodal Fusion Equation Weights</span>
          </h3>

          <div style={{
            fontSize: '12px',
            fontFamily: 'var(--font-mono)',
            padding: '4px 10px',
            borderRadius: '6px',
            background: Math.abs(sumWeights - 1.0) < 0.02 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
            color: Math.abs(sumWeights - 1.0) < 0.02 ? '#34d399' : '#fbbf24'
          }}>
            Sum: {sumWeights.toFixed(2)} (Auto-normalized)
          </div>
        </div>

        <form onSubmit={handleSave}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* W_FACE */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13.5px', marginBottom: '6px' }}>
                <span style={{ fontWeight: 600 }}>W_FACE (ArcFace Facial Biometrics)</span>
                <strong style={{ color: '#00f2fe', fontFamily: 'var(--font-mono)' }}>{weights.w_face.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={weights.w_face}
                onChange={(e) => handleWeightChange('w_face', e.target.value)}
                style={{ width: '100%', accentColor: '#00f2fe' }}
              />
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>High discriminatory power when facial angle is frontal; degraded by occlusion.</div>
            </div>

            {/* W_REID */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13.5px', marginBottom: '6px' }}>
                <span style={{ fontWeight: 600 }}>W_REID (OSNet Whole-Body Appearance)</span>
                <strong style={{ color: '#6366f1', fontFamily: 'var(--font-mono)' }}>{weights.w_reid.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={weights.w_reid}
                onChange={(e) => handleWeightChange('w_reid', e.target.value)}
                style={{ width: '100%', accentColor: '#6366f1' }}
              />
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Robust against turned-away targets and partial occlusions.</div>
            </div>

            {/* W_TEMPORAL */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13.5px', marginBottom: '6px' }}>
                <span style={{ fontWeight: 600 }}>W_TEMPORAL (Transit Kinematics Consistency)</span>
                <strong style={{ color: '#10b981', fontFamily: 'var(--font-mono)' }}>{weights.w_temp.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={weights.w_temp}
                onChange={(e) => handleWeightChange('w_temp', e.target.value)}
                style={{ width: '100%', accentColor: '#10b981' }}
              />
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Penalizes physically impossible velocities and anomalous teleports.</div>
            </div>

            {/* W_CAMERA */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13.5px', marginBottom: '6px' }}>
                <span style={{ fontWeight: 600 }}>W_CAMERA (Resort Topological Transition Prior)</span>
                <strong style={{ color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>{weights.w_cam.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={weights.w_cam}
                onChange={(e) => handleWeightChange('w_cam', e.target.value)}
                style={{ width: '100%', accentColor: '#f59e0b' }}
              />
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Probabilistic adjacency weighting based on connected corridors and walkways.</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '28px', paddingTop: '20px', borderTop: '1px solid var(--border-subtle)' }}>
            {saved ? (
              <span style={{ color: '#34d399', fontSize: '13.5px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle size={16} /> Parameters saved and applied to live pipeline!
              </span>
            ) : <span />}

            <button type="submit" className="btn btn-primary">
              <Save size={15} />
              <span>Apply Parameters</span>
            </button>
          </div>
        </form>
      </div>

      {/* Privacy and Data Retention Settings */}
      <div className="glass-panel" style={{ padding: '28px' }}>
        <h3 style={{ fontSize: '17px', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <ShieldCheck size={18} color="#10b981" />
          <span>Biometric Privacy & Data Retention</span>
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', fontSize: '13px' }}>
          <div style={{ padding: '14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
            <div style={{ fontWeight: 600, marginBottom: '4px' }}>Data Retention Policy</div>
            <div style={{ color: 'var(--text-muted)' }}>Surveillance detections and transit timestamps purged automatically after 30 days.</div>
          </div>

          <div style={{ padding: '14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
            <div style={{ fontWeight: 600, marginBottom: '4px' }}>Biometric Protection</div>
            <div style={{ color: 'var(--text-muted)' }}>Raw 512-D float vectors remain isolated within database; never transmitted to browser clients.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
