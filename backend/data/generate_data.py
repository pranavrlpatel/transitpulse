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
from datetime import datetime, timedelta, timezone

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

START_DATE = datetime(2025, 7, 1, tzinfo=timezone.utc)

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
# ── Anomaly injection ────────────────────────────────────────────────────────
# Generate 100 random anomalies spread across the 30 days
ANOMALIES = []
for _ in range(100):
    a_day = random.randint(0, NUM_DAYS - 1)
    a_stop = random.choice(list(STOP_NAMES.keys()))
    a_start_h = random.uniform(6.0, 20.0)
    a_dur_h = random.uniform(2.0, 5.0)
    a_sev = random.uniform(0.2, 1.0)
    a_type = random.choice(["breakdown", "stormy", "rainy", "protest"])
    ANOMALIES.append({
        "day": a_day, "stop_id": a_stop, "start_h": a_start_h,
        "dur_h": a_dur_h, "severity": a_sev, "type": a_type
    })

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import state, propagation

# Mock state.get_active_anomalies to bypass the real-time filter
state.get_active_anomalies = lambda: list(state._active_anomalies)

def generate() -> pd.DataFrame:
    rows: list[dict] = []
    
    # Pre-generate weather for each day so it's consistent
    daily_weather = {day: max(0.0, np.random.normal(5.0, 8.0)) if random.random() > 0.6 else 0.0 for day in range(NUM_DAYS)}
    
    disrupted_count = 0
    total_count = 0

    for day in range(NUM_DAYS):
        dt_day = START_DATE + timedelta(days=day)
        d_factor = day_factor(dt_day)
        weather_mm = daily_weather[day]
        weather_mult = 1.0 + min(weather_mm * 0.05, 0.4)

        # Pre-filter anomalies for this day
        active_anoms_for_day = [a for a in ANOMALIES if a["day"] == day]

        for slot in range(SLOTS_PER_DAY):
            minutes = slot * SLOT_MINUTES
            dt = dt_day + timedelta(minutes=minutes)
            hour_frac = dt.hour + dt.minute / 60.0

            # Manage anomalies in state
            state.clear_anomalies()
            for a in active_anoms_for_day:
                if a["start_h"] <= hour_frac < a["start_h"] + a["dur_h"]:
                    state._active_anomalies.append({
                        "stop_id": a["stop_id"],
                        "severity": a["severity"],
                        "anomaly_type": a["type"],
                        "started_at": dt.isoformat(),
                        "expires_at": (dt + timedelta(hours=2)).isoformat()
                    })

            for route_id, stops in ROUTE_DEFINITIONS.items():
                for stop_idx, stop_id in enumerate(stops):
                    capacity = BASE_CAPACITY[stop_id]
                    
                    # 1. Base
                    rider = base_ridership(hour_frac, capacity)
                    # 2. Day multiplier
                    rider *= d_factor
                    # 3. Weather multiplier
                    rider *= weather_mult
                    # 4. Disruption multiplier (from propagation!)
                    crowd_mult, added_delay = propagation.get_disruption_impacts(stop_id)
                    rider *= crowd_mult
                    
                    if crowd_mult > 1.0:
                        disrupted_count += 1
                    total_count += 1
                    
                    # Gaussian noise ±10 %
                    rider *= max(0.0, np.random.normal(1.0, 0.10))
                    
                    # Ensure it stays within physical limits but allows crowding
                    rider = min(rider, capacity * 2.0)

                    delay = max(0.0, np.random.normal(1.0, 0.8)) + added_delay

                    rows.append({
                        "stop_id":        stop_id,
                        "route_id":       route_id,
                        "timestamp":      dt.isoformat(),
                        "weather_intensity_mm": round(weather_mm, 2),
                        "disruption_multiplier_at_time": round(crowd_mult, 3),
                        "ridership":      round(rider, 1),
                        "capacity":       capacity,
                        "delay_minutes":  round(delay, 2),
                    })
                    
    percent_disrupted = (disrupted_count / total_count) * 100
    print(f"  --> {percent_disrupted:.2f}% of rows have disruption_multiplier > 1.0")

    return pd.DataFrame(rows)


def main():
    print("Generating synthetic transit data …")
    df = generate()
    print(f"  {len(df):,} rows generated.")

    db_path = os.path.join(os.path.dirname(__file__), "transit_history.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    df.to_sql("history", conn, index=False, if_exists="replace")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_stop_ts ON history(stop_id, timestamp)")
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    sample = pd.read_sql("SELECT * FROM history ORDER BY RANDOM() LIMIT 5", conn)
    conn.close()

    print(f"  Written to {db_path} ({count:,} rows)")
    print("\nSample rows:")
    print(sample.to_string(index=False))


if __name__ == "__main__":
    main()
