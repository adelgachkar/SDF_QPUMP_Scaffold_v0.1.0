"""Universal Directed Acyclic Graph (DAG) pipeline engine for SDF_QPUMP."""

from collections import deque
from typing import Any, Dict, List, Tuple


class NodeDict(dict):
    """Dictionary supporting mapping, len, membership, and callable access."""
    def __call__(self):
        return list(self.values())


class Graph:
    def __init__(self, name: str = "default_graph"):
        self.name = name
        self.nodes = NodeDict()
        self.edges: List[Tuple[str, str, str, str]] = []  # (src_name, src_port, dst_name, dst_port)

    def add_node(self, node: Any) -> Any:
        # Resolve node name: support node_id, name, or raw string/object
        name = getattr(node, "node_id", None) or getattr(node, "name", None) or str(node)
        if name in self.nodes:
            raise ValueError(f"duplicate node detected: '{name}'")
        self.nodes[name] = node
        return node

    def connect(self, src: str, src_port: str, dst: str, dst_port: str) -> None:
        if src not in self.nodes:
            raise KeyError(f"Source node '{src}' does not exist.")
        if dst not in self.nodes:
            raise KeyError(f"Destination node '{dst}' does not exist.")
        self.edges.append((src, src_port, dst, dst_port))

    def add_edge(self, src: str, src_port: str, dst: str, dst_port: str) -> None:
        """Alias for connect to support multi-phase pipeline tests."""
        self.connect(src, src_port, dst, dst_port)

    def _order(self) -> List[str]:
        """Kahn's topological sort algorithm checking for acyclicity."""
        in_degree = {name: 0 for name in self.nodes}
        adj = {name: [] for name in self.nodes}

        for src, _, dst, _ in self.edges:
            adj[src].append(dst)
            in_degree[dst] = in_degree.get(dst, 0) + 1

        queue = deque([n for n, deg in in_degree.items() if deg == 0])
        ordered = []

        while queue:
            curr = queue.popleft()
            ordered.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) != len(self.nodes):
            raise ValueError("cycle detected in computational graph")

        return ordered

    def run(self, initial_inputs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Dict[str, Any]]:
        initial_inputs = initial_inputs or {}
        ordered_names = self._order()

        node_inputs: Dict[str, Dict[str, Any]] = {
            name: dict(initial_inputs.get(name, {})) for name in self.nodes
        }
        node_outputs: Dict[str, Dict[str, Any]] = {}

        for name in ordered_names:
            node = self.nodes[name]
            current_in = node_inputs[name]

            if hasattr(node, "compute"):
                out = node.compute(current_in)
            elif callable(node):
                out = node(current_in)
            else:
                out = {}

            node_outputs[name] = out or {}

            # Route edge outputs to target inputs
            for src, src_p, dst, dst_p in self.edges:
                if src == name:
                    if src_p not in node_outputs[name]:
                        raise KeyError(f"missing output port '{src_p}' from node '{src}'")
                    node_inputs[dst][dst_p] = node_outputs[name][src_p]

        return node_outputs

    def execute(self, initial_inputs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Dict[str, Any]]:
        """Alias for run method."""
        return self.run(initial_inputs)


class ComputationalGraph(Graph):
    """Alias/subclass for ComputationalGraph used across test suites."""
    pass
