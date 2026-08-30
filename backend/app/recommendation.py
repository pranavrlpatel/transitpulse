"""
recommendation.py — Route option discovery and scoring.

find_route_options():  direct routes + single-transfer combos (no general pathfinding).
recommend():           evaluate departure windows, score by crowding + delay, return top 3 + naive.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from . import network, prediction


# ── Route option discovery ───────────────────────────────────────────────────

def find_route_options(
    origin: str,
    dest: str,
    route_stops: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    """
    Find up to 3 route options between *origin* and *dest*.
    Supports arbitrary number of transfers via BFS to minimize transfers and stops.
    Optimized with an index and transfer cap.
    """
    if route_stops is None:
        from . import network
        route_stops = network.ROUTE_STOPS

    from collections import deque

    # Build reverse index for fast O(1) transfer lookups
    stop_to_routes = {}
    for rid, stops in route_stops.items():
        for s in stops:
            stop_to_routes.setdefault(s, []).append(rid)

    # Queue stores: (current_stop, current_route, path_stops, path_routes)
    queue = deque()
    visited: dict[tuple[str, str], int] = {}
    
    if origin not in stop_to_routes:
        return []

    for rid in stop_to_routes[origin]:
        queue.append((origin, rid, [origin], [rid]))
        visited[(origin, rid)] = 0

    found_paths = []
    MAX_TRANSFERS = 2  # Hard limit to keep searches lightning fast

    while queue:
        curr_stop, curr_route, p_stops, p_routes = queue.popleft()

        if curr_stop == dest:
            parts = [p_routes[0]]
            for i in range(1, len(p_stops)):
                if p_routes[i] != p_routes[i-1]:
                    parts.append(p_stops[i])
                    parts.append(p_routes[i])
            found_paths.append({
                "type": "multi",
                "path_label": " -> ".join(parts),
                "stops": p_stops
            })
            if len(found_paths) >= 20:
                break
            continue

        transfers = sum(1 for i in range(1, len(p_routes)) if p_routes[i] != p_routes[i-1])

        # 1. Stay on current route
        stops_on_route = route_stops[curr_route]
        idx = stops_on_route.index(curr_stop)
        if idx + 1 < len(stops_on_route):
            nxt_stop = stops_on_route[idx + 1]
            if visited.get((nxt_stop, curr_route), 999) > transfers:
                visited[(nxt_stop, curr_route)] = transfers
                queue.append((nxt_stop, curr_route, p_stops + [nxt_stop], p_routes + [curr_route]))

        # 2. Transfer to another route (only if within limit)
        if transfers < MAX_TRANSFERS:
            for nxt_route in stop_to_routes.get(curr_stop, []):
                if nxt_route != curr_route:
                    if visited.get((curr_stop, nxt_route), 999) > transfers + 1:
                        visited[(curr_stop, nxt_route)] = transfers + 1
                        queue.append((curr_stop, nxt_route, p_stops, p_routes[:-1] + [nxt_route]))

    # Sort options by number of transfers, then total travel time (stops)
    found_paths.sort(key=lambda x: (x["path_label"].count("->"), len(x["stops"])))

    # Deduplicate
    unique_paths = []
    seen = set()
    for p in found_paths:
        sig = tuple(p["stops"])
        if sig not in seen:
            seen.add(sig)
            unique_paths.append(p)

    return unique_paths[:3]


# ── Scoring helper ───────────────────────────────────────────────────────────

def _score_option(
    stops: list[str],
    departure: datetime,
    wait_time_minutes: float = 0.0,
) -> tuple[float, float, float]:
    """
    Compute aggregate (score, avg_crowding, avg_delay) for a list of stops
    at a given departure time.

    score = avg_crowding * 0.6 + normalized_delay * 0.2 + normalized_wait * 0.2
    """
    crowdings: list[float] = []
    delays: list[float] = []

    for stop in stops:
        c = prediction.predict_crowding(stop, departure)
        d = prediction.predict_delay(stop, departure)
        crowdings.append(c)
        delays.append(d)

    avg_crowding = sum(crowdings) / len(crowdings) if crowdings else 0.0
    avg_delay = sum(delays) / len(delays) if delays else 0.0

    # Normalize delay and wait time: treat 60 min as max -> 1.0
    norm_delay = min(avg_delay / 60.0, 1.0)
    norm_wait = min(wait_time_minutes / 60.0, 1.0)

    # Heavily penalize waiting so the AI prefers jumping on a transfer route right now
    score = avg_crowding * 0.6 + norm_delay * 0.2 + norm_wait * 0.8
    return score, avg_crowding, avg_delay


# ── Public API ───────────────────────────────────────────────────────────────

def recommend(
    origin: str,
    dest: str,
    target_time: datetime | str,
) -> dict[str, Any]:
    """
    Return ``{options: [...top 3 scored...], naive: {...}}``

    Each option dict has:
      type, route (or first_route/interchange/second_route), stops,
      departure_time, score, avg_crowding, avg_delay, crowding_tier
    """
    if isinstance(target_time, str):
        target_time = datetime.fromisoformat(target_time)

    route_options = find_route_options(origin, dest)
    if not route_options:
        return {"options": [], "naive": None}

    # ── Evaluate departure windows for each route option ─────────────
    scored: list[dict[str, Any]] = []
    for opt in route_options:
        stops = opt["stops"]
        # Check every 5 min from 0 min to +30 min after target_time
        for delta_min in range(0, 31, 5):
            dep = target_time + timedelta(minutes=delta_min)
            score, avg_c, avg_d = _score_option(stops, dep, wait_time_minutes=delta_min)
            entry = {
                **opt,
                "departure_time": dep.isoformat(),
                "score": round(score, 4),
                "avg_crowding": round(avg_c, 4),
                "avg_delay": round(avg_d, 2),
                "crowding_tier": prediction.crowding_tier(avg_c),
            }
            scored.append(entry)

    scored.sort(key=lambda x: x["score"])
    top3 = scored[:3]

    # ── Naive option: first route, exactly at target_time ────────────
    first_opt = route_options[0]
    n_score, n_c, n_d = _score_option(first_opt["stops"], target_time, wait_time_minutes=0.0)
    naive = {
        **first_opt,
        "departure_time": target_time.isoformat(),
        "score": round(n_score, 4),
        "avg_crowding": round(n_c, 4),
        "avg_delay": round(n_d, 2),
        "crowding_tier": prediction.crowding_tier(n_c),
    }

    return {"options": top3, "naive": naive}
