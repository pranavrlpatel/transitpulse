"""
generate_data.py — Synthetic historical transit dataset generator.

Produces a SQLite database (transit_history.db) with a single `history` table:
  stop_id, route_id, timestamp, ridership, capacity, delay_minutes

Algorithm:
  1. Generate 6 routes × ~40 stops (sequential IDs).
  2. For each stop × 15-min slot × 30 days:
     - Base ridership = sum of two Gaussians (peaks at 08:00 and 18:00).
     - Multiply by day-of-week factor (1.0 weekday, 0.55 weekend).
     - Add Gaussian noise (~±10%).
  3. Inject 2–3 anomalies: 1.8× ridership for 2–3 hours + fixed delay.
  4. Write to SQLite.
"""

import sqlite3
import os
import random
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Network definition ───────────────────────────────────────────────────────
# 6 routes, each with 6–8 stops.  Some stops are shared (transfer points).
# Total unique stops ≈ 40.

import sys
import os

# Ensure the backend directory is in the path to import app.network
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.network import ROUTE_STOPS as ROUTE_DEFINITIONS, STOP_NAMES


# Capacity per stop (passengers that fit in the typical vehicle serving it)
# Varies by route size to keep things realistic.
BASE_CAPACITY = {sid: random.randint(50, 120) for sid in STOP_NAMES}

# ── Time parameters ──────────────────────────────────────────────────────────
NUM_DAYS = 30
SLOT_MINUTES = 15
SLOTS_PER_DAY = 24 * 60 // SLOT_MINUTES  # 96

START_DATE = datetime(2025, 7, 1)

# ── Ridership model ──────────────────────────────────────────────────────────

def _gaussian(x: float, mu: float, sigma: float) -> float:
    """Unnormalized Gaussian."""
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def base_ridership(hour_frac: float, capacity: int) -> float:
    """
    Sum of two Gaussians centred at 08:00 and 18:00.
    Returns a raw rider count (before noise / day factor).
    """
    morning = _gaussian(hour_frac, 8.0, 1.5)
    evening = _gaussian(hour_frac, 18.0, 1.5)
    peak = morning + evening          # max ≈ 1.0 at peak hours
    off_peak_floor = 0.08             # ~8 % of capacity even at 3 AM
    return capacity * (off_peak_floor + 0.85 * peak)


def day_factor(dt: datetime) -> float:
    """1.0 on weekdays, 0.55 on weekends."""
    return 0.55 if dt.weekday() >= 5 else 1.0


# ── Anomaly injection ────────────────────────────────────────────────────────
# Each anomaly: (day_offset, route_id, start_hour, duration_hours,
#                ridership_mult, extra_delay_min, from_stop_index)
ANOMALIES = []


def _is_anomaly(route_id: str, stop_idx: int, dt: datetime) -> tuple[bool, float, float]:
    """Return (is_anomalous, ridership_multiplier, extra_delay)."""
    day_offset = (dt - START_DATE).days
    hour_frac = dt.hour + dt.minute / 60.0
    for a in ANOMALIES:
        if (a["route"] == route_id
                and day_offset == a["day"]
                and a["start_h"] <= hour_frac < a["start_h"] + a["dur_h"]
                and stop_idx >= a["from_idx"]):
            return True, a["rider_mult"], a["delay"]
    return False, 1.0, 0.0


# ── Main generation loop ─────────────────────────────────────────────────────

def generate() -> pd.DataFrame:
    rows: list[dict] = []
    for day in range(NUM_DAYS):
        dt_day = START_DATE + timedelta(days=day)
        d_factor = day_factor(dt_day)

        for route_id, stops in ROUTE_DEFINITIONS.items():
            for stop_idx, stop_id in enumerate(stops):
                capacity = BASE_CAPACITY[stop_id]
                for slot in range(SLOTS_PER_DAY):
                    minutes = slot * SLOT_MINUTES
                    dt = dt_day + timedelta(minutes=minutes)
                    hour_frac = dt.hour + dt.minute / 60.0

                    rider = base_ridership(hour_frac, capacity)
                    rider *= d_factor
                    # Gaussian noise ±10 %
                    rider *= max(0.0, np.random.normal(1.0, 0.10))

                    delay = max(0.0, np.random.normal(1.0, 0.8))  # baseline ~1 min

                    # Anomaly check
                    is_anom, r_mult, extra_delay = _is_anomaly(route_id, stop_idx, dt)
                    if is_anom:
                        rider *= r_mult
                        delay += extra_delay

                    rows.append({
                        "stop_id":        stop_id,
                        "route_id":       route_id,
                        "timestamp":      dt.isoformat(),
                        "ridership":      round(rider, 1),
                        "capacity":       capacity,
                        "delay_minutes":  round(delay, 2),
                    })

    return pd.DataFrame(rows)


def main():
    print("Generating synthetic transit data …")
    df = generate()
    print(f"  {len(df):,} rows generated.")

    db_path = os.path.join(os.path.dirname(__file__), "transit_history.db")
    # Remove stale DB if present
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    df.to_sql("history", conn, index=False, if_exists="replace")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_stop_ts ON history(stop_id, timestamp)")
    conn.commit()

    # Quick sanity check
    count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    sample = pd.read_sql("SELECT * FROM history ORDER BY RANDOM() LIMIT 5", conn)
    conn.close()

    print(f"  Written to {db_path} ({count:,} rows)")
    print("\nSample rows:")
    print(sample.to_string(index=False))


if __name__ == "__main__":
    main()
