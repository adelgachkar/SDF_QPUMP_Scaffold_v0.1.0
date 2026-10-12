"""
Node Registry for Q-PUMP architecture.
Manages node registration, instantiation, and discovery.
"""

from typing import Dict, Type, Any, Optional
from src.nodes.base import Node

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


# Safe discovery / pre-registration
try:
    from src.nodes.cavity_resonator import CavityResonatorNode
    register_node("cavity_resonator")(CavityResonatorNode)
except ImportError:
    pass

try:
    from src.nodes.berry_torque_bridge import BerryTorqueBridgeNode
    register_node("berry_torque_bridge")(BerryTorqueBridgeNode)
except ImportError:
    pass

try:
    from src.nodes.peristaltic_pump import PeristalticPumpNode
    register_node("peristaltic_pump")(PeristalticPumpNode)
except ImportError:
    pass

try:
    from src.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode
    register_node("boundary_stress_integrator")(BoundaryStressIntegratorNode)
except ImportError:
    pass

try:
    from src.nodes.gravitational_curvature import GravitationalCurvatureNode
    register_node("gravitational_curvature")(GravitationalCurvatureNode)
except ImportError:
    pass

try:
    from src.nodes.quantum_backreaction import QuantumBackreactionNode
    register_node("quantum_backreaction")(QuantumBackreactionNode)
except ImportError:
    pass

try:
    from src.nodes.radial_propagation import RadialPropagationNode
    register_node("radial_propagation")(RadialPropagationNode)
except ImportError:
    pass
