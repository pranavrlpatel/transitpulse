import { useState } from 'react';
import TripSearch from './components/TripSearch';
import ComparisonCard from './components/ComparisonCard';
import StopCrowdingList from './components/StopCrowdingList';
import AnomalyButton from './components/AnomalyButton';
import RouteMap from './components/RouteMap';
import { fetchRecommend } from './api';
import './styles/index.css';

export default function App() {
  const [currentView, setCurrentView] = useState('search');
  const [selectedRoute, setSelectedRoute] = useState('244-C VSD-0');
  const [recommendation, setRecommendation] = useState(null);
  const [showAnomalyModal, setShowAnomalyModal] = useState(false);

  // Hoisted state for auto-refresh
  const [origin, setOrigin] = useState('21869');
  const [destination, setDestination] = useState('38855');
  const [targetTime, setTargetTime] = useState(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  });
  const [isSearching, setIsSearching] = useState(false);

  const refreshRecommendation = async () => {
    if (!origin || !destination) return;
    setIsSearching(true);
    try {
      const isoTime = new Date(targetTime).toISOString();
      const result = await fetchRecommend(origin, destination, isoTime);
      setRecommendation(result);
      if (result?.options?.length > 0) {
        const best = result.options[0];
        const routeId = best.route || best.first_route;
        if (routeId) setSelectedRoute(routeId);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchSubmit = async () => {
    await refreshRecommendation();
    setCurrentView('dashboard');
  };

  if (currentView === 'search') {
    return (
      <div className="search-page">
        <div className="search-container">
          <div className="logo-header">
            <img src="/logo.jpg" alt="TransitPulse Logo" className="logo-img" />
            <h1>TransitPulse</h1>
          </div>
          <p className="subtitle">Real-time crowding prediction & smart route recommendations</p>
          <div className="search-box">
            <TripSearch 
              origin={origin} setOrigin={setOrigin}
              destination={destination} setDestination={setDestination}
              targetTime={targetTime} setTargetTime={setTargetTime}
              onSearch={handleSearchSubmit}
              loading={isSearching}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-logo">
          <img src="/logo.jpg" alt="Logo" />
        </div>
        <div className="sidebar-actions">
          <button className="sidebar-icon" title="Trip Search" onClick={() => setCurrentView('search')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </button>
          <button className="sidebar-icon" title="Disruption Simulator" onClick={() => setShowAnomalyModal(true)}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          </button>
        </div>
      </nav>

      {/* Main Dashboard Area */}
      <main className="dashboard-main">
        <header className="dashboard-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2>Route Comparison</h2>
            <span style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>TransitPulse</span>
          </div>
        </header>
        
        <div className="dashboard-content">
          <ComparisonCard
            naive={recommendation?.naive}
            recommended={recommendation?.options?.[0] || null}
          />
          <div className="dashboard-row">
            <RouteMap routeId={selectedRoute} />
            <StopCrowdingList
              selectedRoute={selectedRoute}
              onRouteChange={setSelectedRoute}
            />
          </div>
        </div>
      </main>

      {/* Anomaly Modal */}
      <div 
        className="modal-overlay" 
        style={{ display: showAnomalyModal ? 'flex' : 'none' }} 
        onClick={() => setShowAnomalyModal(false)}
      >
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <button className="modal-close" onClick={() => setShowAnomalyModal(false)}>&times;</button>
          <AnomalyButton onAnomalyChanged={async () => {
            await refreshRecommendation();
            setShowAnomalyModal(false);
          }} />
        </div>
      </div>
    </div>
  );
}
