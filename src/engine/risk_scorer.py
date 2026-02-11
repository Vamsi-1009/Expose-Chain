"""Risk scoring engine that evaluates exposure severity."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Weights for each risk dimension (must sum to 1.0)
_WEIGHTS = {
    "environment": 0.25,
    "protocol": 0.20,
    "authentication": 0.20,
    "tls": 0.15,
    "port": 0.10,
    "service_type": 0.10,
}


@dataclass
class RiskResult:
    """Output of the risk scoring engine."""

    score: float  # 0.0 (safe) – 10.0 (critical)
    factors: dict[str, float] = field(default_factory=dict)
    details: dict[str, str] = field(default_factory=dict)

    @property
    def severity(self) -> str:
        if self.score >= 8.0:
            return "critical"
        if self.score >= 6.0:
            return "high"
        if self.score >= 4.0:
            return "medium"
        if self.score >= 2.0:
            return "low"
        return "info"


class RiskScorer:
    """Algorithmic risk assessment based on environment, auth, protocol, etc."""

    # ---- Environment risk (production > staging > dev > unknown) ----------
    _ENV_SCORES: dict[str, float] = {
        "production": 10.0,
        "staging": 6.0,
        "development": 3.0,
        "unknown": 5.0,
    }

    # ---- Risky ports -------------------------------------------------------
    _HIGH_RISK_PORTS = {22, 3389, 5432, 3306, 6379, 27017, 9200, 8080, 8443}
    _STANDARD_WEB_PORTS = {80, 443}

    # ---- Service type risk -------------------------------------------------
    _SERVICE_TYPE_SCORES: dict[str, float] = {
        "LoadBalancer": 8.0,
        "NodePort": 7.0,
        "Ingress": 6.0,
        "ClusterIP": 2.0,
    }

    def score(
        self,
        environment: str | None = None,
        protocol: str | None = None,
        tls_enabled: bool = False,
        port: int | None = None,
        service_type: str | None = None,
        annotations: dict[str, str] | None = None,
    ) -> RiskResult:
        """Calculate a composite risk score for an exposure."""
        factors: dict[str, float] = {}
        details: dict[str, str] = {}

        # 1. Environment
        env = (environment or "unknown").lower()
        factors["environment"] = self._ENV_SCORES.get(env, 5.0)
        details["environment"] = env

        # 2. Protocol
        proto = (protocol or "TCP").upper()
        if proto in ("HTTPS", "TLS"):
            factors["protocol"] = 2.0
        elif proto in ("HTTP",):
            factors["protocol"] = 8.0
        else:
            factors["protocol"] = 5.0
        details["protocol"] = proto

        # 3. Authentication (heuristic from annotations)
        auth_score = self._evaluate_auth(annotations or {})
        factors["authentication"] = auth_score
        details["authentication"] = "present" if auth_score < 5.0 else "missing"

        # 4. TLS
        factors["tls"] = 2.0 if tls_enabled else 9.0
        details["tls"] = "enabled" if tls_enabled else "disabled"

        # 5. Port
        if port in self._HIGH_RISK_PORTS:
            factors["port"] = 9.0
            details["port"] = f"{port} (high-risk)"
        elif port in self._STANDARD_WEB_PORTS:
            factors["port"] = 4.0
            details["port"] = f"{port} (standard web)"
        else:
            factors["port"] = 5.0
            details["port"] = str(port) if port else "unknown"

        # 6. Service type
        st = service_type or ""
        factors["service_type"] = self._SERVICE_TYPE_SCORES.get(st, 5.0)
        details["service_type"] = st or "unknown"

        # Weighted composite
        total = sum(factors[k] * _WEIGHTS[k] for k in _WEIGHTS)
        total = round(min(max(total, 0.0), 10.0), 2)

        return RiskResult(score=total, factors=factors, details=details)

    @staticmethod
    def _evaluate_auth(annotations: dict[str, str]) -> float:
        """Check annotations for signs of authentication being configured."""
        auth_indicators = [
            "nginx.ingress.kubernetes.io/auth-url",
            "nginx.ingress.kubernetes.io/auth-signin",
            "nginx.ingress.kubernetes.io/auth-type",
            "auth",
            "authentication",
            "oauth",
        ]
        for key in annotations:
            if any(indicator in key.lower() for indicator in auth_indicators):
                return 2.0
        return 8.0
