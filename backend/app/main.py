"""
main.py — FastAPI application with all route handlers.

Endpoints:
  GET  /stops                     list all stops
  GET  /routes                    list all routes with stop lists
  GET  /predict                   single-stop crowding/delay prediction
  GET  /route-crowding            prediction for every stop on a route
  POST /recommend                 trip recommendation (naive + optimized)
  POST /inject-anomaly            inject a demo disruption
  POST /clear-anomalies           clear all active anomalies
"""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from . import network, prediction, state
from .recommendation import recommend as _recommend
from .schemas import (
    AnomalyResponse,
    InjectAnomalyRequest,
    RecommendRequest,
    RecommendResponse,
    RouteInfo,
    RouteOption,
    StopCrowding,
    StopInfo,
)

# ── App instance ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="TransitPulse API",
    version="1.0.0",
    description="Crowding prediction and route recommendation for public transit.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # dev convenience — lock down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/stops", response_model=list[StopInfo])
def list_stops():
    """Return every stop in the network."""
    return [
        StopInfo(stop_id=sid, name=network.get_stop_name(sid))
        for sid in network.get_all_stop_ids()
    ]


@app.get("/routes", response_model=list[RouteInfo])
def list_routes():
    """Return every route with its ordered stop list."""
    return [
        RouteInfo(route_id=rid, stops=stops)
        for rid, stops in network.ROUTE_STOPS.items()
    ]


@app.get("/predict", response_model=StopCrowding)
def predict_stop(
    stop_id: str = Query(..., description="Stop ID, e.g. S01"),
    timestamp: str = Query(
        ...,
        description="ISO-8601 datetime, e.g. 2025-07-15T08:30:00",
    ),
):
    """Predict crowding and delay for a single stop at a given time."""
    crowding = prediction.predict_crowding(stop_id, timestamp)
    delay = prediction.predict_delay(stop_id, timestamp)
    tier = prediction.crowding_tier(crowding)
    return StopCrowding(
        stop_id=stop_id,
        name=network.get_stop_name(stop_id),
        crowding=round(crowding, 4),
        tier=tier,
        delay=round(delay, 2),
    )


@app.get("/route-crowding", response_model=list[StopCrowding])
def route_crowding(
    route_id: str = Query(..., description="Route ID, e.g. R1"),
    timestamp: str = Query(
        default=None,
        description="ISO-8601 datetime; defaults to now.",
    ),
):
    """Return crowding predictions for every stop on a route."""
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    stops = network.ROUTE_STOPS.get(route_id, [])
    results: list[StopCrowding] = []
    for sid in stops:
        c = prediction.predict_crowding(sid, timestamp)
        d = prediction.predict_delay(sid, timestamp)
        results.append(StopCrowding(
            stop_id=sid,
            name=network.get_stop_name(sid),
            crowding=round(c, 4),
            tier=prediction.crowding_tier(c),
            delay=round(d, 2),
        ))
    return results


@app.post("/recommend", response_model=RecommendResponse)
def recommend_trip(req: RecommendRequest):
    """Find the best route + departure time for a trip."""
    result = _recommend(req.origin, req.destination, req.target_time)
    return RecommendResponse(
        options=[RouteOption(**o) for o in result["options"]],
        naive=RouteOption(**result["naive"]) if result["naive"] else None,
    )


@app.post("/inject-anomaly", response_model=AnomalyResponse)
def inject_anomaly(req: InjectAnomalyRequest):
    """Inject a demo disruption at a stop."""
    anomaly = state.inject_anomaly(req.stop_id, req.severity, req.anomaly_type)
    return AnomalyResponse(status="injected", anomaly=anomaly)


@app.post("/clear-anomalies", response_model=AnomalyResponse)
def clear_anomalies():
    """Clear all active anomalies."""
    n = state.clear_anomalies()
    return AnomalyResponse(status="cleared", cleared_count=n)

@app.get("/reachable-stops", response_model=list[StopInfo])
def get_reachable_stops(origin: str):
    """Return all stops reachable from the origin within 2 transfers."""
    reachable_ids = network.get_reachable_stops(origin, max_transfers=2)
    return [
        StopInfo(stop_id=sid, name=network.get_stop_name(sid))
        for sid in reachable_ids
    ]

