/**
 * RouteMap.jsx — Schematic stop visualization.
 *
 * Renders stops as a horizontal sequence of circles connected by lines,
 * colored by current crowding tier. Reuses the same polled data as
 * StopCrowdingList.
 */

import { useState, useEffect, useRef } from 'react';
import { fetchRouteCrowding } from '../api';

const TIER_COLORS = {
  light:    'var(--tier-light)',
  moderate: 'var(--tier-moderate)',
  heavy:    'var(--tier-heavy)',
  severe:   'var(--tier-severe)',
};

export default function RouteMap({ routeId }) {
  const [stops, setStops] = useState([]);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!routeId) return;

    const poll = () => {
      fetchRouteCrowding(routeId)
        .then(setStops)
        .catch(console.error);
    };

    poll();
    intervalRef.current = setInterval(poll, 3000);
    return () => clearInterval(intervalRef.current);
  }, [routeId]);

  if (!routeId || stops.length === 0) {
    return (
      <div className="glass-card">
        <div className="card-title">
          <span className="icon">&#128739;</span> Route Map
        </div>
        <div className="empty-state">Select a route to see the map</div>
      </div>
    );
  }

  return (
    <div className="glass-card">
      <div className="card-title">
        <span className="icon">&#128739;</span> Route Map &mdash; {routeId}
      </div>
      <div className="route-map">
        <div className="route-map-track" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px 0' }}>
          {stops.map((stop, i) => (
            <div key={stop.stop_id} style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
              <div className="route-map-stop">
                <div
                  className={`node ${stop.tier}`}
                  title={`${stop.name}: ${Math.round(stop.crowding * 100)}% (${stop.tier})`}
                />
                <div className="stop-label">{stop.name}</div>
              </div>
              {i < stops.length - 1 && (
                <div
                  className="route-map-connector"
                  style={{
                    background: TIER_COLORS[stop.tier] || 'var(--border-subtle)',
                    opacity: 0.5,
                    width: '30px', // shorter connector since we are wrapping
                  }}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
