import React, { useState, useEffect } from 'react';
import { FlaskConical, Play, CheckCircle2, TrendingUp, BarChart2, Award, Zap } from 'lucide-react';
import { api } from '../services/api';

export default function Experiments() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [sampleCount, setSampleCount] = useState(80);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    setLoading(true);
    try {
      const res = await api.getExperimentResults();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunBenchmark = async () => {
    setRunning(true);
    try {
      const res = await api.runExperimentBenchmark(sampleCount);
      setData(res);
    } catch (e) {
      alert(e.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="status-pill status-online" style={{ background: 'rgba(0, 242, 254, 0.1)', color: '#00f2fe', borderColor: 'rgba(0, 242, 254, 0.3)' }}>
              RESEARCH CONTRIBUTION MODULE
            </span>
          </div>
          <h2 style={{ fontSize: '22px', marginTop: '6px' }}>Multimodal Identity Association Benchmark</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
            Comparative ablation study evaluating Face Only vs ReID Only vs Multimodal Fusion across 25 resort cameras.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
            <span>Test Sequences:</span>
            <select
              className="form-select"
              style={{ width: '100px', padding: '6px 10px', fontSize: '12.5px' }}
              value={sampleCount}
              onChange={(e) => setSampleCount(parseInt(e.target.value))}
            >
              <option value="50">50 runs</option>
              <option value="80">80 runs</option>
              <option value="120">120 runs</option>
            </select>
          </div>

          <button
            id="btn-run-benchmark"
            className="btn btn-primary"
            onClick={handleRunBenchmark}
            disabled={running}
          >
            <Play size={15} />
            <span>{running ? 'Benchmarking Models...' : 'Run Benchmark Evaluation'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px' }}>Loading empirical experiment results...</div>
      ) : data ? (
        <div>
          {/* Research Conclusion Highlight Callout */}
          <div className="glass-panel glass-panel-accent" style={{ padding: '20px 24px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(0, 242, 254, 0.2)', color: '#00f2fe' }}>
                <Award size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', color: '#00f2fe', marginBottom: '4px' }}>Empirical Research Findings</h3>
                <p style={{ fontSize: '13.5px', color: '#e2e8f0', lineHeight: 1.6 }}>
                  {data.research_conclusion}
                </p>
              </div>
            </div>
          </div>

          {/* Quantitative Performance Metrics Table */}
          <div className="glass-panel" style={{ padding: '24px', overflowX: 'auto', marginBottom: '24px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Quantitative Ablation Results</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Experiment Model</th>
                  <th>Accuracy</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>ReID Rank-1</th>
                  <th>mAP</th>
                  <th>IDF1</th>
                  <th>MOTA</th>
                  <th>ID Switches</th>
                  <th>Latency</th>
                </tr>
              </thead>
              <tbody>
                {data.experiments.map((exp, idx) => {
                  const isTop = idx === data.experiments.length - 1;
                  return (
                    <tr key={exp.experiment_id} style={{ background: isTop ? 'rgba(0, 242, 254, 0.04)' : 'transparent' }}>
                      <td>
                        <div style={{ fontWeight: 700, color: isTop ? '#00f2fe' : '#f8fafc' }}>
                          {exp.name}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{exp.description}</div>
                      </td>
                      <td style={{ fontWeight: 700, color: isTop ? '#34d399' : 'inherit' }}>
                        {exp.accuracy}%
                      </td>
                      <td>{exp.precision}%</td>
                      <td>{exp.recall}%</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{exp.reid_rank1}%</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{exp.reid_map}%</td>
                      <td style={{ fontWeight: 700, color: isTop ? '#00f2fe' : 'inherit' }}>
                        {exp.idf1}%
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{exp.mota}%</td>
                      <td>
                        <span style={{
                          color: exp.id_switches === 0 ? '#34d399' : '#f87171',
                          fontWeight: 700,
                          fontFamily: 'var(--font-mono)'
                        }}>
                          {exp.id_switches}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                        {exp.latency_ms} ms
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Research Metric Comparison Bars */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '15px', marginBottom: '16px' }}>IDF1 Tracking Identity Continuity Score (%)</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {data.experiments.map((exp, i) => (
                  <div key={i}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                      <span>{exp.name}</span>
                      <strong style={{ color: '#00f2fe' }}>{exp.idf1}%</strong>
                    </div>
                    <div style={{ height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{
                        width: `${exp.idf1}%`,
                        height: '100%',
                        background: i === data.experiments.length - 1 ? 'linear-gradient(90deg, #00f2fe, #34d399)' : '#475569'
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '15px', marginBottom: '16px' }}>Overall Cross-Camera Association Accuracy (%)</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {data.experiments.map((exp, i) => (
                  <div key={i}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                      <span>{exp.name}</span>
                      <strong style={{ color: '#34d399' }}>{exp.accuracy}%</strong>
                    </div>
                    <div style={{ height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{
                        width: `${exp.accuracy}%`,
                        height: '100%',
                        background: i === data.experiments.length - 1 ? 'linear-gradient(90deg, #10b981, #00f2fe)' : '#475569'
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
