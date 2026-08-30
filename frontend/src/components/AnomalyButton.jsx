/**
 * AnomalyButton.jsx — Toggle button to inject / clear a demo disruption.
 */

import { useState, useEffect } from 'react';
import { injectAnomaly, clearAnomalies, fetchStops, fetchWeather } from '../api';

export default function AnomalyButton({ onAnomalyChanged }) {
  const [active, setActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stops, setStops] = useState([]);
  const [selectedStop, setSelectedStop] = useState('36720');
  const [selectedType, setSelectedType] = useState('breakdown');
  const [severity, setSeverity] = useState(0.8);
  const [isLiveMode, setIsLiveMode] = useState(true);
  const [weatherData, setWeatherData] = useState(null);

  useEffect(() => {
    fetchStops()
      .then((data) => setStops(data))
      .catch(console.error);
      
    // Poll weather every 30 seconds if in live mode
    const getW = () => fetchWeather().then(setWeatherData).catch(console.error);
    getW();
    const inv = setInterval(getW, 30000);
    return () => clearInterval(inv);
  }, []);

  const handleToggle = async () => {
    setLoading(true);
    try {
      if (active) {
        await clearAnomalies();
        setActive(false);
      } else {
        await injectAnomaly(selectedStop, severity, selectedType);
        setActive(true);
      }
      if (onAnomalyChanged) {
        onAnomalyChanged();
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
      
      <div style={{ display: 'flex', gap: '8px', marginBottom: '1.5rem', background: 'var(--bg-primary)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
        <button 
          style={{ flex: 1, padding: '0.5rem', borderRadius: 'var(--radius-sm)', border: 'none', background: isLiveMode ? 'var(--bg-glass-hover)' : 'transparent', color: isLiveMode ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: isLiveMode ? '600' : '400', cursor: 'pointer', transition: 'all 0.2s' }}
          onClick={() => setIsLiveMode(true)}
        >
          Live Weather
        </button>
        <button 
          style={{ flex: 1, padding: '0.5rem', borderRadius: 'var(--radius-sm)', border: 'none', background: !isLiveMode ? 'var(--bg-glass-hover)' : 'transparent', color: !isLiveMode ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: !isLiveMode ? '600' : '400', cursor: 'pointer', transition: 'all 0.2s' }}
          onClick={() => setIsLiveMode(false)}
        >
          Manual Setup
        </button>
      </div>

      <div className="anomaly-section" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {isLiveMode ? (
          <div style={{ padding: '1rem', background: 'rgba(56, 189, 248, 0.1)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div className="pulse-dot" style={{ background: 'var(--accent-blue)', boxShadow: '0 0 8px var(--accent-blue)' }}></div>
              <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--accent-blue)' }}>Syncing with Open-Meteo API</span>
            </div>
            {weatherData ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                <div><strong>Temp:</strong> {weatherData.raw_data?.temperature_2m}°C</div>
                <div><strong>Rain:</strong> {weatherData.precipitation_mm}mm</div>
                <div><strong>Status:</strong> {weatherData.is_raining ? 'Raining' : 'Clear'}</div>
                <div><strong>Wind:</strong> {weatherData.raw_data?.wind_speed_10m} km/h</div>
              </div>
            ) : (
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Loading live data...</div>
            )}
            <div style={{ marginTop: '15px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Predictions are currently adapting in real-time based on actual weather conditions in Bangalore.
            </div>
          </div>
        ) : (
          <>
            <div className="anomaly-controls" style={{ flexWrap: 'wrap' }}>
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
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '5px' }}>
              <label htmlFor="severity-slider" style={{ fontSize: '0.85rem', fontWeight: '600' }}>Severity:</label>
              <input 
                id="severity-slider"
                type="range" 
                min="0.1" 
                max="1.0" 
                step="0.1" 
                value={severity} 
                onChange={(e) => setSeverity(parseFloat(e.target.value))}
                disabled={active}
                style={{ flex: 1, accentColor: 'var(--brand-primary)' }}
              />
              <span style={{ fontSize: '0.85rem', minWidth: '35px' }}>{Math.round(severity * 100)}%</span>
            </div>

            <div className={`anomaly-status ${active ? 'active' : 'inactive'}`}>
              {active ? (
                <>
                  <span className="pulse-dot" />
                  {selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} ({Math.round(severity * 100)}% severity) active at {stops.find(s => s.stop_id === selectedStop)?.name || selectedStop}
                </>
              ) : (
                'No active disruptions'
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
