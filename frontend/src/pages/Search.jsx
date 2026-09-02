import React, { useState } from 'react';
import { Search as SearchIcon, MessageSquare, MapPin, Clock, Filter, Sparkles, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function Search({ onSelectPerson }) {
  const [activeMode, setActiveMode] = useState('nlp'); // 'nlp' or 'structured'
  const [nlQuery, setNlQuery] = useState('Where was P001 last seen?');
  const [nlpResult, setNlpResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Structured query state
  const [structQuery, setStructQuery] = useState({
    person_code: 'P001',
    camera_code: '',
    min_confidence: 0.6
  });
  const [structResult, setStructResult] = useState(null);

  const sampleQueries = [
    'Where was P001 last seen?',
    'Where was P001 detected today?',
    'Show P001 movement history between 9 AM and 11 AM'
  ];

  const handleNlpSearch = async (queryText) => {
    const q = queryText || nlQuery;
    setLoading(true);
    try {
      const res = await api.searchNlp(q);
      setNlpResult(res);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStructuredSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.searchStructured(structQuery);
      setStructResult(res);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '22px' }}>Multi-Camera Person Search Console</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>
          Query sightings across 25 cameras using structured parametric filters or Controlled Natural Language interpretation.
        </p>
      </div>

      {/* Mode Switcher */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        <button
          className={`btn ${activeMode === 'nlp' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveMode('nlp')}
        >
          <Sparkles size={15} />
          <span>Natural Language Search</span>
        </button>

        <button
          className={`btn ${activeMode === 'structured' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveMode('structured')}
        >
          <Filter size={15} />
          <span>Structured Parameter Filter</span>
        </button>
      </div>

      {activeMode === 'nlp' ? (
        /* Natural Language Search Console */
        <div>
          <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <MessageSquare size={14} color="#00f2fe" />
              <span>Ask a natural language question about person movements</span>
            </label>

            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
              <input
                id="input-nlp-query"
                type="text"
                className="form-input"
                style={{ fontSize: '15px', padding: '12px 18px' }}
                value={nlQuery}
                onChange={(e) => setNlQuery(e.target.value)}
                placeholder="e.g. Where was P001 last seen?"
                onKeyDown={(e) => e.key === 'Enter' && handleNlpSearch()}
              />
              <button
                id="btn-nlp-search-submit"
                className="btn btn-primary"
                style={{ padding: '0 24px' }}
                onClick={() => handleNlpSearch()}
                disabled={loading}
              >
                <SearchIcon size={16} />
                <span>Search</span>
              </button>
            </div>

            {/* Quick Sample Queries */}
            <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Try example queries:</span>
              {sampleQueries.map((sq, i) => (
                <button
                  key={i}
                  type="button"
                  style={{
                    background: 'rgba(255,255,255,0.04)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '12px',
                    color: '#38bdf8',
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    setNlQuery(sq);
                    handleNlpSearch(sq);
                  }}
                >
                  "{sq}"
                </button>
              ))}
            </div>
          </div>

          {/* NLP Results Display */}
          {nlpResult && (
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '12px 16px',
                background: 'rgba(0, 242, 254, 0.08)',
                border: '1px solid var(--border-glow)',
                borderRadius: '8px',
                marginBottom: '20px'
              }}>
                <CheckCircle2 size={20} color="#00f2fe" />
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Interpreted Intent: {nlpResult.interpreted_intent}
                  </div>
                  <div style={{ fontSize: '14.5px', fontWeight: 600, color: '#f8fafc', marginTop: '2px' }}>
                    {nlpResult.summary}
                  </div>
                </div>
              </div>

              <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
                Parsed Detection Records ({nlpResult.results.length})
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {nlpResult.results.map((r, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'rgba(255,255,255,0.02)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span className="camera-code-tag">{r.camera_code}</span>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '14px' }}>{r.camera_name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{r.location}</div>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: '#00f2fe' }}>
                        {r.entry_time ? new Date(r.entry_time).toLocaleTimeString() : ''}
                      </div>
                      <div style={{ fontSize: '11px', color: '#34d399' }}>
                        Match Confidence: {Math.round((r.confidence || 0.9) * 100)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Structured Search Console */
        <div>
          <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
            <form onSubmit={handleStructuredSearch}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Person Code</label>
                  <input
                    type="text"
                    className="form-input"
                    value={structQuery.person_code}
                    onChange={(e) => setStructQuery({ ...structQuery, person_code: e.target.value })}
                    placeholder="P001"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Camera Code</label>
                  <input
                    type="text"
                    className="form-input"
                    value={structQuery.camera_code}
                    onChange={(e) => setStructQuery({ ...structQuery, camera_code: e.target.value })}
                    placeholder="e.g. CAM-08 (optional)"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Minimum Match Confidence</label>
                  <select
                    className="form-select"
                    value={structQuery.min_confidence}
                    onChange={(e) => setStructQuery({ ...structQuery, min_confidence: parseFloat(e.target.value) })}
                  >
                    <option value="0.5">50% or higher</option>
                    <option value="0.65">65% or higher (Standard)</option>
                    <option value="0.8">80% or higher (Strict)</option>
                  </select>
                </div>
              </div>

              <div style={{ textAlign: 'right', marginTop: '10px' }}>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  <SearchIcon size={15} />
                  <span>Execute Structured Query</span>
                </button>
              </div>
            </form>
          </div>

          {structResult && (
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h4 style={{ fontSize: '15px', marginBottom: '14px' }}>
                Query Results: {structResult.total_detections} matching detections found
              </h4>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Camera</th>
                    <th>Location</th>
                    <th>Local Track</th>
                    <th>Timestamp</th>
                    <th>Final Score</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {structResult.records.map((r) => (
                    <tr key={r.id}>
                      <td><span className="camera-code-tag">{r.camera_code}</span></td>
                      <td>{r.location}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>Track {r.local_track_id}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                        {new Date(r.timestamp).toLocaleTimeString()}
                      </td>
                      <td style={{ fontWeight: 700, color: '#00f2fe' }}>
                        {Math.round(r.scores.final * 100)}%
                      </td>
                      <td>
                        <span className="status-pill status-online">MATCHED</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
