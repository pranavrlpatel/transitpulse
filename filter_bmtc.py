import csv, ast, json
from collections import Counter

stops_file = 'e:/bmtc-gtfs-main/bmtc-gtfs-main/csv/stops.csv'
routes_file = 'e:/bmtc-gtfs-main/bmtc-gtfs-main/csv/routes.csv'

name_to_id = {}
stop_names = {}
with open(stops_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name_to_id[row['name']] = row['id']
        stop_names[row['id']] = row['name']

# Let's find a popular stop to use as a hub
route_stops_raw = []
with open(routes_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rid = row['name'] + '-' + row['direction_id']
        stop_list_names = ast.literal_eval(row['stop_list'])
        stops_ids = [name_to_id.get(n) for n in stop_list_names if name_to_id.get(n)]
        if len(stops_ids) > 1:
            route_stops_raw.append((rid, stops_ids))

stop_frequencies = Counter()
for rid, stops in route_stops_raw:
    stop_frequencies.update(stops)

top_hub = stop_frequencies.most_common(1)[0][0]
print(f'Top hub is {stop_names[top_hub]} ({top_hub}) with {stop_frequencies[top_hub]} routes.')

# Pick 8 routes that pass through the top hub
selected_routes = {}
for rid, stops in route_stops_raw:
    if top_hub in stops:
        selected_routes[rid] = stops
        if len(selected_routes) == 8:
            break

active_stops = set()
for stops in selected_routes.values():
    active_stops.update(stops)

filtered_stop_names = {k: v for k, v in stop_names.items() if k in active_stops}
print(f'Selected {len(selected_routes)} routes and {len(filtered_stop_names)} stops.')

out_py = f'''"""
network.py — Transit network topology.
"""
from __future__ import annotations
import json

ROUTE_STOPS: dict[str, list[str]] = {json.dumps(selected_routes, indent=4)}
STOP_NAMES: dict[str, str] = {json.dumps(filtered_stop_names, indent=4)}

def _build_adjacency() -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {{}}
    for stops in ROUTE_STOPS.values():
        for i in range(len(stops) - 1):
            adj.setdefault(stops[i], set()).add(stops[i + 1])
            adj.setdefault(stops[i + 1], set()).add(stops[i])
    for stops in ROUTE_STOPS.values():
        for s in stops:
            adj.setdefault(s, set())
    return adj

_ADJACENCY: dict[str, set[str]] = _build_adjacency()

def get_neighbors(stop_id: str) -> list[str]:
    return list(_ADJACENCY.get(stop_id, []))

def get_all_stop_ids() -> list[str]:
    return sorted(STOP_NAMES.keys())

def get_stop_name(stop_id: str) -> str:
    return STOP_NAMES.get(stop_id, stop_id)

def get_reachable_stops(origin: str, max_transfers: int = 2) -> list[str]:
    stop_to_routes = {{}}
    for rid, stops in ROUTE_STOPS.items():
        for s in stops:
            stop_to_routes.setdefault(s, []).append(rid)

    from collections import deque
    queue = deque()
    visited = {{}}
    
    if origin not in stop_to_routes:
        return []
        
    for rid in stop_to_routes[origin]:
        queue.append((origin, rid, 0))
        visited[(origin, rid)] = 0
        
    reachable = set([origin])
    
    while queue:
        curr_stop, curr_route, transfers = queue.popleft()
        reachable.add(curr_stop)
        
        stops_on_route = ROUTE_STOPS[curr_route]
        try:
            idx = stops_on_route.index(curr_stop)
            if idx + 1 < len(stops_on_route):
                nxt_stop = stops_on_route[idx + 1]
                if visited.get((nxt_stop, curr_route), 999) > transfers:
                    visited[(nxt_stop, curr_route)] = transfers
                    queue.append((nxt_stop, curr_route, transfers))
        except ValueError:
            pass
            
        if transfers < max_transfers:
            for nxt_route in stop_to_routes.get(curr_stop, []):
                if nxt_route != curr_route:
                    if visited.get((curr_stop, nxt_route), 999) > transfers + 1:
                        visited[(curr_stop, nxt_route)] = transfers + 1
                        queue.append((curr_stop, nxt_route, transfers + 1))
                        
    return sorted(list(reachable))
'''
with open('backend/app/network.py', 'w', encoding='utf-8') as f:
    f.write(out_py)
print('Wrote new network.py')
