"""Response models for the PathSnap API. This file is the machine-readable form of docs/API_CONTRACT.md.

Contract version 1.0. Change it only together with the UI owner and bump CONTRACT_VERSION.
Coordinates are always [lat, lon] (Leaflet order).
"""
from __future__ import annotations

from pydantic import BaseModel, Field

CONTRACT_VERSION = "1.0"


class Health(BaseModel):
    status: str = "ok"
    contract_version: str = CONTRACT_VERSION
    model: str
    version: str = Field(description="git short hash of the running code")


class TripSummary(BaseModel):
    trip_id: str
    n_points: int


class Route(BaseModel):
    arc_ids: list[int] = Field(description="predicted arcs in order, consecutive repeats removed")
    segments: list[list[list[float]]] = Field(
        description="connected polylines, each a list of [lat, lon]; a break between segments is a disconnected jump")


class RouteMetrics(BaseModel):
    top1_accuracy: float
    route_continuity: float
    route_arc_f1: float


class Metrics(RouteMetrics):
    """HMM metrics; the classifier-only baseline sits alongside for the before/after view."""
    n_points: int
    n_scored_points: int = Field(description="points that had at least one candidate arc")
    candidate_miss_rate: float
    classifier_only: RouteMetrics


class PerPoint(BaseModel):
    hmm_arc: list[int] = Field(description="one entry per GPS point; -1 = no candidate")
    classifier_arc: list[int]


class Timing(BaseModel):
    seconds: float
    candidates_s: float | None = None
    features_s: float | None = None
    classifier_s: float | None = None
    hmm_s: float | None = None


class ModelInfo(BaseModel):
    name: str
    version: str


class PredictResponse(BaseModel):
    contract_version: str = CONTRACT_VERSION
    trip_id: str
    n_points: int
    gps: list[list[float]] = Field(description="[lat, lon, t_seconds] per point, in order")
    classifier_route: Route
    hmm_route: Route
    per_point: PerPoint
    metrics: Metrics
    timing: Timing
    model: ModelInfo
    warnings: list[str] = []
    mock: bool = Field(default=False, description="true only in ui/mock example files")


class ErrorResponse(BaseModel):
    detail: str
    code: str = Field(description="UNKNOWN_TRIP | PIPELINE_ERROR | BAD_REQUEST")
