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

from . import network, state

DECAY_RATE = 0.3
MIN_IMPACT = 0.05


def get_disruption_multiplier(stop_id: str) -> float:
    """
    Compute the aggregate disruption multiplier for *stop_id*
    considering all currently active anomalies.
    """
    anomalies = state.get_active_anomalies()
    if not anomalies:
        return 1.0

    total_impact = 0.0

    for anomaly in anomalies:
        origin = anomaly["stop_id"]
        severity = anomaly["severity"]

        # BFS with distance tracking
        visited: dict[str, int] = {origin: 0}
        queue: deque[str] = deque([origin])

        while queue:
            current = queue.popleft()
            hop = visited[current]
            impact = severity * (1 - DECAY_RATE) ** hop

            if impact < MIN_IMPACT:
                continue

            if current == stop_id:
                total_impact += impact

            for neighbor in network.get_neighbors(current):
                if neighbor not in visited:
                    visited[neighbor] = hop + 1
                    queue.append(neighbor)

    return 1.0 + total_impact
