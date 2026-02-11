"""Tests for the risk scoring engine."""

import pytest

from src.engine.risk_scorer import RiskScorer, RiskResult


@pytest.fixture
def scorer():
    return RiskScorer()


class TestRiskScorer:
    def test_score_returns_risk_result(self, scorer):
        result = scorer.score()
        assert isinstance(result, RiskResult)
        assert 0.0 <= result.score <= 10.0

    def test_production_env_scores_higher(self, scorer):
        prod = scorer.score(environment="production")
        dev = scorer.score(environment="development")
        assert prod.score > dev.score

    def test_tls_enabled_reduces_risk(self, scorer):
        no_tls = scorer.score(tls_enabled=False)
        with_tls = scorer.score(tls_enabled=True)
        assert with_tls.score < no_tls.score

    def test_http_protocol_higher_risk_than_https(self, scorer):
        http = scorer.score(protocol="HTTP")
        https = scorer.score(protocol="HTTPS")
        assert http.score > https.score

    def test_high_risk_port(self, scorer):
        ssh = scorer.score(port=22)
        web = scorer.score(port=443)
        assert ssh.score > web.score

    def test_load_balancer_higher_risk_than_clusterip(self, scorer):
        lb = scorer.score(service_type="LoadBalancer")
        cip = scorer.score(service_type="ClusterIP")
        assert lb.score > cip.score

    def test_auth_annotations_reduce_risk(self, scorer):
        no_auth = scorer.score(annotations={})
        with_auth = scorer.score(
            annotations={"nginx.ingress.kubernetes.io/auth-url": "https://auth.example.com"}
        )
        assert with_auth.score < no_auth.score

    def test_severity_levels(self, scorer):
        critical = RiskResult(score=9.0)
        assert critical.severity == "critical"

        high = RiskResult(score=7.0)
        assert high.severity == "high"

        medium = RiskResult(score=5.0)
        assert medium.severity == "medium"

        low = RiskResult(score=3.0)
        assert low.severity == "low"

        info = RiskResult(score=1.0)
        assert info.severity == "info"

    def test_score_capped_at_10(self, scorer):
        result = scorer.score(
            environment="production",
            protocol="HTTP",
            tls_enabled=False,
            port=22,
            service_type="LoadBalancer",
        )
        assert result.score <= 10.0

    def test_factors_contain_all_dimensions(self, scorer):
        result = scorer.score()
        expected_keys = {"environment", "protocol", "authentication", "tls", "port", "service_type"}
        assert set(result.factors.keys()) == expected_keys
