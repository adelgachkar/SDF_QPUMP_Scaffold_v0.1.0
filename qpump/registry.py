from typing import Dict, Type
from qpump.nodes.base import Node
from qpump.nodes.peristaltic_pump import PeristalticPumpNode
from qpump.nodes.cavity_resonator import CavityResonatorNode
from qpump.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode
from qpump.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from qpump.nodes.effective_metric_source import EffectiveMetricSourceNode
from qpump.nodes.gravitational_curvature import GravitationalCurvatureNode
from qpump.nodes.quantum_backreaction import QuantumBackreactionNode
from qpump.nodes.z_axis_filter_queue import ZAxisFilterQueueNode

NODE_REGISTRY: Dict[str, Type[Node]] = {
    "peristaltic_pump": PeristalticPumpNode,
    "cavity_resonator": CavityResonatorNode,
    "boundary_stress_integrator": BoundaryStressIntegratorNode,
    "berry_torque_bridge": BerryTorqueBridgeNode,
    "effective_metric_source": EffectiveMetricSourceNode,
    "gravitational_curvature": GravitationalCurvatureNode,
    "quantum_backreaction": QuantumBackreactionNode,
    "z_axis_filter_queue": ZAxisFilterQueueNode,
}

def get_node_class(node_type: str) -> Type[Node]:
    if node_type not in NODE_REGISTRY:
        raise ValueError(f"Unknown node type: {node_type}. Available types: {list(NODE_REGISTRY.keys())}")
    return NODE_REGISTRY[node_type]
