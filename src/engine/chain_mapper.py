"""Exposure chain mapper that builds a DAG of Domain -> LB -> Ingress -> Service -> Pod."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class ChainNodeData:
    """Data associated with a node in the exposure chain."""

    node_id: str
    node_type: str  # domain, load_balancer, ingress, service, pod
    name: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ChainMapper:
    """Builds and queries a Directed Acyclic Graph representing exposure chains.

    Chain flow: Domain -> Load Balancer -> Ingress -> Service -> Pod
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: ChainNodeData) -> None:
        """Add a node to the chain graph."""
        self.graph.add_node(
            node.node_id,
            node_type=node.node_type,
            name=node.name,
            metadata=node.metadata,
        )

    def add_edge(self, parent_id: str, child_id: str, **attrs) -> None:
        """Add a directed edge from parent to child."""
        self.graph.add_edge(parent_id, child_id, **attrs)

    def build_chain_from_exposure(self, exposure_data: dict[str, Any]) -> list[ChainNodeData]:
        """Build a chain of nodes from a single exposure record.

        Returns the list of ChainNodeData objects created.
        """
        nodes: list[ChainNodeData] = []
        parent_id: str | None = None

        # 1. Domain node
        domain = exposure_data.get("domain")
        if domain:
            node = ChainNodeData(
                node_id=f"domain:{domain}",
                node_type="domain",
                name=domain,
            )
            self._add_and_link(node, parent_id)
            nodes.append(node)
            parent_id = node.node_id

        # 2. Load Balancer / External IP node
        ip = exposure_data.get("ip_address")
        cloud_type = exposure_data.get("cloud_resource_type", "")
        if ip or cloud_type in ("elbv2", "elb"):
            lb_name = ip or exposure_data.get("cloud_resource_id", "unknown-lb")
            node = ChainNodeData(
                node_id=f"lb:{lb_name}",
                node_type="load_balancer",
                name=lb_name,
                metadata={"ip": ip, "cloud_resource_id": exposure_data.get("cloud_resource_id")},
            )
            self._add_and_link(node, parent_id)
            nodes.append(node)
            parent_id = node.node_id

        # 3. Ingress node
        ingress = exposure_data.get("ingress_name")
        ns = exposure_data.get("namespace", "")
        if ingress:
            node = ChainNodeData(
                node_id=f"ingress:{ns}/{ingress}",
                node_type="ingress",
                name=f"{ns}/{ingress}",
                metadata={"namespace": ns},
            )
            self._add_and_link(node, parent_id)
            nodes.append(node)
            parent_id = node.node_id

        # 4. Service node
        svc = exposure_data.get("service_name")
        if svc:
            node = ChainNodeData(
                node_id=f"service:{ns}/{svc}",
                node_type="service",
                name=f"{ns}/{svc}",
                metadata={
                    "namespace": ns,
                    "service_type": exposure_data.get("service_type"),
                    "port": exposure_data.get("port"),
                },
            )
            self._add_and_link(node, parent_id)
            nodes.append(node)
            parent_id = node.node_id

        # 5. Pod selector (represents potential pods)
        selector = exposure_data.get("pod_selector")
        if selector:
            selector_str = ",".join(f"{k}={v}" for k, v in sorted(selector.items()))
            node = ChainNodeData(
                node_id=f"pods:{ns}/{selector_str}",
                node_type="pod",
                name=selector_str,
                metadata={"namespace": ns, "selector": selector},
            )
            self._add_and_link(node, parent_id)
            nodes.append(node)

        return nodes

    def _add_and_link(self, node: ChainNodeData, parent_id: str | None) -> None:
        """Add a node and optionally link it to its parent."""
        self.add_node(node)
        if parent_id:
            self.add_edge(parent_id, node.node_id)

    def get_full_chains(self) -> list[list[dict[str, Any]]]:
        """Return all root-to-leaf paths as chains."""
        roots = [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]
        leaves = [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]

        chains: list[list[dict[str, Any]]] = []
        for root in roots:
            for leaf in leaves:
                for path in nx.all_simple_paths(self.graph, root, leaf):
                    chain = [
                        {
                            "node_id": nid,
                            **self.graph.nodes[nid],
                        }
                        for nid in path
                    ]
                    chains.append(chain)
        return chains

    def get_chain_for_domain(self, domain: str) -> list[list[dict[str, Any]]]:
        """Return all chains originating from a specific domain."""
        node_id = f"domain:{domain}"
        if node_id not in self.graph:
            return []

        leaves = [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]
        chains: list[list[dict[str, Any]]] = []
        for leaf in leaves:
            for path in nx.all_simple_paths(self.graph, node_id, leaf):
                chain = [{"node_id": nid, **self.graph.nodes[nid]} for nid in path]
                chains.append(chain)
        return chains

    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph to a JSON-compatible dict."""
        return {
            "nodes": [
                {"node_id": nid, **data}
                for nid, data in self.graph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **data}
                for u, v, data in self.graph.edges(data=True)
            ],
        }

    def stats(self) -> dict[str, int]:
        """Return basic statistics about the chain graph."""
        type_counts: dict[str, int] = {}
        for _, data in self.graph.nodes(data=True):
            t = data.get("node_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            **type_counts,
        }
