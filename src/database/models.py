"""SQLAlchemy ORM models for ExposeChain."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from src.database.connection import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ScanRecord(Base):
    """Represents a single scanning run."""

    __tablename__ = "scan_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    started_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running", nullable=False)  # running, completed, failed
    source = Column(String(50), nullable=False)  # kubernetes, aws, manual
    summary = Column(JSON, nullable=True)

    exposures = relationship("Exposure", back_populates="scan", cascade="all, delete-orphan")


class Exposure(Base):
    """A discovered exposed service / entry-point."""

    __tablename__ = "exposures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scan_records.id"), nullable=False)
    discovered_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    # Identity
    domain = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)
    port = Column(Integer, nullable=True)
    protocol = Column(String(10), default="TCP")

    # Kubernetes metadata
    namespace = Column(String(255), nullable=True)
    service_name = Column(String(255), nullable=True)
    service_type = Column(String(50), nullable=True)  # LoadBalancer, NodePort, ClusterIP
    ingress_name = Column(String(255), nullable=True)
    pod_selector = Column(JSON, nullable=True)

    # Cloud metadata
    cloud_provider = Column(String(20), nullable=True)  # aws, gcp, azure
    cloud_resource_id = Column(String(512), nullable=True)
    cloud_resource_type = Column(String(100), nullable=True)

    # Risk
    risk_score = Column(Float, default=0.0)
    risk_factors = Column(JSON, nullable=True)

    # Ownership
    owner_team = Column(String(255), nullable=True)
    owner_contact = Column(String(255), nullable=True)
    environment = Column(String(50), nullable=True)  # production, staging, dev

    # TLS
    tls_enabled = Column(Boolean, default=False)
    tls_cert_expiry = Column(DateTime(timezone=True), nullable=True)

    # Extra
    annotations = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)

    scan = relationship("ScanRecord", back_populates="exposures")
    chain_nodes = relationship("ChainNode", back_populates="exposure", cascade="all, delete-orphan")


class ChainNode(Base):
    """A node in the exposure chain DAG (Domain -> LB -> Ingress -> Service -> Pod)."""

    __tablename__ = "chain_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exposure_id = Column(String(36), ForeignKey("exposures.id"), nullable=False)

    node_type = Column(String(50), nullable=False)  # domain, load_balancer, ingress, service, pod
    name = Column(String(512), nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)

    parent_id = Column(String(36), ForeignKey("chain_nodes.id"), nullable=True)

    exposure = relationship("Exposure", back_populates="chain_nodes")
    children = relationship(
        "ChainNode",
        back_populates="parent_ref",
        foreign_keys="ChainNode.parent_id",
    )
    parent_ref = relationship(
        "ChainNode",
        back_populates="children",
        remote_side="ChainNode.id",
        foreign_keys="ChainNode.parent_id",
    )
