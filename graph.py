"""
SDF QPUMP Scaffold - Core Graph Data Structure
Defines the Graph and Directed Acyclic Graph (DAG) abstractions used across
curvature computation pipelines and quantum simulation DAGs.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx


class Graph:
    """
    Core Graph representation wrapping NetworkX DiGraph for quantum pipeline operations,
    curvature flow, and DAG processing.
    """

    def __init__(self, name: str = "SDF_DAG", **kwargs: Any) -> None:
        self.name = name
        self._graph = nx.DiGraph(name=name, **kwargs)

    @property
    def underlying_graph(self) -> nx.DiGraph:
        """Direct access to internal NetworkX DiGraph instance."""
        return self._graph

    def add_node(self, node_id: Any, **attributes: Any) -> None:
        """Add a single node with arbitrary metadata/attributes."""
        self._graph.add_node(node_id, **attributes)

    def add_nodes_from(self, nodes_for_adding: Any, **attributes: Any) -> None:
        """Add multiple nodes with shared or distinct attributes."""
        self._graph.add_nodes_from(nodes_for_adding, **attributes)

    def add_edge(self, u: Any, v: Any, **attributes: Any) -> None:
        """Add a directed edge from node u to node v with attributes."""
        self._graph.add_edge(u, v, **attributes)

    def add_edges_from(self, ebunch_to_add: Any, **attributes: Any) -> None:
        """Add multiple directed edges."""
        self._graph.add_edges_from(ebunch_to_add, **attributes)

    def remove_node(self, node_id: Any) -> None:
        """Remove a node and all incident edges."""
        self._graph.remove_node(node_id)

    def remove_edge(self, u: Any, v: Any) -> None:
        """Remove the edge between u and v."""
        self._graph.remove_edge(u, v)

    def nodes(self, data: bool = False) -> Any:
        """Return graph nodes, optionally with attribute dictionaries."""
        return self._graph.nodes(data=data)

    def edges(self, data: bool = False) -> Any:
        """Return graph edges, optionally with attribute dictionaries."""
        return self._graph.edges(data=data)

    def neighbors(self, node_id: Any) -> Any:
        """Successors / outgoing neighbors of a given node."""
        return self._graph.neighbors(node_id)

    def predecessors(self, node_id: Any) -> Any:
        """Incoming predecessors of a given node."""
        return self._graph.predecessors(node_id)

    def successors(self, node_id: Any) -> Any:
        """Outgoing successors of a given node."""
        return self._graph.successors(node_id)

    def is_directed_acyclic_graph(self) -> bool:
        """Check if the internal graph structure is a valid DAG."""
        return nx.is_directed_acyclic_graph(self._graph)

    def topological_sort(self) -> List[Any]:
        """Return nodes in topologically sorted order."""
        if not self.is_directed_acyclic_graph():
            raise ValueError("Graph contains cycles; topological sort is undefined.")
        return list(nx.topological_sort(self._graph))

    def node_attributes(self, node_id: Any) -> Dict[str, Any]:
        """Retrieve attribute dictionary for a specific node."""
        return dict(self._graph.nodes[node_id])

    def edge_attributes(self, u: Any, v: Any) -> Dict[str, Any]:
        """Retrieve attribute dictionary for a specific directed edge."""
        return dict(self._graph.edges[u, v])

    def number_of_nodes(self) -> int:
        """Total node count."""
        return self._graph.number_of_nodes()

    def number_of_edges(self) -> int:
        """Total edge count."""
        return self._graph.number_of_edges()

    def clear(self) -> None:
        """Clear all nodes and edges."""
        self._graph.clear()

    def __len__(self) -> int:
        return len(self._graph)

    def __contains__(self, node_id: Any) -> bool:
        return node_id in self._graph

    def __iter__(self):
        return iter(self._graph)

    def __repr__(self) -> str:
        return (
            f"Graph(name='{self.name}', nodes={self.number_of_nodes()}, "
            f"edges={self.number_of_edges()}, is_dag={self.is_directed_acyclic_graph()})"
        )


__all__ = ["Graph"]
