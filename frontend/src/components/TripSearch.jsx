import { useState, useEffect } from 'react';
import { fetchStops } from '../api';

export default function TripSearch({ 
  origin, setOrigin, 
  destination, setDestination, 
  targetTime, setTargetTime, 
  onSearch, loading 
}) {
  const [stops, setStops] = useState([]);
  const [destStops, setDestStops] = useState([]);
  const [originLimit, setOriginLimit] = useState(10);
  const [destLimit, setDestLimit] = useState(10);

  useEffect(() => {
    fetchStops()
      .then((data) => {
        setStops(data);
        if (data.length >= 2 && !origin) {
          setOrigin(data[0].stop_id);
        }
      })
      .catch(console.error);
  }, []); // Only fetch stops on mount

  useEffect(() => {
    if (!origin) return;
    import('../api').then(({ fetchReachableStops }) => {
      fetchReachableStops(origin)
        .then((data) => {
          setDestStops(data);
          setDestLimit(10);
          if (data.length > 0 && (!destination || !data.find(d => d.stop_id === destination))) {
            setDestination(data[0].stop_id);
          }
        })
        .catch(console.error);
    });
  }, [origin]); // Refetch reachable dests when origin changes

  const handleOriginChange = (e) => {
    const val = e.target.value;
    if (val === 'LOAD_MORE') {
      setOriginLimit(prev => prev + 10);
    } else {
      setOrigin(val);
    }
  };

  const handleDestChange = (e) => {
    const val = e.target.value;
    if (val === 'LOAD_MORE') {
      setDestLimit(prev => prev + 10);
    } else {
      setDestination(val);
    }
  };

  const visibleOrigins = stops.slice(0, originLimit);
  const hasMoreOrigins = originLimit < stops.length;

  const visibleDests = destStops.slice(0, destLimit);
  const hasMoreDests = destLimit < destStops.length;

  return (
    <div className="glass-card">
      <div className="card-title">
        <span className="icon">&#128269;</span> Trip Search
      </div>
      <div className="trip-search">
        <div className="input-group">
          <label htmlFor="origin-select">From</label>
          <select
            id="origin-select"
            value={origin}
            onChange={handleOriginChange}
          >
            <option value="" disabled>Select origin</option>
            {visibleOrigins.map((s) => (
              <option key={s.stop_id} value={s.stop_id}>
                {s.name} ({s.stop_id})
              </option>
            ))}
            {hasMoreOrigins && (
              <option value="LOAD_MORE" className="load-more-option">
                Load More...
              </option>
            )}
          </select>
        </div>

        <div className="input-group">
          <label htmlFor="dest-select">To</label>
          <select
            id="dest-select"
            value={destination}
            onChange={handleDestChange}
          >
            <option value="" disabled>Select destination</option>
            {visibleDests.map((s) => (
              <option key={s.stop_id} value={s.stop_id}>
                {s.name} ({s.stop_id})
              </option>
            ))}
            {hasMoreDests && (
              <option value="LOAD_MORE" className="load-more-option">
                Load More...
              </option>
            )}
          </select>
        </div>

        <div className="input-group">
          <label htmlFor="time-select">Departure Time</label>
          <input
            type="datetime-local"
            id="time-select"
            value={targetTime}
            onChange={(e) => setTargetTime(e.target.value)}
          />
        </div>

        <button
          className="btn-search"
          onClick={onSearch}
          disabled={loading || !origin || !destination || origin === destination}
          id="search-button"
        >
          {loading ? 'Searching...' : 'Find Best Route'}
        </button>
      </div>
    </div>
  );
}
