"""
Core Computational Graph and DAG representation for SDF_QPUMP Scaffold.
Supports port-based routing, cycle detection, deterministic execution,
and NetworkX-compatible node mapping.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import networkx as nx


class NodePortConnection:
    """Represents a connection between specific output and input ports."""
    def __init__(self, src_node: str, src_port: str, dst_node: str, dst_port: str):
        self.src_node = src_node
        self.src_port = src_port
        self.dst_node = dst_node
        self.dst_port = dst_port


class Graph:
    """
    DAG execution graph with port-level wiring and deterministic evaluation.
    """

    def __init__(self, name: str = "QuantumSDFGraph"):
        self.name = name
        self._graph = nx.DiGraph()
        self._node_objects: Dict[str, Any] = {}
        self._edges: List[NodePortConnection] = []

    @property
    def internal_graph(self) -> nx.DiGraph:
        """Direct access to underlying DiGraph."""
        return self._graph

    @property
    def nodes(self) -> Dict[str, Any]:
        """Provides mapping interface to nodes consistent with test expectations."""
        return self._node_objects

    def add_node(self, node: Any, **attributes: Any) -> None:
        """
        Register a node object or node identifier.
        Raises ValueError on duplicate node ID.
        """
        # Determine node identifier
        if hasattr(node, "name"):
            node_id = node.name
        elif hasattr(node, "node_id"):
            node_id = node.node_id
        elif isinstance(node, str):
            node_id = node
        else:
            node_id = str(node)

        if node_id in self._node_objects:
            raise ValueError(f"duplicate node '{node_id}' detected in graph")

        self._node_objects[node_id] = node
        self._graph.add_node(node_id, obj=node, **attributes)

    def connect(self, src: str, src_port: str, dst: str, dst_port: str) -> None:
        """
        Connect output port of src node to input port of dst node.
        Validates presence of nodes and ports, and rejects cycles.
        """
        if src not in self._node_objects:
            raise KeyError(f"Source node '{src}' not found.")
        if dst not in self._node_objects:
            raise KeyError(f"Destination node '{dst}' not found.")

        src_obj = self._node_objects[src]
        # Validate output port if node exposes output_ports / outputs
        if hasattr(src_obj, "output_ports"):
            ports = src_obj.output_ports
            if callable(ports):
                ports = ports()
            if src_port not in ports:
                raise ValueError(f"Port '{src_port}' is absent on source node '{src}'.")
        elif hasattr(src_obj, "outputs"):
            ports = src_obj.outputs
            if callable(ports):
                ports = ports()
            if src_port not in ports:
                raise ValueError(f"Port '{src_port}' is absent on source node '{src}'.")

        # Cycle check
        self._graph.add_edge(src, dst)
        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(src, dst)
            raise ValueError(f"Cycle detected: connecting '{src}' -> '{dst}' forms a cycle.")

        self._edges.append(NodePortConnection(src, src_port, dst, dst_port))

    def add_edge(self, *args: Any, **kwargs: Any) -> None:
        """
        Flexible edge connector supporting both:
          add_edge(src, dst, **attrs)
          add_edge(src, src_port, dst, dst_port)
        """
        if len(args) == 4:
            src, src_port, dst, dst_port = args
            self.connect(src, src_port, dst, dst_port)
        elif len(args) == 2:
            src, dst = args
            self._graph.add_edge(src, dst, **kwargs)
        else:
            raise TypeError(f"Graph.add_edge takes 2 or 4 positional arguments, got {len(args)}.")

    def get_node(self, node_id: str) -> Any:
        """Retrieve node instance by identifier."""
        if node_id not in self._node_objects:
            raise KeyError(f"Node '{node_id}' does not exist in graph.")
        return self._node_objects[node_id]

    def topological_sort(self) -> List[str]:
        """Return execution order respecting node dependencies."""
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("Graph contains cycles; cannot perform topological sort.")
        return list(nx.topological_sort(self._graph))

    def run(self, initial_state: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Execute nodes in topological order, routing values through port connections.
        """
        outputs: Dict[str, Dict[str, Any]] = {}
        inputs: Dict[str, Dict[str, Any]] = {k: dict(v) for k, v in (initial_state or {}).items()}

        order = self.topological_sort()
        for node_id in order:
            node_obj = self._node_objects[node_id]
            node_in = inputs.get(node_id, {})

            if hasattr(node_obj, "execute"):
                res = node_obj.execute(node_in)
            elif hasattr(node_obj, "run"):
                res = node_obj.run(node_in)
            elif hasattr(node_obj, "compute"):
                res = node_obj.compute(node_in)
            elif callable(node_obj):
                res = node_obj(node_in)
            else:
                res = dict(node_in)

            if not isinstance(res, dict):
                res = {"output": res}
            outputs[node_id] = res

            # Route to connected destination ports
            for edge in self._edges:
                if edge.src_node == node_id:
                    dst = edge.dst_node
                    if dst not in inputs:
                        inputs[dst] = {}
                    if edge.src_port in res:
                        inputs[dst][edge.dst_port] = res[edge.src_port]

        return outputs

    def clear(self) -> None:
        """Clear graph state."""
        self._graph.clear()
        self._node_objects.clear()
        self._edges.clear()


class ComputationalGraph(Graph):
    """Network graph specialized for hybrid pipeline execution."""

    def __init__(self, name: str = "ComputationalGraph"):
        super().__init__(name=name)

    def validate_dag(self) -> bool:
        """Check if current topology is a valid DAG."""
        return nx.is_directed_acyclic_graph(self._graph)

    def predecessors(self, node_id: str) -> List[str]:
        """Return upstream node IDs."""
        return list(self._graph.predecessors(node_id))

    def successors(self, node_id: str) -> List[str]:
        """Return downstream node IDs."""
        return list(self._graph.successors(node_id))
