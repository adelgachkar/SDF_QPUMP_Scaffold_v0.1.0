"""Deterministic directed acyclic graph execution."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .nodes.base import Node

@dataclass(frozen=True)
class Edge:
    source: str
    source_port: str
    target: str
    target_port: str

class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node) -> None:
        if node.node_id in self.nodes:
            raise ValueError(f"duplicate node id: {node.node_id}")
        self.nodes[node.node_id] = node

    def connect(self, source: str, source_port: str, target: str, target_port: str) -> Edge:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("both source and target nodes must exist")
        if not all(isinstance(p, str) and p for p in (source_port, target_port)):
            raise ValueError("port names must be non-empty strings")
        edge = Edge(source, source_port, target, target_port)
        self.edges.append(edge)
        return edge

    def _order(self) -> list[str]:
        incoming = {n: 0 for n in self.nodes}
        outgoing = {n: [] for n in self.nodes}
        for edge in self.edges:
            incoming[edge.target] += 1
            outgoing[edge.source].append(edge.target)
        ready = sorted(n for n, count in incoming.items() if count == 0)
        result = []
        while ready:
            current = ready.pop(0)
            result.append(current)
            for target in sorted(outgoing[current]):
                incoming[target] -= 1
                if incoming[target] == 0:
                    ready.append(target)
                    ready.sort()
        if len(result) != len(self.nodes):
            raise ValueError("graph contains a cycle")
        return result

    def run(self, initial: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
        values = {key: dict(value) for key, value in (initial or {}).items()}
        unknown = set(values) - set(self.nodes)
        if unknown:
            raise KeyError(f"initial values reference unknown node(s): {sorted(unknown)}")
        for node_id in self.nodes:
            values.setdefault(node_id, {})
        for node_id in self._order():
            try:
                outputs = self.nodes[node_id].compute(dict(values[node_id]))
                if not isinstance(outputs, dict):
                    raise TypeError("compute() must return a dict")
            except Exception as exc:
                raise RuntimeError(f"Execution failed at Node '{node_id}': {exc}") from exc
            values[node_id].update(outputs)
            for edge in self.edges:
                if edge.source == node_id:
                    if edge.source_port not in outputs:
                        raise KeyError(f"missing output port: {node_id}.{edge.source_port}")
                    values[edge.target][edge.target_port] = outputs[edge.source_port]
        return values

NodeGraph = Graph
