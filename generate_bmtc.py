import csv, ast, json

stops_file = 'e:/bmtc-gtfs-main/bmtc-gtfs-main/csv/stops.csv'
routes_file = 'e:/bmtc-gtfs-main/bmtc-gtfs-main/csv/routes.csv'

name_to_id = {}
stop_names = {}
with open(stops_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name_to_id[row['name']] = row['id']
        stop_names[row['id']] = row['name']

route_stops = {}
with open(routes_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 500: break  # Top 500 routes
        rid = row['name'] + '-' + row['direction_id']
        stop_list_names = ast.literal_eval(row['stop_list'])
        stops_ids = [name_to_id.get(n) for n in stop_list_names if name_to_id.get(n)]
        # Filter out empty or single stop routes
        if len(stops_ids) > 1:
            route_stops[rid] = stops_ids

# Filter stop_names to only include stops that exist in the selected routes
active_stops = set()
for stops in route_stops.values():
    active_stops.update(stops)

filtered_stop_names = {k: v for k, v in stop_names.items() if k in active_stops}

out_py = f'''"""
network.py — Transit network topology.
"""
from __future__ import annotations

ROUTE_STOPS: dict[str, list[str]] = {json.dumps(route_stops, indent=4)}

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
'''

with open('backend/app/network.py', 'w', encoding='utf-8') as f:
    f.write(out_py)

print(f'Successfully wrote network.py with {len(route_stops)} routes and {len(filtered_stop_names)} stops.')
