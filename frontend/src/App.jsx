/**
 * App.jsx — Main application layout.
 *
 * Holds top-level state (selected route, recommendation result).
 * Lays out TripSearch, ComparisonCard, RouteMap, StopCrowdingList,
 * and AnomalyButton on a single-page dashboard.
 */

import { useState } from 'react';
import TripSearch from './components/TripSearch';
import ComparisonCard from './components/ComparisonCard';
import StopCrowdingList from './components/StopCrowdingList';
import AnomalyButton from './components/AnomalyButton';
import RouteMap from './components/RouteMap';

export default function App() {
  const [selectedRoute, setSelectedRoute] = useState('244-C VSD-0');
  const [recommendation, setRecommendation] = useState(null);

  const handleResult = (result) => {
    setRecommendation(result);
    // If the recommended option has a route, switch the map/crowding view to it
    if (result?.options?.length > 0) {
      const best = result.options[0];
      const routeId = best.route || best.first_route;
      if (routeId) setSelectedRoute(routeId);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>TransitPulse</h1>
        <p className="subtitle">
          Real-time crowding prediction &amp; smart route recommendations
        </p>
      </header>

      <div className="dashboard-grid">
        {/* Left panel: search + anomaly controls */}
        <div className="left-panel">
          <TripSearch onResult={handleResult} />
        </div>

        {/* Right panel: comparison + map + crowding list */}
        <div className="right-panel">
          <ComparisonCard
            naive={recommendation?.naive}
            recommended={recommendation?.options?.[0] || null}
          />
          <RouteMap routeId={selectedRoute} />
          <AnomalyButton />
          <StopCrowdingList
            selectedRoute={selectedRoute}
            onRouteChange={setSelectedRoute}
          />
        </div>
      </div>
    </div>
  );
}
