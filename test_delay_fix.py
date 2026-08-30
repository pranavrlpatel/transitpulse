import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app import state, prediction, network
from datetime import datetime

# Choose a starting stop (epicenter)
stops = network.get_all_stop_ids()
epicenter = "20922"  # Kempegowda Bus Station (KBS)

# Manually find a path of hops
visited = {epicenter: 0}
queue = [epicenter]
hops_map = {0: epicenter}

while queue:
    curr = queue.pop(0)
    curr_hop = visited[curr]
    for neighbor in network.get_neighbors(curr):
        if neighbor not in visited:
            visited[neighbor] = curr_hop + 1
            if curr_hop + 1 not in hops_map:
                hops_map[curr_hop + 1] = neighbor
            queue.append(neighbor)
        if len(hops_map) >= 4:
            break
    if len(hops_map) >= 4:
        break

ts = datetime(2026, 8, 30, 14, 0, 0).isoformat()

def test_severity(severity):
    print(f"\n--- Testing Severity {severity} ---")
    state.clear_anomalies()
    # Baseline
    baselines = {}
    for hop in range(4):
        stop_id = hops_map.get(hop)
        if stop_id:
            baselines[hop] = prediction.predict_delay(stop_id, ts)
            
    # Inject
    state.inject_anomaly(epicenter, severity, "breakdown")
    
    for hop in range(4):
        stop_id = hops_map.get(hop)
        if stop_id:
            new_delay = prediction.predict_delay(stop_id, ts)
            added = new_delay - baselines[hop]
            print(f"Hop {hop} ({stop_id}): Baseline = {baselines[hop]:.2f}m | New Delay = {new_delay:.2f}m | Added = {added:.2f}m")

test_severity(1.0)
test_severity(0.3)
