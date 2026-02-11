"""Tests for database models."""

import pytest

from src.database.models import ScanRecord, Exposure, ChainNode


class TestModels:
    def test_create_scan_record(self, db_session):
        scan = ScanRecord(source="kubernetes", status="running")
        db_session.add(scan)
        db_session.commit()

        result = db_session.query(ScanRecord).first()
        assert result is not None
        assert result.source == "kubernetes"
        assert result.status == "running"
        assert result.id is not None

    def test_create_exposure(self, db_session):
        scan = ScanRecord(source="test", status="completed")
        db_session.add(scan)
        db_session.commit()

        exposure = Exposure(
            scan_id=scan.id,
            domain="test.example.com",
            port=443,
            protocol="TCP",
            namespace="production",
            service_name="web-svc",
            service_type="LoadBalancer",
            risk_score=7.5,
            tls_enabled=True,
            environment="production",
        )
        db_session.add(exposure)
        db_session.commit()

        result = db_session.query(Exposure).first()
        assert result.domain == "test.example.com"
        assert result.risk_score == 7.5
        assert result.tls_enabled is True

    def test_scan_exposure_relationship(self, db_session):
        scan = ScanRecord(source="kubernetes", status="completed")
        db_session.add(scan)
        db_session.commit()

        e1 = Exposure(scan_id=scan.id, domain="a.com", risk_score=5.0)
        e2 = Exposure(scan_id=scan.id, domain="b.com", risk_score=8.0)
        db_session.add_all([e1, e2])
        db_session.commit()

        result = db_session.query(ScanRecord).first()
        assert len(result.exposures) == 2

    def test_create_chain_node(self, db_session):
        scan = ScanRecord(source="test", status="completed")
        db_session.add(scan)
        db_session.commit()

        exposure = Exposure(scan_id=scan.id, domain="chain.test", risk_score=3.0)
        db_session.add(exposure)
        db_session.commit()

        node = ChainNode(
            exposure_id=exposure.id,
            node_type="domain",
            name="chain.test",
        )
        db_session.add(node)
        db_session.commit()

        result = db_session.query(ChainNode).first()
        assert result.node_type == "domain"
        assert result.name == "chain.test"

    def test_chain_node_parent_child(self, db_session):
        scan = ScanRecord(source="test", status="completed")
        db_session.add(scan)
        db_session.commit()

        exp = Exposure(scan_id=scan.id, domain="pc.test", risk_score=1.0)
        db_session.add(exp)
        db_session.commit()

        parent = ChainNode(exposure_id=exp.id, node_type="domain", name="pc.test")
        db_session.add(parent)
        db_session.commit()

        child = ChainNode(
            exposure_id=exp.id,
            node_type="service",
            name="web-svc",
            parent_id=parent.id,
        )
        db_session.add(child)
        db_session.commit()

        parent_result = db_session.query(ChainNode).filter_by(node_type="domain").first()
        assert len(parent_result.children) == 1
        assert parent_result.children[0].name == "web-svc"
