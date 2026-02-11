"""Standalone script to trigger a scan without the API server."""

import sys
import os
import logging

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings
from src.database.connection import SessionLocal, init_db
from src.database.models import ScanRecord, Exposure
from src.discovery.k8s_scanner import KubernetesScanner
from src.discovery.cloud_scanner import AWSScanner
from src.engine.risk_scorer import RiskScorer

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Run a scan and persist results to the database."""
    logger.info("Initializing database...")
    init_db()

    db = SessionLocal()
    scorer = RiskScorer()

    scan = ScanRecord(source="kubernetes,aws", status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    logger.info("Scan %s started", scan.id)

    total = 0

    # Kubernetes scan
    try:
        k8s = KubernetesScanner()
        for raw in k8s.scan_all():
            risk = scorer.score(
                environment=raw.environment,
                protocol=raw.protocol,
                tls_enabled=raw.tls_enabled,
                port=raw.port,
                service_type=raw.service_type,
                annotations=raw.annotations,
            )
            exposure = Exposure(
                scan_id=scan.id,
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
            db.add(exposure)
            total += 1
    except Exception as exc:
        logger.warning("Kubernetes scan skipped: %s", exc)

    # AWS scan
    try:
        aws = AWSScanner()
        for raw in aws.scan_all():
            risk = scorer.score(
                environment=raw.environment,
                protocol=raw.protocol,
                tls_enabled=raw.tls_enabled,
                port=raw.port,
            )
            exposure = Exposure(
                scan_id=scan.id,
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
            db.add(exposure)
            total += 1
    except Exception as exc:
        logger.warning("AWS scan skipped: %s", exc)

    from datetime import datetime, timezone

    scan.status = "completed"
    scan.finished_at = datetime.now(timezone.utc)
    scan.summary = {"total_exposures": total}
    db.commit()

    logger.info("Scan %s completed: %d exposures found", scan.id, total)
    db.close()


if __name__ == "__main__":
    main()
