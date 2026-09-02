import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, ShieldAlert, Cpu, Activity, Clock } from 'lucide-react';
import { api } from '../services/api';

export default function Analytics() {
  const [charts, setCharts] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const [cData, sData] = await Promise.all([
        api.getChartsAnalytics(),
        api.getDashboardAnalytics()
      ]);
      setCharts(cData);
      setSummary(sData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !charts) {
    return <div style={{ textAlign: 'center', padding: '60px' }}>Loading analytics telemetry...</div>;
  }

  const maxHourly = Math.max(...charts.hourly_detections.map(h => h.count), 1);
  const maxBusiest = Math.max(...charts.busiest_cameras.map(b => b.detections), 1);

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '22px' }}>Surveillance Network Analytics & Flow Patterns</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
          Real-time metrics on person volume, camera density, detection confidence distributions, and security alerts.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
        {/* Hourly Detections Histogram */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={18} color="#00f2fe" />
            <span>Detection Volume by Hour of Day</span>
          </h3>

          <div style={{ display: 'flex', alignItems: 'flex-end', height: '180px', gap: '8px', paddingBottom: '24px' }}>
            {charts.hourly_detections.map((h, i) => {
              const heightPct = Math.round((h.count / maxHourly) * 100);
              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                  <div
                    style={{
                      width: '100%',
                      height: `${heightPct}%`,
                      background: 'linear-gradient(180deg, #00f2fe 0%, #3b82f6 100%)',
                      borderRadius: '4px 4px 0 0',
                      transition: 'height 0.4s ease'
                    }}
                    title={`${h.hour}: ${h.count} detections`}
                  />
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '6px', whiteSpace: 'nowrap' }}>
                    {h.hour.split(':')[0]}h
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Busiest Resort Cameras */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} color="#10b981" />
            <span>Highest Traffic Camera Locations</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {charts.busiest_cameras.map((b, i) => {
              const pct = Math.round((b.detections / maxBusiest) * 100);
              return (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                    <span>
                      <strong style={{ color: '#00f2fe' }}>{b.camera_code}</strong> {b.name}
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{b.detections} hits</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #34d399)' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={18} color="#a78bfa" />
            <span>Identity Matching Confidence Distribution</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {charts.confidence_distribution.map((c, i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Confidence Range {c.range}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: '#a78bfa' }}>{c.count} samples</span>
                </div>
                <div style={{ height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${(c.count / 115) * 100}%`, height: '100%', background: 'linear-gradient(90deg, #818cf8, #c084fc)' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Categories */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={18} color="#ef4444" />
            <span>Security Anomaly Breakdown</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {charts.alert_distribution.map((a, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: a.color }} />
                  <span style={{ fontSize: '13px', fontWeight: 600 }}>{a.type}</span>
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 700, color: a.color }}>
                  {a.count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
