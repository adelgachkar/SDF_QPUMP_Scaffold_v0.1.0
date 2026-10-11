"""
Node Registry for Q-PUMP architecture.
Manages node registration, instantiation, and discovery.
"""

from typing import Dict, Type, Any, Optional
from qpump.nodes.base import Node

# دیکشنری نگه‌دارنده کلاس نودهای ثبت‌شده
_NODE_REGISTRY: Dict[str, Type[Node]] = {}


def register_node(name: Optional[str] = None):
    """
    Decorator for registering node classes into the registry.
    Can be used as @register_node or @register_node("custom_name").
    """
    def decorator(cls: Type[Node]) -> Type[Node]:
        node_name = name or cls.__name__
        _NODE_REGISTRY[node_name] = cls
        return cls

    if callable(name):
        cls_func = name
        name = cls_func.__name__
        _NODE_REGISTRY[name] = cls_func
        return cls_func

    return decorator


def create_node(node_type: str, *args, **kwargs) -> Node:
    """
    Factory function to instantiate a node by its registered name.
    """
    if node_type not in _NODE_REGISTRY:
        raise KeyError(
            f"Node type '{node_type}' is not registered. "
            f"Available types: {list(_NODE_REGISTRY.keys())}"
        )
    return _NODE_REGISTRY[node_type](*args, **kwargs)


def registered_types() -> Dict[str, Type[Node]]:
    """
    Returns a copy of the registered node types dictionary.
    """
    return dict(_NODE_REGISTRY)


def clear_registry() -> None:
    """
    Clears the node registry (useful for test isolation).
    """
    _NODE_REGISTRY.clear()
