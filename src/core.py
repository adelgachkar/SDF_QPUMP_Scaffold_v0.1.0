"""
Core DAG orchestration and execution engine for QPUMP.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Edge:
    src_node: str
    src_port: str
    dst_node: str
    dst_port: str


class Graph:
    def __init__(self, name: Optional[str] = None):
        self.name = name or "Graph"
        self.nodes: Dict[str, Any] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Any) -> None:
        node_id = getattr(node, "node_id", getattr(node, "name", None))
        if node_id is None:
            raise ValueError("Node must have node_id or name")
        if node_id in self.nodes:
            raise ValueError(f"duplicate node: {node_id}")
        self.nodes[node_id] = node

    def connect(self, src_id: str, src_port: str, dst_id: str, dst_port: str) -> None:
        if src_id not in self.nodes:
            raise KeyError(f"source node not found: {src_id}")
        if dst_id not in self.nodes:
            raise KeyError(f"target node not found: {dst_id}")

        src_node = self.nodes[src_id]
        if hasattr(src_node, "output_ports") and src_port not in src_node.output_ports:
            raise KeyError(f"missing output port '{src_port}' on node '{src_id}'")

        dst_node = self.nodes[dst_id]
        if hasattr(dst_node, "input_ports") and dst_port not in dst_node.input_ports:
            raise KeyError(f"missing input port '{dst_port}' on node '{dst_id}'")

        self.edges.append(Edge(src_id, src_port, dst_id, dst_port))

    def add_edge(self, src_id: str, src_port: str, dst_id: str, dst_port: str) -> None:
        """Alias for connect() matching test suite interface."""
        self.connect(src_id, src_port, dst_id, dst_port)

    def _order(self) -> List[str]:
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}

        for edge in self.edges:
            adj[edge.src_node].append(edge.dst_node)
            in_degree[edge.dst_node] += 1

        queue = [nid for nid in sorted(self.nodes.keys()) if in_degree[nid] == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in sorted(adj[curr]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) < len(self.nodes):
            raise ValueError("cycle detected in graph")

        return order

    def run(self, initial_inputs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Dict[str, Any]]:
        initial_inputs = initial_inputs or {}
        order = self._order()
        node_inputs: Dict[str, Dict[str, Any]] = {
            nid: dict(initial_inputs.get(nid, {})) for nid in self.nodes
        }
        node_outputs: Dict[str, Dict[str, Any]] = {}

        for nid in order:
            node = self.nodes[nid]
            curr_in = node_inputs[nid]
            if hasattr(node, "execute"):
                out = node.execute(curr_in)
            elif hasattr(node, "compute"):
                out = node.compute(curr_in)
            elif callable(node):
                out = node(curr_in)
            else:
                out = {}

            if not isinstance(out, dict):
                out = {"out": out}
            node_outputs[nid] = out

            for edge in self.edges:
                if edge.src_node == nid:
                    if edge.src_port not in out:
                        raise KeyError(f"missing output port '{edge.src_port}' from '{nid}'")
                    node_inputs[edge.dst_node][edge.dst_port] = out[edge.src_port]

        return node_outputs

    def execute(self, initial_inputs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Dict[str, Any]]:
        """Alias for run() matching test suite execution call."""
        return self.run(initial_inputs=initial_inputs)


NodeGraph = Graph
