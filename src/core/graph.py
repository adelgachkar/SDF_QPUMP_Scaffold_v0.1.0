"""
Core Computational Graph and DAG representation for SDF_QPUMP Scaffold.
Provides directed acyclic graph operations for quantum pipeline and tensor processing.
"""

from typing import Any, Dict, List, Optional
import networkx as nx


class Graph:
    """Wrapper around NetworkX DiGraph for structured SDF pipeline execution."""

    def __init__(self, name: str = "QuantumSDFGraph"):
        self.name = name
        self._graph = nx.DiGraph()

    @property
    def internal_graph(self) -> nx.DiGraph:
        """Direct access to the underlying NetworkX directed graph."""
        return self._graph

    def add_node(self, node_id: str, **attributes: Any) -> None:
        """Register a node in the graph with optional metadata."""
        self._graph.add_node(node_id, **attributes)

    def add_edge(self, source: str, target: str, **attributes: Any) -> None:
        """Add a directed edge representing data flow dependency."""
        self._graph.add_edge(source, target, **attributes)

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Retrieve node attributes by identifier."""
        if node_id not in self._graph:
            raise KeyError(f"Node '{node_id}' does not exist in graph.")
        return dict(self._graph.nodes[node_id])

    def nodes(self) -> List[str]:
        """List all node IDs currently in the graph."""
        return list(self._graph.nodes())

    def edges(self) -> List[tuple]:
        """List all directed edges in the graph."""
        return list(self._graph.edges())

    def topological_sort(self) -> List[str]:
        """Return execution order of nodes respecting dependencies."""
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("Graph contains cycles; cannot perform topological sort.")
        return list(nx.topological_sort(self._graph))

    def clear(self) -> None:
        """Reset the graph completely."""
        self._graph.clear()


class ComputationalGraph(Graph):
    """
    Specialized DAG for quantum-classical hybrid nodes,
    handling state routing and dependency execution.
    """

    def __init__(self, name: str = "ComputationalGraph"):
        super().__init__(name=name)
        self.execution_state: Dict[str, Any] = {}

    def validate_dag(self) -> bool:
        """Check if current topology is a valid DAG."""
        return nx.is_directed_acyclic_graph(self._graph)

    def predecessors(self, node_id: str) -> List[str]:
        """Return node IDs that this node directly depends on."""
        return list(self._graph.predecessors(node_id))

    def successors(self, node_id: str) -> List[str]:
        """Return node IDs that directly depend on this node."""
        return list(self._graph.successors(node_id))
