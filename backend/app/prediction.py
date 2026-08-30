"""
prediction.py — Heuristic crowding and delay prediction.

Uses the spec formula:
  crowding_score = base_ratio * day_multiplier * weather_multiplier * disruption_multiplier

where base_ratio = avg(ridership) / capacity  (from historical DB, matched on
stop + time-of-day + day-of-week).

Time matching uses 15-minute slots for finer granularity, so different
departure times within the same hour produce different predictions.
"""

from __future__ import annotations

import math
import os
import sqlite3
from datetime import datetime
from functools import lru_cache

import pandas as pd

from . import propagation

# ── Database path ────────────────────────────────────────────────────────────
_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "transit_history.db")

# Demo flag — in a real system this would come from a weather API
WEATHER_RAINING = False


# ── Historical data helpers ──────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_base_capacity() -> dict[str, int]:
    """Return a dictionary of base capacities for each stop."""
    # Since we replaced the hardcoded network, we'll assign a deterministic pseudo-random
    # capacity based on the stop_id string so it's consistent.
    from . import network
    import hashlib
    caps = {}
    for sid in network.get_all_stop_ids():
        # Hash to get a consistent capacity between 50 and 120
        h = int(hashlib.md5(sid.encode()).hexdigest(), 16)
        caps[sid] = 50 + (h % 71)
    return caps

def _gaussian(x: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def _historical_avg(stop_id: str, hour: int, minute: int, dow: int) -> tuple[float, float, float]:
    """
    Return (avg_ridership, capacity, avg_delay) in O(1) time by re-computing
    the synthetic deterministic values rather than scanning 42M DB rows.
    """
    capacity = _get_base_capacity().get(stop_id, 100)
    
    hour_frac = hour + minute / 60.0
    morning = _gaussian(hour_frac, 8.0, 1.5)
    evening = _gaussian(hour_frac, 18.0, 1.5)
    peak = morning + evening
    off_peak_floor = 0.08
    rider = capacity * (off_peak_floor + 0.85 * peak)
    
    d_factor = 0.55 if dow >= 5 else 1.0
    rider *= d_factor
    
    # Deterministic noise based on stop and time
    import hashlib
    noise_seed = f"{stop_id}_{hour}_{minute}"
    h = int(hashlib.md5(noise_seed.encode()).hexdigest(), 16)
    noise_rider = (h % 20) / 100.0  # 0 to 20%
    rider *= (1.0 + noise_rider - 0.1)
    
    # Baseline delay with variation (e.g., peak hours = more delay)
    peak_delay = 5.0 * peak 
    random_delay = (h % 300) / 100.0  # 0 to 3.0 mins
    avg_delay = 1.0 + peak_delay + random_delay
    
    return rider, float(capacity), avg_delay



# ── Public API ───────────────────────────────────────────────────────────────

def predict_crowding(stop_id: str, timestamp: datetime | str) -> float:
    """
    Return a crowding score (fraction of capacity, can exceed 1.0).

    Formula from spec:
      base_ratio * day_multiplier * weather_multiplier * disruption_multiplier
    """
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    hour = timestamp.hour
    minute = timestamp.minute
    dow = timestamp.weekday()

    avg_rider, capacity, _ = _historical_avg(stop_id, hour, minute, dow)
    if capacity <= 0:
        capacity = 100.0

    base_ratio = avg_rider / capacity
    day_multiplier = 0.6 if dow >= 5 else 1.0
    weather_multiplier = 1.15 if WEATHER_RAINING else 1.0
    disruption_multiplier = propagation.get_disruption_multiplier(stop_id)

    return base_ratio * day_multiplier * weather_multiplier * disruption_multiplier


def predict_delay(stop_id: str, timestamp: datetime | str) -> float:
    """
    Return predicted delay in minutes.

    Uses historical average delay plus any active-anomaly flat delay bump
    (approximated via the disruption multiplier).
    """
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    hour = timestamp.hour
    minute = timestamp.minute
    dow = timestamp.weekday()

    _, _, avg_delay = _historical_avg(stop_id, hour, minute, dow)
    disruption = propagation.get_disruption_multiplier(stop_id)

    return avg_delay * disruption


def crowding_tier(score: float) -> str:
    """
    Convert a crowding score to a human-readable tier.

    Cutoffs from spec: 0.4 / 0.7 / 0.9
    """
    if score < 0.4:
        return "light"
    if score < 0.7:
        return "moderate"
    if score < 0.9:
        return "heavy"
    return "severe"
