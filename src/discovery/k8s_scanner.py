"""Kubernetes cluster scanner for discovering exposed services."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class K8sExposure:
    """Raw exposure data discovered from a Kubernetes cluster."""

    domain: str | None = None
    ip_address: str | None = None
    port: int | None = None
    protocol: str = "TCP"
    namespace: str = ""
    service_name: str = ""
    service_type: str = ""
    ingress_name: str | None = None
    pod_selector: dict[str, str] | None = None
    tls_enabled: bool = False
    tls_hosts: list[str] = field(default_factory=list)
    annotations: dict[str, str] = field(default_factory=dict)
    environment: str | None = None
    owner_team: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


class KubernetesScanner:
    """Scans a Kubernetes cluster for publicly exposed services and ingresses."""

    def __init__(self):
        self._load_config()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    def _load_config(self):
        """Load kubeconfig based on application settings."""
        if settings.k8s_in_cluster:
            config.load_incluster_config()
        else:
            config.load_kube_config(
                config_file=settings.k8s_kubeconfig,
                context=settings.k8s_context,
            )

    def scan_all(self) -> list[K8sExposure]:
        """Run a full scan: services + ingresses across all namespaces."""
        exposures: list[K8sExposure] = []
        exposures.extend(self._scan_services())
        exposures.extend(self._scan_ingresses())
        logger.info("K8s scan complete: found %d exposures", len(exposures))
        return exposures

    # ------------------------------------------------------------------
    # Service scanning
    # ------------------------------------------------------------------

    def _scan_services(self) -> list[K8sExposure]:
        """Discover LoadBalancer and NodePort services."""
        exposures: list[K8sExposure] = []
        try:
            services = self.core_v1.list_service_for_all_namespaces()
        except ApiException as exc:
            logger.error("Failed to list services: %s", exc)
            return exposures

        for svc in services.items:
            svc_type = svc.spec.type
            if svc_type not in ("LoadBalancer", "NodePort"):
                continue

            annotations = dict(svc.metadata.annotations or {})
            owner = annotations.get("owner", annotations.get("team"))
            env = annotations.get("environment", self._guess_env(svc.metadata.namespace))

            for port_spec in svc.spec.ports or []:
                ip = self._get_external_ip(svc)
                exposures.append(
                    K8sExposure(
                        ip_address=ip,
                        port=port_spec.port,
                        protocol=port_spec.protocol or "TCP",
                        namespace=svc.metadata.namespace,
                        service_name=svc.metadata.name,
                        service_type=svc_type,
                        pod_selector=dict(svc.spec.selector or {}),
                        annotations=annotations,
                        environment=env,
                        owner_team=owner,
                        raw_data={"kind": "Service", "name": svc.metadata.name},
                    )
                )
        return exposures

    def _get_external_ip(self, svc) -> str | None:
        """Extract the external IP or hostname from a service."""
        if svc.spec.type == "LoadBalancer" and svc.status.load_balancer.ingress:
            ing = svc.status.load_balancer.ingress[0]
            return ing.ip or ing.hostname
        if svc.spec.external_i_ps:
            return svc.spec.external_i_ps[0]
        return None

    # ------------------------------------------------------------------
    # Ingress scanning
    # ------------------------------------------------------------------

    def _scan_ingresses(self) -> list[K8sExposure]:
        """Discover Ingress resources and their rules."""
        exposures: list[K8sExposure] = []
        try:
            ingresses = self.networking_v1.list_ingress_for_all_namespaces()
        except ApiException as exc:
            logger.error("Failed to list ingresses: %s", exc)
            return exposures

        for ing in ingresses.items:
            annotations = dict(ing.metadata.annotations or {})
            owner = annotations.get("owner", annotations.get("team"))
            env = annotations.get("environment", self._guess_env(ing.metadata.namespace))

            tls_hosts: list[str] = []
            if ing.spec.tls:
                for tls_block in ing.spec.tls:
                    tls_hosts.extend(tls_block.hosts or [])

            for rule in ing.spec.rules or []:
                host = rule.host
                for path in (rule.http.paths if rule.http else []):
                    backend_svc = path.backend.service
                    port = (
                        backend_svc.port.number
                        if backend_svc and backend_svc.port
                        else None
                    )
                    exposures.append(
                        K8sExposure(
                            domain=host,
                            port=port,
                            namespace=ing.metadata.namespace,
                            service_name=backend_svc.name if backend_svc else "",
                            service_type="Ingress",
                            ingress_name=ing.metadata.name,
                            tls_enabled=host in tls_hosts if host else False,
                            tls_hosts=tls_hosts,
                            annotations=annotations,
                            environment=env,
                            owner_team=owner,
                            raw_data={"kind": "Ingress", "name": ing.metadata.name},
                        )
                    )
        return exposures

    @staticmethod
    def _guess_env(namespace: str) -> str:
        """Heuristically guess the environment from a namespace name."""
        ns = namespace.lower()
        if "prod" in ns:
            return "production"
        if "stag" in ns:
            return "staging"
        if "dev" in ns:
            return "development"
        return "unknown"
