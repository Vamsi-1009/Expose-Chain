"""Tests for the exposure chain mapper."""

import pytest

from src.engine.chain_mapper import ChainMapper, ChainNodeData


@pytest.fixture
def mapper():
    return ChainMapper()


class TestChainMapper:
    def test_add_node(self, mapper):
        node = ChainNodeData(node_id="test:1", node_type="domain", name="example.com")
        mapper.add_node(node)
        assert mapper.graph.number_of_nodes() == 1

    def test_add_edge(self, mapper):
        n1 = ChainNodeData(node_id="domain:a", node_type="domain", name="a.com")
        n2 = ChainNodeData(node_id="service:b", node_type="service", name="svc-b")
        mapper.add_node(n1)
        mapper.add_node(n2)
        mapper.add_edge("domain:a", "service:b")
        assert mapper.graph.number_of_edges() == 1

    def test_build_chain_from_full_exposure(self, mapper):
        exposure = {
            "domain": "app.example.com",
            "ip_address": "10.0.0.1",
            "namespace": "production",
            "ingress_name": "app-ingress",
            "service_name": "app-service",
            "service_type": "Ingress",
            "port": 443,
            "pod_selector": {"app": "my-app"},
        }
        nodes = mapper.build_chain_from_exposure(exposure)
        assert len(nodes) == 5  # domain, lb, ingress, service, pod

    def test_build_chain_service_only(self, mapper):
        exposure = {
            "namespace": "default",
            "service_name": "redis",
            "service_type": "LoadBalancer",
            "ip_address": "34.1.2.3",
            "port": 6379,
        }
        nodes = mapper.build_chain_from_exposure(exposure)
        assert len(nodes) >= 2  # lb + service

    def test_get_full_chains(self, mapper):
        exposure = {
            "domain": "web.example.com",
            "ip_address": "10.0.0.5",
            "namespace": "default",
            "ingress_name": "web-ing",
            "service_name": "web-svc",
            "service_type": "Ingress",
            "port": 80,
            "pod_selector": {"app": "web"},
        }
        mapper.build_chain_from_exposure(exposure)
        chains = mapper.get_full_chains()
        assert len(chains) >= 1
        assert chains[0][0]["node_type"] == "domain"

    def test_get_chain_for_domain(self, mapper):
        mapper.build_chain_from_exposure({
            "domain": "api.example.com",
            "namespace": "prod",
            "service_name": "api-svc",
            "service_type": "Ingress",
            "ingress_name": "api-ing",
        })
        chains = mapper.get_chain_for_domain("api.example.com")
        assert len(chains) >= 1

    def test_get_chain_for_missing_domain(self, mapper):
        chains = mapper.get_chain_for_domain("nonexistent.com")
        assert chains == []

    def test_to_dict(self, mapper):
        mapper.build_chain_from_exposure({
            "domain": "x.com",
            "namespace": "ns",
            "service_name": "svc",
        })
        result = mapper.to_dict()
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) > 0

    def test_stats(self, mapper):
        mapper.build_chain_from_exposure({
            "domain": "y.com",
            "ip_address": "1.2.3.4",
            "namespace": "ns",
            "service_name": "svc",
            "pod_selector": {"app": "test"},
        })
        stats = mapper.stats()
        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0
        assert "domain" in stats
