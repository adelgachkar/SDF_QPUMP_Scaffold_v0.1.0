"""
SDF_QPUMP Core Registry Module
Compatibility layer and NodeRegistry class definition.
"""

from typing import Dict, Any, Type, Optional
import src.registry as _root_reg
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
    """Registry class for managing and instantiating pipeline nodes."""
    def __init__(self):
        self._nodes: Dict[str, Any] = dict(_NODE_REGISTRY)

    def register(self, name: str, cls: Any) -> Any:
        self._nodes[name] = cls
        _NODE_REGISTRY[name] = cls
        return cls

    def get(self, name: str) -> Any:
        if name not in self._nodes:
            raise KeyError(f"Node type '{name}' not found in registry.")
        return self._nodes[name]

    def list_nodes(self) -> Dict[str, Any]:
        return dict(self._nodes)
