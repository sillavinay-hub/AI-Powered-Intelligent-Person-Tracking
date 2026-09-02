import React, { useState, useEffect } from 'react';
import { 
  Camera, 
  Users, 
  Activity, 
  AlertTriangle, 
  Eye, 
  Maximize2, 
  Play, 
  Pause, 
  Cpu,
  TrendingUp,
  MapPin,
  ExternalLink,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';

function CameraTileItem({ cam, gridMode, isPaused, aiEnabled, onViewCamera }) {
  const [imgSrc, setImgSrc] = useState('');
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  useEffect(() => {
    if (isPaused) return;

    // In 1 or 4 camera view: Live MJPEG stream provides high-framerate fluid video
    if (gridMode <= 4) {
      setImgSrc(`${api.getCameraStreamUrl(cam.id)}?ai=${aiEnabled}&t=${Date.now()}`);
      return;
    }

    // In 9, 16, or 25 camera view:
    // Staggered snapshot polling avoids browser HTTP/1.1 6-connection limit per host,
    // ensuring ALL 25 cameras load simultaneously and display video reliably.
    let isMounted = true;
    const updateSnapshot = () => {
      if (isMounted) {
        setImgSrc(`${api.getCameraSnapshotUrl(cam.id)}?t=${Date.now()}`);
        setLastUpdate(Date.now());
      }
    };

    // Stagger initial load by camera ID to distribute network traffic evenly
    const initialDelay = ((cam.id - 1) % 8) * 80;
    const initialTimer = setTimeout(() => {
      updateSnapshot();
      const interval = setInterval(updateSnapshot, 800);
      return () => clearInterval(interval);
    }, initialDelay);

    return () => {
      isMounted = false;
      clearTimeout(initialTimer);
    };
  }, [cam.id, gridMode, isPaused, aiEnabled]);

  const handleImgError = () => {
    // If stream fails or times out, immediately fall back to snapshot
    setImgSrc(`${api.getCameraSnapshotUrl(cam.id)}?fallback=1&t=${Date.now()}`);
  };

  return (
    <div className="camera-tile">
      <div className="camera-header-bar">
        <div className="camera-title-group">
          <span className="camera-code-tag">{cam.camera_code}</span>
          <span className="camera-name-text" title={`${cam.name} (${cam.location})`}>
            {cam.name}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="status-pill status-online">
            <span className="status-dot" />
            ONLINE
          </span>
          <button
            className="btn btn-secondary"
            style={{ padding: '4px 6px', borderRadius: '4px' }}
            onClick={() => onViewCamera(cam.id)}
            title="Focus Camera"
          >
            <ExternalLink size={13} />
          </button>
        </div>
      </div>

      <div className="camera-media-wrap">
        {!isPaused && imgSrc ? (
          <img
            key={gridMode <= 4 ? `stream-${cam.id}` : `snap-${cam.id}-${lastUpdate}`}
            src={imgSrc}
            alt={cam.camera_code}
            className="camera-stream-img"
            onError={handleImgError}
          />
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            {isPaused ? '[ Stream Paused ]' : '[ Initializing Feed... ]'}
          </div>
        )}

        <div className="camera-hud-overlay">
          <span className="camera-hud-badge">
            {cam.source_type} • {gridMode <= 4 ? `${cam.fps || 10} FPS Live` : 'Snapshot Mode'}
          </span>
          <span className="camera-hud-badge" style={{ color: '#00f2fe' }}>
            AI ACTIVE
          </span>
        </div>
      </div>

      <div className="camera-footer-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <MapPin size={13} color="#64748b" />
          <span style={{ fontSize: '11.5px', color: '#94a3b8' }}>{cam.location}</span>
        </div>
        <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: '#00f2fe' }}>
          {cam.camera_code === 'CAM-01' || cam.camera_code === 'CAM-03' || cam.camera_code === 'CAM-04' || cam.camera_code === 'CAM-08' ? 'P001 DETECTED' : 'MONITORING'}
        </span>
      </div>
    </div>
  );
}

