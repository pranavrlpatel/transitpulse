/**
 * StopCrowdingList.jsx — Per-stop crowding list with auto-polling.
 *
 * Polls GET /route-crowding every 3 seconds so it reflects
 * injected anomalies without manual refresh.
 */

import { useState, useEffect, useRef } from 'react';
import { fetchRouteCrowding, fetchRoutes } from '../api';

const TIER_COLORS = {
  light:    'var(--tier-light)',
  moderate: 'var(--tier-moderate)',
  heavy:    'var(--tier-heavy)',
  severe:   'var(--tier-severe)',
};

export default function StopCrowdingList({ selectedRoute, onRouteChange }) {
  const [routes, setRoutes] = useState([]);
  const [crowdingData, setCrowdingData] = useState([]);
  const intervalRef = useRef(null);

  // Load available routes once
  useEffect(() => {
    fetchRoutes()
      .then((data) => {
        setRoutes(data);
        if (!selectedRoute && data.length > 0) {
          onRouteChange(data[0].route_id);
        }
      })
      .catch(console.error);
  }, []);

  // Poll crowding data for selected route
  useEffect(() => {
    if (!selectedRoute) return;

    const poll = () => {
      fetchRouteCrowding(selectedRoute)
        .then(setCrowdingData)
        .catch(console.error);
    };

    poll(); // immediate first call
    intervalRef.current = setInterval(poll, 3000);

    return () => clearInterval(intervalRef.current);
  }, [selectedRoute]);

  return (
    <div className="glass-card">
      <div className="card-title">
        <span className="icon">&#128202;</span> Stop Crowding
      </div>

      {/* Route selector chips */}
      <div className="route-selector">
        {routes.map((r) => (
          <button
            key={r.route_id}
            className={`route-chip ${selectedRoute === r.route_id ? 'active' : ''}`}
            onClick={() => onRouteChange(r.route_id)}
          >
            {r.route_id}
          </button>
        ))}
      </div>

      {/* Crowding rows */}
      <div className="crowding-list">
        {crowdingData.length === 0 && (
          <div className="loading-shimmer" />
        )}
        {crowdingData.map((stop) => {
          const pct = Math.round(stop.crowding * 100);
          const barWidth = Math.min(pct, 100);
          const color = TIER_COLORS[stop.tier] || TIER_COLORS.light;

          return (
            <div key={stop.stop_id} className="crowding-row">
              <div>
                <div className="stop-name">{stop.name}</div>
                <div className="stop-id">{stop.stop_id}</div>
                <div className="crowding-bar-bg">
                  <div
                    className="crowding-bar-fill"
                    style={{
                      width: `${barWidth}%`,
                      background: color,
                    }}
                  />
                </div>
              </div>
              <div className="crowding-pct" style={{ color }}>
                {pct}%
              </div>
              <div className="delay-val">{stop.delay.toFixed(1)}m</div>
              <span className={`tier-badge ${stop.tier}`}>{stop.tier}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
