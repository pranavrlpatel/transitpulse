import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app import state, prediction, recommendation, network
from datetime import datetime

ts = datetime(2026, 8, 30, 14, 0, 0)
epicenter = "20922"  # Kempegowda Bus Station

print(f"--- Diagnosing Avg Delay Dilution ---")
print(f"Epicenter (Anomaly location): {epicenter} (Kempegowda Bus Station)")

# User's searched route: Rajajinagara 6th Block (20587) to Papareddypalya (21642)
options = recommendation.find_route_options("20587", "21642")
route_stops = options[0]["stops"]
print(f"Trip Path length: {len(route_stops)} stops")

def test_avg_delay(severity):
    print(f"\n--- Testing Severity {severity} ---")
    state.clear_anomalies()
    if severity > 0:
        state.inject_anomaly(epicenter, severity, "breakdown")
        
    delays = []
    print("Per-stop delays:")
    for i, stop in enumerate(route_stops):
        d = prediction.predict_delay(stop, ts)
        delays.append(d)
        name = network.get_stop_name(stop)
        is_epicenter = " <--- EPICENTER" if stop == epicenter else ""
        print(f"  Stop {i:02d} ({name}): {d:.2f} min{is_epicenter}")
        
    avg_delay = sum(delays) / len(delays)
    print(f"\nFINAL AVG DELAY (sum / length): {avg_delay:.2f} min")

test_avg_delay(0.0)
test_avg_delay(1.0)