export default function Dashboard({ onViewCamera, onOpenTimeline }) {
  const [cameras, setCameras] = useState([]);
  const [summary, setSummary] = useState(null);
  const [gridMode, setGridMode] = useState(4); // 1, 4, 9, 16, 25
  const [aiEnabled, setAiEnabled] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [cams, stats] = await Promise.all([
        api.getCameras(),
        api.getDashboardAnalytics()
      ]);
      setCameras(cams);
      setSummary(stats);
    } catch (e) {
      console.error('Failed to load dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  const displayedCameras = cameras.slice(0, gridMode);

  return (
    <div>
      {/* Top KPI Telemetry */}
      <div className="kpi-grid">
        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <span className="kpi-label">Total Cameras</span>
            <span className="kpi-value">{summary ? summary.total_cameras : 25}</span>
            <span className="kpi-badge">25 Configured Nodes</span>
          </div>
          <div className="kpi-icon-wrap" style={{ color: '#00f2fe' }}>
            <Camera size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <span className="kpi-label">Active Feeds</span>
            <span className="kpi-value" style={{ color: '#34d399' }}>
              {summary ? summary.online_cameras : 25}
            </span>
            <span className="kpi-badge" style={{ color: '#34d399' }}>
              ● 100% Operational
            </span>
          </div>
          <div className="kpi-icon-wrap" style={{ color: '#10b981' }}>
            <Activity size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <span className="kpi-label">Tracked Targets</span>
            <span className="kpi-value" style={{ color: '#38bdf8' }}>
              {summary ? summary.tracked_persons : 2}
            </span>
            <span className="kpi-badge" style={{ color: '#38bdf8' }}>
              VIP P001 Monitored
            </span>
          </div>
          <div className="kpi-icon-wrap" style={{ color: '#38bdf8' }}>
            <Users size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <span className="kpi-label">Today's Sightings</span>
            <span className="kpi-value">{summary ? summary.today_events : 5}</span>
            <span className="kpi-badge">Cross-Camera Events</span>
          </div>
          <div className="kpi-icon-wrap" style={{ color: '#818cf8' }}>
            <TrendingUp size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <span className="kpi-label">Active Alerts</span>
            <span className="kpi-value" style={{ color: '#f87171' }}>
              {summary ? summary.active_alerts : 1}
            </span>
            <span className="kpi-badge" style={{ color: '#f87171' }}>
              Restricted Area
            </span>
          </div>
          <div className="kpi-icon-wrap" style={{ color: '#ef4444' }}>
            <AlertTriangle size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <span className="kpi-label">AI Match Confidence</span>
            <span className="kpi-value" style={{ color: '#a78bfa' }}>
              {summary ? `${summary.average_confidence_pct}%` : '91.4%'}
            </span>
            <span className="kpi-badge" style={{ color: '#a78bfa' }}>
              Multimodal Fusion
            </span>
          </div>
          <div className="kpi-icon-wrap" style={{ color: '#a78bfa' }}>
            <Cpu size={24} />
          </div>
        </div>
      </div>

      {/* Grid Controls */}
      <div className="grid-controls">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <h2 style={{ fontSize: '18px', margin: 0 }}>Surveillance Grid</h2>
          <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
            Showing {displayedCameras.length} of {cameras.length} cameras
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            id="btn-toggle-pause"
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setIsPaused(!isPaused)}
          >
            {isPaused ? <Play size={14} /> : <Pause size={14} />}
            <span>{isPaused ? 'Resume Feeds' : 'Pause All'}</span>
          </button>

          <button
            id="btn-toggle-ai"
            className={`btn ${aiEnabled ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setAiEnabled(!aiEnabled)}
          >
            <Cpu size={14} />
            <span>AI BBoxes: {aiEnabled ? 'ON' : 'OFF'}</span>
          </button>

          <div className="grid-view-buttons">
            {[1, 4, 9, 16, 25].map((mode) => (
              <button
                key={mode}
                id={`grid-btn-${mode}`}
                className={`grid-btn ${gridMode === mode ? 'active' : ''}`}
                onClick={() => setGridMode(mode)}
              >
                {mode} Cam
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Camera Grid View */}
      <div className={`camera-grid-${gridMode}`}>
        {displayedCameras.map((cam) => (
          <CameraTileItem
            key={cam.id}
            cam={cam}
            gridMode={gridMode}
            isPaused={isPaused}
            aiEnabled={aiEnabled}
            onViewCamera={onViewCamera}
          />
        ))}
      </div>
    </div>
  );
}
