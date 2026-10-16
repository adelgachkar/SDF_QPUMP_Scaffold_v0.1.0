"""
SDF-QPUMP Scaffold: Core Registry Bridge
Compatibility layer forwarding to src.registry with NodeRegistry adapter.
"""
from typing import Dict, List, Type, Any
from src.registry import (
    register_node,
    create_node,
    registered_types,
    clear_registry,
    load_graph_from_dict,
    load_graph_from_json,
    save_graph_to_dict,
    save_graph_to_json,
    _NODE_REGISTRY,
)


class NodeRegistry:
    """Class wrapper adapting the test expectation to functional registry."""
    def register(self, name: str, node_cls: Type[Any]) -> None:
        register_node(name)(node_cls)

    def get(self, name: str) -> Type[Any]:
        return _NODE_REGISTRY[name]

    def list_nodes(self) -> List[str]:
        return sorted(_NODE_REGISTRY.keys())


__all__ = [
    "register_node",
    "create_node",
    "registered_types",
    "clear_registry",
    "load_graph_from_dict",
    "load_graph_from_json",
    "save_graph_to_dict",
    "save_graph_to_json",
    "_NODE_REGISTRY",
    "NodeRegistry",
]
