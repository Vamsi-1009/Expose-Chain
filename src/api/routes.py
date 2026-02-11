"""FastAPI route definitions for ExposeChain API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.schemas import (
    ChainResponse,
    ChainNodeResponse,
    ExposureListResponse,
    ExposureResponse,
    HealthResponse,
    RiskSummary,
    ScanListResponse,
    ScanRequest,
    ScanResponse,
)
from src.config import settings
from src.database.connection import get_db
from src.database.models import Exposure, ScanRecord
from src.engine.chain_mapper import ChainMapper
from src.engine.risk_scorer import RiskScorer
from src.discovery.k8s_scanner import KubernetesScanner, K8sExposure
from src.discovery.cloud_scanner import AWSScanner, CloudExposure

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Health ───────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check(db: Session = Depends(get_db)):
    """Check application and database health."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database=db_status,
    )


# ── Scans ────────────────────────────────────────────────────────────────────

@router.post("/scans", response_model=ScanResponse, status_code=201, tags=["scans"])
def trigger_scan(body: ScanRequest, db: Session = Depends(get_db)):
    """Trigger a new infrastructure scan."""
    source_label = ",".join(body.sources)
    scan = ScanRecord(source=source_label, status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    scorer = RiskScorer()
    total_exposures = 0

    for source in body.sources:
        raw_exposures = _run_source_scan(source)
        for raw in raw_exposures:
            exposure = _create_exposure(raw, scan.id, scorer)
            db.add(exposure)
            total_exposures += 1

    scan.status = "completed"
    scan.finished_at = datetime.now(timezone.utc)
    scan.summary = {"total_exposures": total_exposures}
    db.commit()
    db.refresh(scan)
    return scan


@router.get("/scans", response_model=ScanListResponse, tags=["scans"])
def list_scans(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List all scan records."""
    total = db.query(ScanRecord).count()
    scans = (
        db.query(ScanRecord)
        .order_by(ScanRecord.started_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ScanListResponse(total=total, scans=scans)


@router.get("/scans/{scan_id}", response_model=ScanResponse, tags=["scans"])
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    """Get details of a specific scan."""
    scan = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


# ── Exposures ────────────────────────────────────────────────────────────────

@router.get("/exposures", response_model=ExposureListResponse, tags=["exposures"])
def list_exposures(
    namespace: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    min_risk: float = Query(default=0.0, ge=0.0, le=10.0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List discovered exposures with optional filters."""
    query = db.query(Exposure)
    if namespace:
        query = query.filter(Exposure.namespace == namespace)
    if environment:
        query = query.filter(Exposure.environment == environment)
    query = query.filter(Exposure.risk_score >= min_risk)

    total = query.count()
    exposures = (
        query.order_by(Exposure.risk_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ExposureListResponse(total=total, exposures=exposures)


@router.get("/exposures/{exposure_id}", response_model=ExposureResponse, tags=["exposures"])
def get_exposure(exposure_id: str, db: Session = Depends(get_db)):
    """Get details of a specific exposure."""
    exposure = db.query(Exposure).filter(Exposure.id == exposure_id).first()
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")
    return exposure


# ── Chain mapping ────────────────────────────────────────────────────────────

@router.get("/chains", response_model=ChainResponse, tags=["chains"])
def get_exposure_chains(
    domain: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Build and return exposure chain DAG."""
    exposures = db.query(Exposure).all()
    mapper = ChainMapper()

    for exp in exposures:
        mapper.build_chain_from_exposure(
            {
                "domain": exp.domain,
                "ip_address": exp.ip_address,
                "port": exp.port,
                "namespace": exp.namespace,
                "service_name": exp.service_name,
                "service_type": exp.service_type,
                "ingress_name": exp.ingress_name,
                "pod_selector": exp.pod_selector,
                "cloud_resource_id": exp.cloud_resource_id,
                "cloud_resource_type": exp.cloud_resource_type,
            }
        )

    if domain:
        chains = mapper.get_chain_for_domain(domain)
    else:
        chains = mapper.get_full_chains()

    chain_nodes = [
        [ChainNodeResponse(**node) for node in chain]
        for chain in chains
    ]
    return ChainResponse(chains=chain_nodes, stats=mapper.stats())


# ── Risk summary ─────────────────────────────────────────────────────────────

@router.get("/risk/summary", response_model=RiskSummary, tags=["risk"])
def risk_summary(db: Session = Depends(get_db)):
    """Get an aggregate risk summary across all exposures."""
    exposures = db.query(Exposure).all()
    if not exposures:
        return RiskSummary()

    summary = RiskSummary(total_exposures=len(exposures))
    total_score = 0.0
    for exp in exposures:
        total_score += exp.risk_score
        if exp.risk_score >= 8.0:
            summary.critical += 1
        elif exp.risk_score >= 6.0:
            summary.high += 1
        elif exp.risk_score >= 4.0:
            summary.medium += 1
        elif exp.risk_score >= 2.0:
            summary.low += 1
        else:
            summary.info += 1
    summary.average_score = round(total_score / len(exposures), 2)
    return summary


# ── Helpers ──────────────────────────────────────────────────────────────────

def _run_source_scan(source: str) -> list:
    """Run a scan for a specific source and return raw exposure objects."""
    if source == "kubernetes":
        try:
            scanner = KubernetesScanner()
            return scanner.scan_all()
        except Exception as exc:
            logger.warning("Kubernetes scan skipped: %s", exc)
            return []
    elif source == "aws":
        try:
            scanner = AWSScanner()
            return scanner.scan_all()
        except Exception as exc:
            logger.warning("AWS scan skipped: %s", exc)
            return []
    else:
        logger.warning("Unknown scan source: %s", source)
        return []


def _create_exposure(raw, scan_id: str, scorer: RiskScorer) -> Exposure:
    """Convert a raw exposure dataclass to a database Exposure model."""
    if isinstance(raw, K8sExposure):
        risk = scorer.score(
            environment=raw.environment,
            protocol=raw.protocol,
            tls_enabled=raw.tls_enabled,
            port=raw.port,
            service_type=raw.service_type,
            annotations=raw.annotations,
        )
        return Exposure(
            scan_id=scan_id,
            domain=raw.domain,
            ip_address=raw.ip_address,
            port=raw.port,
            protocol=raw.protocol,
            namespace=raw.namespace,
            service_name=raw.service_name,
            service_type=raw.service_type,
            ingress_name=raw.ingress_name,
            pod_selector=raw.pod_selector,
            tls_enabled=raw.tls_enabled,
            environment=raw.environment,
            owner_team=raw.owner_team,
            annotations=raw.annotations,
            risk_score=risk.score,
            risk_factors=risk.factors,
            raw_data=raw.raw_data,
        )
    elif isinstance(raw, CloudExposure):
        risk = scorer.score(
            environment=raw.environment,
            protocol=raw.protocol,
            tls_enabled=raw.tls_enabled,
            port=raw.port,
        )
        return Exposure(
            scan_id=scan_id,
            domain=raw.domain,
            ip_address=raw.ip_address,
            port=raw.port,
            protocol=raw.protocol,
            cloud_provider=raw.cloud_provider,
            cloud_resource_id=raw.cloud_resource_id,
            cloud_resource_type=raw.cloud_resource_type,
            tls_enabled=raw.tls_enabled,
            environment=raw.environment,
            owner_team=raw.owner_team,
            annotations=raw.annotations,
            risk_score=risk.score,
            risk_factors=risk.factors,
            raw_data=raw.raw_data,
        )
    else:
        raise ValueError(f"Unknown exposure type: {type(raw)}")
