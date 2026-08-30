"""
schemas.py — Pydantic request/response models for the FastAPI endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request models ───────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    origin: str = Field(..., examples=["S01"])
    destination: str = Field(..., examples=["S07"])
    target_time: str = Field(
        ...,
        description="ISO-8601 datetime string",
        examples=["2025-07-15T08:30:00"],
    )


class InjectAnomalyRequest(BaseModel):
    stop_id: str = Field(..., examples=["S04"])
    severity: float = Field(
        ...,
        ge=0.0,
        le=5.0,
        examples=[0.8],
        description="Disruption severity (0–5 scale).",
    )
    anomaly_type: str = Field(
        default="general",
        examples=["rainy", "stormy", "snowy", "breakdown"],
        description="Type of the disruption",
    )


# ── Response models ──────────────────────────────────────────────────────────

class StopInfo(BaseModel):
    stop_id: str
    name: str
    lat: float | None = None
    lon: float | None = None


class RouteInfo(BaseModel):
    route_id: str
    stops: list[str]


class StopCrowding(BaseModel):
    stop_id: str
    name: str
    crowding: float
    tier: str
    delay: float


class RouteOption(BaseModel):
    type: str                                     # "direct" | "transfer" | "transfer_2"
    route: str | None = None                      # for direct
    first_route: str | None = None                # for transfer / transfer_2
    interchange: str | None = None                # for transfer
    interchange1: str | None = None               # for transfer_2
    second_route: str | None = None               # for transfer / transfer_2
    interchange2: str | None = None               # for transfer_2
    third_route: str | None = None                # for transfer_2
    path_label: str | None = None                 # for multi
    stops: list[str]
    departure_time: str
    score: float
    avg_crowding: float
    avg_delay: float
    crowding_tier: str


class RecommendResponse(BaseModel):
    options: list[RouteOption]
    naive: RouteOption | None


class AnomalyResponse(BaseModel):
    status: str
    anomaly: dict | None = None
    cleared_count: int | None = None
