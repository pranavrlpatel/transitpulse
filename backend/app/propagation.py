"""
propagation.py — Cascade decay logic over the adjacency map.

For every active anomaly, does a BFS walk outward from the anomaly stop.
At hop n, impact = severity * (1 - DECAY_RATE) ** n.
Stops expanding when impact < MIN_IMPACT.
Sums contributions from all active anomalies for a given stop.
Returns multiplier = 1.0 + total_impact.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime

from . import network, state

MIN_IMPACT = 0.05

# Type configs (within ~20% of baseline Breakdown)
# format: { type: (decay_rate, max_delay_minutes) }
ANOMALY_CONFIGS = {
    "breakdown": (0.30, 60.0), # Baseline
    "stormy":    (0.24, 72.0), # Spreads further (-20% decay), higher peak (+20% delay)
    "rainy":     (0.36, 48.0), # Spreads less (+20% decay), lower peak (-20% delay)
    "protest":   (0.27, 54.0), # Slightly wider spread (-10% decay), slightly less peak (-10% delay)
    "general":   (0.30, 60.0), # Fallback
}

def get_disruption_impacts(stop_id: str, timestamp: datetime | None = None) -> tuple[float, float]:
    """
    Returns (crowding_multiplier, total_added_delay_minutes)
    """
    anomalies = state.get_active_anomalies()
    if not anomalies:
        return 1.0, 0.0

    total_crowding_impact = 0.0
    total_added_delay = 0.0

    # Calculate minutes in the future if timestamp provided
    future_mins = 0.0
    if timestamp:
        now = datetime.now()
        # If timestamp is naive, assume local. If aware, this might need timezone handling.
        # But for the hackathon, a simple difference is fine:
        try:
            diff = (timestamp.replace(tzinfo=None) - now.replace(tzinfo=None)).total_seconds() / 60.0
            future_mins = max(0.0, diff)
        except Exception:
            future_mins = 0.0

    for anomaly in anomalies:
        origin = anomaly["stop_id"]
        # Decay severity over time (loses 2% severity per minute in the future)
        time_decay = max(0.0, 1.0 - (future_mins * 0.02))
        severity = anomaly["severity"] * time_decay
        
        if severity <= 0:
            continue
            
        a_type = anomaly.get("anomaly_type", "general")
        decay_rate, max_delay = ANOMALY_CONFIGS.get(a_type, ANOMALY_CONFIGS["general"])

        # BFS with distance tracking
        visited: dict[str, int] = {origin: 0}
        queue: deque[str] = deque([origin])

        while queue:
            current = queue.popleft()
            hop = visited[current]
            impact = severity * (1 - decay_rate) ** hop

            if impact < MIN_IMPACT:
                continue

            if current == stop_id:
                total_crowding_impact += impact
                total_added_delay += (impact * max_delay)

            for neighbor in network.get_neighbors(current):
                if neighbor not in visited:
                    visited[neighbor] = hop + 1
                    queue.append(neighbor)

    return 1.0 + total_crowding_impact, total_added_delay

def get_disruption_multiplier(stop_id: str, timestamp: datetime | None = None) -> float:
    # Backwards compatibility if called directly
    return get_disruption_impacts(stop_id, timestamp)[0]
