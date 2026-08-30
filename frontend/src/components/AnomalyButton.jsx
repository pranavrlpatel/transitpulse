/**
 * AnomalyButton.jsx — Toggle button to inject / clear a demo disruption.
 */

import { useState, useEffect } from 'react';
import { injectAnomaly, clearAnomalies, fetchStops } from '../api';

export default function AnomalyButton() {
  const [active, setActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stops, setStops] = useState([]);
  const [selectedStop, setSelectedStop] = useState('20922');
  const [selectedType, setSelectedType] = useState('breakdown');

  useEffect(() => {
    fetchStops()
      .then((data) => setStops(data))
      .catch(console.error);
  }, []);

  const handleToggle = async () => {
    setLoading(true);
    try {
      if (active) {
        await clearAnomalies();
        setActive(false);
      } else {
        await injectAnomaly(selectedStop, 0.8, selectedType);
        setActive(true);
      }
    } catch (err) {
      console.error('Anomaly toggle failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <div className="card-title">
        <span className="icon">&#9888;</span> Disruption Simulator
      </div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: '1.4' }}>
        Test how the system reacts to unexpected events. Injecting a disruption simulates a major delay at a specific station, dynamically rippling through the network to update crowding predictions and route recommendations in real-time. (Re-click "Find Best Route" after injecting to see new recommendations).
      </p>
      <div className="anomaly-section">
        <div className="anomaly-controls">
          <select
            value={selectedStop}
            onChange={(e) => setSelectedStop(e.target.value)}
            disabled={active}
            id="anomaly-stop-select"
          >
            {stops.map((s) => (
              <option key={s.stop_id} value={s.stop_id}>
                {s.name} ({s.stop_id})
              </option>
            ))}
          </select>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            disabled={active}
            id="anomaly-type-select"
          >
            <option value="breakdown">Breakdown</option>
            <option value="rainy">Rainy</option>
            <option value="snowy">Snowy</option>
            <option value="stormy">Stormy</option>
            <option value="protest">Protest</option>
          </select>
          <button
            className={`btn-anomaly ${active ? 'clear' : 'inject'}`}
            onClick={handleToggle}
            disabled={loading}
            id="anomaly-toggle-button"
          >
            {loading
              ? '...'
              : active
                ? 'Clear Disruption'
                : 'Inject Disruption'}
          </button>
        </div>

        <div className={`anomaly-status ${active ? 'active' : 'inactive'}`}>
          {active ? (
            <>
              <span className="pulse-dot" />
              {selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} active at {stops.find(s => s.stop_id === selectedStop)?.name || selectedStop}
              &nbsp;(will auto-expire)
            </>
          ) : (
            'No active disruptions'
          )}
        </div>
      </div>
    </div>
  );
}
