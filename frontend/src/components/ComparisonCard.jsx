/**
 * ComparisonCard.jsx — Side-by-side naive vs recommended route comparison.
 */

export default function ComparisonCard({ naive, recommended }) {
  if (!naive || !recommended) {
    return (
      <div className="glass-card">
        <div className="card-title">
          <span className="icon">&#9878;</span> Route Comparison
        </div>
        <div className="empty-state">
          Search for a trip to see the comparison
        </div>
      </div>
    );
  }

  const improvement = naive.score > 0
    ? Math.round((1 - recommended.score / naive.score) * 100)
    : 0;

  const formatTime = (iso) => {
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return iso;
    }
  };

  const routeLabel = (opt) => {
    if (opt.path_label) return opt.path_label;
    if (opt.type === 'direct') return opt.route;
    if (opt.type === 'transfer_2') return `${opt.first_route} → ${opt.interchange1} → ${opt.second_route} → ${opt.interchange2} → ${opt.third_route}`;
    return `${opt.first_route} → ${opt.interchange} → ${opt.second_route}`;
  };

  return (
    <div className="glass-card">
      <div className="card-title">
        <span className="icon">&#9878;</span> Route Comparison
      </div>
      <div className="comparison-container">
        {/* Naive */}
        <div className="comparison-block naive">
          <div className="comparison-label">Next Available</div>
          <div className="comparison-stat">
            <div className="stat-label">Crowding</div>
            <div className="stat-value">
              {Math.round(naive.avg_crowding * 100)}%
            </div>
            <div className="stat-detail">
              <span className={`tier-badge ${naive.crowding_tier}`}>
                {naive.crowding_tier}
              </span>
            </div>
          </div>
          <div className="comparison-stat">
            <div className="stat-label">Avg Delay</div>
            <div className="stat-value">{naive.avg_delay.toFixed(1)}min</div>
          </div>
          <div className="comparison-stat">
            <div className="stat-label">Departure</div>
            <div className="stat-value" style={{ fontSize: '1.1rem' }}>
              {formatTime(naive.departure_time)}
            </div>
            <div className="stat-detail">{routeLabel(naive)}</div>
          </div>
        </div>

        {/* Recommended */}
        <div className="comparison-block recommended">
          <div className="comparison-label">Recommended</div>
          <div className="comparison-stat">
            <div className="stat-label">Crowding</div>
            <div className="stat-value">
              {Math.round(recommended.avg_crowding * 100)}%
            </div>
            <div className="stat-detail">
              <span className={`tier-badge ${recommended.crowding_tier}`}>
                {recommended.crowding_tier}
              </span>
            </div>
          </div>
          <div className="comparison-stat">
            <div className="stat-label">Avg Delay</div>
            <div className="stat-value">{recommended.avg_delay.toFixed(1)}min</div>
          </div>
          <div className="comparison-stat">
            <div className="stat-label">Departure</div>
            <div className="stat-value" style={{ fontSize: '1.1rem' }}>
              {formatTime(recommended.departure_time)}
            </div>
            <div className="stat-detail">{routeLabel(recommended)}</div>
          </div>
          {improvement > 0 && (
            <div className="score-improvement">
              &#9650; {improvement}% better score
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
