import React, { useState, useEffect } from 'react';
import { MapPin, Navigation, Eye, Activity, Shield, Users } from 'lucide-react';
import { api } from '../services/api';

export default function ResortMap({ onSelectCamera }) {
  const [mapData, setMapData] = useState({ nodes: [], edges: [] });
  const [selectedCam, setSelectedCam] = useState(null);
  const [loading, setLoading] = useState(true);

  // Active tracked targets on map
  const activePings = [
    { person_code: 'P001', camera_code: 'CAM-08', time: '10:42:17', status: 'VERIFIED' },
    { person_code: 'P001', camera_code: 'CAM-04', time: '09:34:10', status: 'PREVIOUS' },
  ];

  useEffect(() => {
    loadMap();
  }, []);

  const loadMap = async () => {
    try {
      const res = await api.getResortMapGraph();
      setMapData(res);
      if (res.nodes && res.nodes.length > 0) {
        setSelectedCam(res.nodes[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '22px' }}>2D Resort Topological Surveillance Map</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
            Interactive spatial layout of all 25 cameras, transit transition corridors, and live target position pings.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="status-pill status-online" style={{ padding: '6px 14px' }}>
            <span className="status-dot" />
            <span>Tracking P001 Live (Pool Area)</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px' }}>
        {/* Interactive Map Canvas */}
        <div className="glass-panel" style={{ padding: '16px', position: 'relative', overflow: 'hidden', minHeight: '620px' }}>
          <svg
            viewBox="0 0 1000 800"
            style={{ width: '100%', height: '100%', minHeight: '600px', background: '#070b16', borderRadius: '12px' }}
          >
            <defs>
              <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00f2fe" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0.15" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Resort Layout Visual Zones */}
            {/* North Entrance & Parking */}
            <rect x="180" y="30" width="640" height="120" rx="12" fill="#0d1424" stroke="rgba(255,255,255,0.05)" />
            <text x="200" y="60" fill="#64748b" fontSize="13" fontWeight="600" letterSpacing="1">NORTH GATE & MAIN PARKING</text>

            {/* Central Atrium & Reception */}
            <rect x="360" y="170" width="280" height="240" rx="12" fill="#0f192e" stroke="rgba(0, 242, 254, 0.15)" />
            <text x="380" y="200" fill="#38bdf8" fontSize="13" fontWeight="600" letterSpacing="1">CENTRAL LOBBY & RECEPTION</text>

            {/* Dining & East Wing */}
            <rect x="680" y="170" width="280" height="150" rx="12" fill="#0d1424" stroke="rgba(255,255,255,0.05)" />
            <text x="700" y="200" fill="#64748b" fontSize="13" fontWeight="600" letterSpacing="1">RESTAURANTS & SERVICE</text>

            {/* Swimming Pool & Beachfront (South East) */}
            <rect x="680" y="360" width="280" height="340" rx="12" fill="#0b172a" stroke="rgba(0, 242, 254, 0.2)" />
            <text x="700" y="390" fill="#00f2fe" fontSize="13" fontWeight="600" letterSpacing="1">POOL, SPA & BEACHFRONT</text>

            {/* Botanical Gardens (West) */}
            <rect x="40" y="170" width="280" height="420" rx="12" fill="#09151c" stroke="rgba(16, 185, 129, 0.15)" />
            <text x="60" y="200" fill="#34d399" fontSize="13" fontWeight="600" letterSpacing="1">BOTANICAL GARDENS & PROMENADE</text>

            {/* Guest Wings (South Central) */}
            <rect x="360" y="440" width="280" height="260" rx="12" fill="#0d1424" stroke="rgba(255,255,255,0.05)" />
            <text x="380" y="470" fill="#64748b" fontSize="13" fontWeight="600" letterSpacing="1">GUEST VILLAS & RESIDENCES</text>

            {/* Draw Directed Transition Edges */}
            {mapData.edges.map((edge, idx) => {
              const u = mapData.nodes.find(n => n.id === edge.from);
              const v = mapData.nodes.find(n => n.id === edge.to);
              if (!u || !v) return null;
              const x1 = u.x * 10;
              const y1 = u.y * 8;
              const x2 = v.x * 10;
              const y2 = v.y * 8;
              return (
                <line
                  key={`edge-${idx}`}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="url(#edgeGrad)"
                  strokeWidth="2"
                  strokeDasharray="4,4"
                />
              );
            })}

            {/* Draw Camera Nodes */}
            {mapData.nodes.map((cam) => {
              const cx = cam.x * 10;
              const cy = cam.y * 8;
              const isSelected = selectedCam && selectedCam.id === cam.id;
              const hasActivePing = activePings.find(p => p.camera_code === cam.code);

              return (
                <g
                  key={cam.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => setSelectedCam(cam)}
                >
                  {/* Ping Animation Ring if person detected */}
                  {hasActivePing && (
                    <circle
                      cx={cx}
                      cy={cy}
                      r="22"
                      fill="none"
                      stroke="#00f2fe"
                      strokeWidth="2"
                      opacity="0.8"
                    >
                      <animate attributeName="r" from="14" to="34" dur="1.8s" repeatCount="indefinite" />
                      <animate attributeName="opacity" from="1" to="0" dur="1.8s" repeatCount="indefinite" />
                    </circle>
                  )}

                  {/* Camera Marker Base */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={isSelected ? 14 : 11}
                    fill={hasActivePing ? '#00f2fe' : isSelected ? '#38bdf8' : '#1e293b'}
                    stroke={isSelected ? '#ffffff' : 'rgba(255,255,255,0.3)'}
                    strokeWidth="2"
                    filter={hasActivePing ? 'url(#glow)' : 'none'}
                  />

                  {/* Camera Code Label */}
                  <text
                    x={cx}
                    y={cy + 24}
                    textAnchor="middle"
                    fill={hasActivePing ? '#00f2fe' : '#e2e8f0'}
                    fontSize="11"
                    fontFamily="monospace"
                    fontWeight="700"
                  >
                    {cam.code}
                  </text>

                  {/* Person Ping Flag */}
                  {hasActivePing && (
                    <g transform={`translate(${cx + 12}, ${cy - 18})`}>
                      <rect width="64" height="20" rx="4" fill="#00f2fe" />
                      <text x="32" y="14" textAnchor="middle" fill="#070b16" fontSize="10" fontWeight="800">
                        {hasActivePing.person_code} NOW
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </svg>
        </div>

        {/* Selected Camera Sidebar Details */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          {selectedCam ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <span className="camera-code-tag" style={{ fontSize: '13px', padding: '3px 8px' }}>
                  {selectedCam.code}
                </span>
                <span className="status-pill status-online">
                  <span className="status-dot" />
                  ONLINE
                </span>
              </div>

              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '4px' }}>{selectedCam.name}</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
                {selectedCam.location}
              </p>

              <div style={{
                aspectRatio: '16/9',
                borderRadius: '8px',
                overflow: 'hidden',
                background: '#050a14',
                border: '1px solid var(--border-subtle)',
                marginBottom: '18px'
              }}>
                <img
                  src={`${api.getCameraSnapshotUrl(selectedCam.id)}?t=${Date.now()}`}
                  alt={selectedCam.code}
                  onError={(e) => {
                    e.target.src = `${api.getCameraSnapshotUrl(selectedCam.id)}?fallback=1&t=${Date.now()}`;
                  }}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12.5px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>AI Tracking:</span>
                  <strong style={{ color: '#34d399' }}>Active (YOLO+ByteTrack)</strong>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Map Coordinates:</span>
                  <span style={{ fontFamily: 'var(--font-mono)' }}>X: {selectedCam.x}, Y: {selectedCam.y}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Active Target:</span>
                  <strong style={{ color: selectedCam.code === 'CAM-08' ? '#00f2fe' : '#94a3b8' }}>
                    {selectedCam.code === 'CAM-08' ? 'VIP P001 (Match: 91%)' : 'None detected'}
                  </strong>
                </div>
              </div>

              <div style={{ marginTop: '24px' }}>
                <button
                  className="btn btn-primary"
                  style={{ width: '100%' }}
                  onClick={() => onSelectCamera && onSelectCamera(selectedCam.id)}
                >
                  <Eye size={15} />
                  <span>Open Full Camera Feed</span>
                </button>
              </div>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)' }}>Click a camera node on the resort map.</div>
          )}
        </div>
      </div>
    </div>
  );
}
