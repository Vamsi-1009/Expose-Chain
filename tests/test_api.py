"""Tests for FastAPI routes using an in-memory database."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.connection import Base, get_db
from src.main import create_app


@pytest.fixture
def client():
    """Create a test client with a fresh in-memory SQLite database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestScansEndpoints:
    def test_list_scans_empty(self, client):
        resp = client.get("/api/v1/scans")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["scans"] == []

    @patch("src.api.routes._run_source_scan", return_value=[])
    def test_trigger_scan(self, mock_scan, client):
        resp = client.post("/api/v1/scans", json={"sources": ["kubernetes"]})
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "completed"
        assert data["source"] == "kubernetes"

    @patch("src.api.routes._run_source_scan", return_value=[])
    def test_get_scan_by_id(self, mock_scan, client):
        create_resp = client.post("/api/v1/scans", json={"sources": ["kubernetes"]})
        scan_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/scans/{scan_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == scan_id

    def test_get_scan_not_found(self, client):
        resp = client.get("/api/v1/scans/nonexistent-id")
        assert resp.status_code == 404


class TestExposuresEndpoints:
    def test_list_exposures_empty(self, client):
        resp = client.get("/api/v1/exposures")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_get_exposure_not_found(self, client):
        resp = client.get("/api/v1/exposures/no-such-id")
        assert resp.status_code == 404


class TestChainsEndpoint:
    def test_chains_empty(self, client):
        resp = client.get("/api/v1/chains")
        assert resp.status_code == 200
        data = resp.json()
        assert data["chains"] == []


class TestRiskEndpoint:
    def test_risk_summary_empty(self, client):
        resp = client.get("/api/v1/risk/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_exposures"] == 0
