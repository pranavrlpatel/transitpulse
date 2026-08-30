"""
state.py — In-memory store of currently active anomalies.

This module holds the live disruption state for the running demo.
No persistence is needed — state only lives for the lifetime of the server.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import TypedDict
import random


class Anomaly(TypedDict):
    stop_id: str
    severity: float
    anomaly_type: str
    started_at: str   # ISO-8601
    expires_at: str   # ISO-8601


_active_anomalies: list[Anomaly] = []


def inject_anomaly(stop_id: str, severity: float, anomaly_type: str = "general") -> Anomaly:
    """Add a new active anomaly with a random duration and return it."""
    duration_mins = random.randint(5, 60)
    now = datetime.now(timezone.utc)
    entry: Anomaly = {
        "stop_id":    stop_id,
        "severity":   severity,
        "anomaly_type": anomaly_type,
        "started_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=duration_mins)).isoformat(),
    }
    _active_anomalies.append(entry)
    return entry


def clear_anomalies() -> int:
    """Remove all active anomalies.  Returns the count of cleared entries."""
    n = len(_active_anomalies)
    _active_anomalies.clear()
    return n


def get_active_anomalies() -> list[Anomaly]:
    """Return a shallow copy of the currently active (unexpired) anomaly list."""
    now = datetime.now(timezone.utc)
    valid_anomalies = []
    for a in _active_anomalies:
        if datetime.fromisoformat(a["expires_at"]) > now:
            valid_anomalies.append(a)
            
    # Clean up expired
    _active_anomalies[:] = valid_anomalies
    return list(_active_anomalies)
