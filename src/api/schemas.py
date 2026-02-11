"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Exposure schemas ─────────────────────────────────────────────────────────

class ExposureBase(BaseModel):
    domain: str | None = None
    ip_address: str | None = None
    port: int | None = None
    protocol: str = "TCP"
    namespace: str | None = None
    service_name: str | None = None
    service_type: str | None = None
    ingress_name: str | None = None
    cloud_provider: str | None = None
    cloud_resource_id: str | None = None
    cloud_resource_type: str | None = None
    environment: str | None = None
    owner_team: str | None = None
    owner_contact: str | None = None
    tls_enabled: bool = False


class ExposureResponse(ExposureBase):
    id: str
    scan_id: str
    discovered_at: datetime
    risk_score: float
    risk_factors: dict[str, Any] | None = None
    pod_selector: dict[str, str] | None = None
    annotations: dict[str, str] | None = None

    model_config = {"from_attributes": True}


class ExposureListResponse(BaseModel):
    total: int
    exposures: list[ExposureResponse]


# ── Scan schemas ─────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    sources: list[str] = Field(
        default=["kubernetes"],
        description="Data sources to scan: kubernetes, aws",
    )


class ScanResponse(BaseModel):
    id: str
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    source: str
    summary: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class ScanListResponse(BaseModel):
    total: int
    scans: list[ScanResponse]


# ── Chain schemas ────────────────────────────────────────────────────────────

class ChainNodeResponse(BaseModel):
    node_id: str
    node_type: str
    name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChainResponse(BaseModel):
    chains: list[list[ChainNodeResponse]]
    stats: dict[str, int]


# ── Risk schemas ─────────────────────────────────────────────────────────────

class RiskSummary(BaseModel):
    total_exposures: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    average_score: float = 0.0


# ── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    database: str = "connected"
