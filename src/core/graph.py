<<<<<<< HEAD
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
=======
"""
Core Computational Graph and DAG representation for SDF_QPUMP Scaffold.
Supports directed acyclic graph operations, state routing, and pipeline execution.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import networkx as nx


@dataclass
class Edge:
    src_node: str
    src_port: str
    dst_node: str
    dst_port: str


class NodesContainer(dict):
    """Container supporting both dict operations (nodes[id], len(nodes)) and method calls (nodes())."""
    def __call__(self) -> List[str]:
        return list(self.keys())


class Graph:
    """Base Graph wrapper supporting both DAG execution and NetworkX graph operations."""

    def __init__(self, name: Optional[str] = "QuantumSDFGraph") -> None:
        self.name: str = name or "QuantumSDFGraph"
        self._graph: nx.DiGraph = nx.DiGraph()
        self.nodes: NodesContainer = NodesContainer()
        self.edges_list: List[Edge] = []

    @property
    def internal_graph(self) -> nx.DiGraph:
        """Returns the underlying NetworkX DiGraph."""
        return self._graph

    def add_node(self, node: Any, **attributes: Any) -> None:
        """Add a node object or node identifier string."""
        if isinstance(node, str):
            node_id = node
            node_obj = attributes.get("obj", node)
        else:
            node_id = None
            # Check explicit config / params / dict first (prioritizing explicit node_id)
            if hasattr(node, "config") and isinstance(node.config, dict):
                node_id = node.config.get("node_id")
            if not node_id and hasattr(node, "params") and isinstance(node.params, dict):
                node_id = node.params.get("node_id")
            if not node_id and hasattr(node, "__dict__"):
                node_id = node.__dict__.get("node_id")

            # Fallback to name or class default
            if not node_id:
                node_id = getattr(node, "name", None) or getattr(node, "node_id", None)

            node_obj = node

        if node_id is None:
            raise ValueError("Node must have node_id or name")

        if node_id in self.nodes:
            raise ValueError(f"duplicate node: {node_id}")

        self.nodes[node_id] = node_obj
        self._graph.add_node(node_id, **attributes)

    def connect(self, src_id: str, src_port: str, dst_id: str, dst_port: str) -> None:
        """Connect source node port to destination node port."""
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

        self.edges_list.append(Edge(src_id, src_port, dst_id, dst_port))
        self._graph.add_edge(src_id, dst_id)

    def add_edge(self, *args: Any, **kwargs: Any) -> None:
        """
        Supports both 4-argument port wiring: (src_id, src_port, dst_id, dst_port)
        and 2-argument topological edge: (src_id, dst_id).
        """
        if len(args) == 4:
            self.connect(args[0], args[1], args[2], args[3])
        elif len(args) == 2:
            src, dst = args[0], args[1]
            if src not in self.nodes:
                self.nodes[src] = src
            if dst not in self.nodes:
                self.nodes[dst] = dst
            self._graph.add_edge(src, dst, **kwargs)
        else:
            raise TypeError(f"add_edge() expects 2 or 4 arguments, got {len(args)}")

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Retrieve attributes of a given node."""
        if node_id not in self._graph and node_id not in self.nodes:
            raise KeyError(f"Node '{node_id}' does not exist in graph.")
        return dict(self._graph.nodes.get(node_id, {}))

    def edges(self) -> List[tuple]:
        """Return list of directed edges."""
        return list(self._graph.edges())

    def topological_sort(self) -> List[str]:
        """Return execution order of nodes respecting DAG constraints."""
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("Graph contains cycles; cannot perform topological sort.")
        return list(nx.topological_sort(self._graph))

    def _order(self) -> List[str]:
        """Topological sort using Kahn's algorithm over registered edges."""
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}

        for edge in self.edges_list:
            if edge.dst_node not in adj[edge.src_node]:
                adj[edge.src_node].append(edge.dst_node)
                in_degree[edge.dst_node] += 1

        queue = [nid for nid in sorted(self.nodes.keys()) if in_degree[nid] == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in sorted(adj[curr]):
>>>>>>> 3a73ed0b5bb0fe7d5691e8c8c09488d6f7a98b39
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

<<<<<<< HEAD
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
=======
        if len(order) < len(self.nodes):
            raise ValueError("cycle detected in graph")

        return order

    def run(self, initial_inputs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
        """Executes the computation graph sequentially."""
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

            for edge in self.edges_list:
                if edge.src_node == nid:
                    if edge.src_port not in out:
                        raise KeyError(f"missing output port '{edge.src_port}' from '{nid}'")
                    node_inputs[edge.dst_node][edge.dst_port] = out[edge.src_port]

        return node_outputs

    def execute(self, initial_inputs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
        """Alias for run()."""
        return self.run(initial_inputs=initial_inputs)

    def clear(self) -> None:
        """Clear all nodes and edges."""
        self._graph.clear()
        self.nodes.clear()
        self.edges_list.clear()


class ComputationalGraph(Graph):
    """Computational Graph specialized for quantum-classical hybrid nodes."""

    def __init__(self, name: str = "ComputationalGraph") -> None:
        super().__init__(name=name)
        self.execution_state: Dict[str, Any] = {}

    def validate_dag(self) -> bool:
        """Checks if the computational graph is valid DAG without circular dependencies."""
        return nx.is_directed_acyclic_graph(self._graph)

    def predecessors(self, node_id: str) -> List[str]:
        return list(self._graph.predecessors(node_id))

    def successors(self, node_id: str) -> List[str]:
        return list(self._graph.successors(node_id))
>>>>>>> 3a73ed0b5bb0fe7d5691e8c8c09488d6f7a98b39
