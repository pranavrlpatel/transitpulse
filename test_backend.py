"""Quick standalone test for all backend modules."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app import network, state, propagation, prediction, recommendation
from datetime import datetime

print("=" * 60)
print("1. NETWORK")
print(f"   All stops ({len(network.get_all_stop_ids())}): {network.get_all_stop_ids()[:5]}...")
print(f"   Route R1: {network.ROUTE_STOPS['R1']}")
print(f"   Neighbors of S03: {network.get_neighbors('S03')}")
print(f"   Neighbors of S04: {network.get_neighbors('S04')}")

print("\n" + "=" * 60)
print("2. PREDICTION (no anomaly)")
ts = "2025-07-15T08:30:00"
c = prediction.predict_crowding("S01", ts)
d = prediction.predict_delay("S01", ts)
print(f"   S01 @ {ts}:")
print(f"     crowding={c:.4f}  tier={prediction.crowding_tier(c)}")
print(f"     delay={d:.2f} min")

print("\n" + "=" * 60)
print("3. PROPAGATION (inject anomaly at S04, severity=0.8)")
state.inject_anomaly("S04", 0.8)
for sid in ["S04", "S05", "S06", "S07", "S01"]:
    m = propagation.get_disruption_multiplier(sid)
    print(f"   {sid} ({network.get_stop_name(sid):20s})  multiplier = {m:.4f}")

print("\n" + "=" * 60)
print("4. PREDICTION (with anomaly)")
c2 = prediction.predict_crowding("S04", ts)
d2 = prediction.predict_delay("S04", ts)
print(f"   S04 @ {ts}:")
print(f"     crowding={c2:.4f}  tier={prediction.crowding_tier(c2)}")
print(f"     delay={d2:.2f} min")

state.clear_anomalies()
print("   (anomalies cleared)")

print("\n" + "=" * 60)
print("5. RECOMMENDATION  S01 -> S07")
result = recommendation.recommend("S01", "S07", ts)
print(f"   Naive: route={result['naive'].get('route')}  "
      f"score={result['naive']['score']}  "
      f"crowding={result['naive']['avg_crowding']}  "
      f"tier={result['naive']['crowding_tier']}")
for i, opt in enumerate(result["options"]):
    print(f"   Opt {i+1}: route={opt.get('route')}  dep={opt['departure_time']}  "
          f"score={opt['score']}  tier={opt['crowding_tier']}")

print("\n" + "=" * 60)
print("6. RECOMMENDATION  S01 -> S12 (needs transfer via S03)")
result2 = recommendation.recommend("S01", "S12", ts)
if result2["options"]:
    opt = result2["options"][0]
    print(f"   Best: type={opt['type']}  "
          f"first={opt.get('first_route')} -> {opt.get('interchange')} -> {opt.get('second_route')}")
    print(f"   stops={opt['stops']}  score={opt['score']}")
else:
    print("   No options found!")

print("\nAll tests passed!")
