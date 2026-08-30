"""
network.py — Transit network topology.
"""
from __future__ import annotations
import json

ROUTE_STOPS: dict[str, list[str]] = {
    "244-C VSD-0": [
        "27263",
        "20985",
        "20922",
        "35387",
        "21200",
        "35429",
        "20587",
        "21103",
        "28613",
        "20600",
        "33481",
        "20906",
        "35413",
        "20937",
        "22615",
        "35404",
        "21642",
        "22374",
        "35595"
    ],
    "296-0": [
        "20922",
        "20985",
        "21259",
        "35192",
        "21869",
        "34912",
        "32206",
        "21706",
        "32378",
        "36715",
        "22298",
        "21929",
        "21891",
        "21827",
        "22230",
        "33706",
        "22124",
        "39173",
        "39174",
        "35921",
        "25856",
        "35587",
        "35585"
    ],
    "296-1": [
        "29409",
        "35587",
        "25856",
        "35921",
        "39174",
        "39173",
        "22124",
        "33706",
        "22230",
        "21827",
        "21891",
        "35922",
        "36715",
        "32378",
        "21706",
        "21868",
        "35192",
        "21259",
        "38026",
        "20985",
        "20697",
        "20922"
    ],
    "296-B-0": [
        "20922",
        "20985",
        "21259",
        "35192",
        "21869",
        "34912",
        "32206",
        "21706",
        "32378",
        "36715",
        "22298",
        "21929",
        "21891",
        "21827",
        "22230",
        "33706",
        "22124",
        "39173",
        "39174",
        "35921",
        "25856",
        "35587",
        "35585"
    ],
    "296-B-1": [
        "29409",
        "35587",
        "25856",
        "35921",
        "39174",
        "39173",
        "22124",
        "33706",
        "22230",
        "21827",
        "21891",
        "35922",
        "36715",
        "32378",
        "21706",
        "21868",
        "35192",
        "21259",
        "20985",
        "20697",
        "20922"
    ],
    "300-H KBS-ADMC-0": [
        "20922",
        "20985",
        "21259",
        "35192",
        "21869",
        "34912",
        "32206",
        "21706",
        "32378",
        "36720",
        "21863",
        "22298",
        "21929",
        "36721",
        "22090",
        "22273",
        "27947",
        "36254",
        "38855"
    ],
    "300-H KBS-ADMC-1": [
        "38855",
        "27947",
        "22273",
        "22090",
        "36721",
        "22298",
        "21863",
        "32378",
        "21706",
        "21868",
        "35192",
        "21259",
        "20985",
        "20697",
        "20922"
    ],
    "45-D-0": [
        "20922",
        "20985",
        "22197",
        "21195",
        "20728",
        "31416",
        "22201",
        "22243",
        "23479",
        "21746",
        "23728",
        "20808",
        "39632",
        "21066",
        "22512",
        "21717",
        "22472",
        "39840",
        "35951",
        "23965",
        "24346",
        "24344",
        "35090",
        "24342",
        "35532"
    ]
}
STOP_NAMES: dict[str, str] = {
    "35595": "2nd Stage 9th Block Nagarabhavi",
    "29409": "5th Block HBR Layout",
    "38855": "ADMC Quarters Office",
    "35532": "AGS Layout Arehalli",
    "24342": "AGS Layout Cross",
    "20600": "Agrahara Dasarahalli",
    "36254": "Ayyappa Temple (Subbayyanapalya)",
    "35404": "BDA Complex Nagarabhavi",
    "21706": "Bamboo Bazar",
    "21717": "Bank Colony",
    "21746": "Bengaluru High School",
    "21868": "CSI Hospital",
    "32206": "Cantonment Railway Station",
    "20697": "Cauvery Bhavana",
    "23479": "Chamarajapet",
    "21827": "Charls School Toll Gate",
    "35922": "Clarence School",
    "32378": "Coles Park",
    "21863": "Coles Road",
    "20728": "Corporation",
    "21869": "Cunningham Road",
    "39174": "Depot-10 Gate",
    "21891": "Devis Road",
    "21929": "East Railway Station",
    "36715": "Frazer Town",
    "35429": "Gopalapura",
    "35587": "HBR Layout 4th Block",
    "35585": "HBR Layout 5th Block",
    "20808": "Hanumanthanagara Ward Office",
    "25856": "Hennur Cross",
    "35921": "Hennur Junction",
    "35951": "Hosakerehalli  Junction",
    "39840": "Hoskerehalli Cross",
    "36721": "ITC Factory",
    "35192": "Indian Express",
    "27947": "Indian Oil",
    "35090": "Ittamadu",
    "22090": "Jai Bharath Nagara",
    "23965": "Janatabazar Junction",
    "22124": "Jyothi School",
    "33481": "KHB Colony",
    "22197": "KR Circle",
    "22201": "KR Market",
    "39173": "Kacharakanahalli",
    "20906": "Kamakshipalya",
    "20922": "Kempegowda Bus Station",
    "20937": "Kottigepalya",
    "33706": "Lingarajapura",
    "22230": "Lingarajapura Bridge",
    "38026": "MS Building",
    "28613": "Magadi Road Tollgate",
    "20985": "Maharani College",
    "22243": "Makkala Koota",
    "22273": "Maruthi Sevanagara",
    "22298": "Mosque Road",
    "21066": "Nirmala Store",
    "35387": "Okalipura",
    "22374": "Papareddypalya",
    "21642": "Papareddypalya Aladamara",
    "21103": "Prasanna Theatre",
    "20587": "Rajajinagara 6th Block",
    "23728": "Ramakrishna Ashrama",
    "21200": "S J R College",
    "24344": "SLV Bakery",
    "22472": "Seetha Circle",
    "36720": "Seventh Day School (Coles Park)",
    "24346": "Srinivasa Kalyana Mantapa",
    "22512": "Srinivasa Nagara",
    "21195": "St Marthas Hospital",
    "39632": "Subramanya Swamy Temple",
    "35413": "Summanahalli",
    "31416": "Town Hall",
    "34912": "Vasantha Nagara",
    "27263": "Vidhana Soudha",
    "21259": "Vidhana Soudha Karnataka High Court",
    "22615": "Vokkaliga School Kottigepalya"
}

def _build_adjacency() -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {}
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
    stop_to_routes = {}
    for rid, stops in ROUTE_STOPS.items():
        for s in stops:
            stop_to_routes.setdefault(s, []).append(rid)

    from collections import deque
    queue = deque()
    visited = {}
    
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
