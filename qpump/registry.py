"""
Node Registry for SDF_QPUMP_Scaffold
Maps string identifiers to concrete Node implementations.
"""

from typing import Dict, Type
from qpump.nodes.base import Node
from qpump.nodes.cavity_resonator import CavityResonatorNode
from qpump.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode
from qpump.nodes.gravitational_curvature import GravitationalCurvatureNode
from qpump.nodes.effective_metric_source import EffectiveMetricSourceNode
from qpump.nodes.peristaltic_pump import PeristalticPumpNode
from qpump.nodes.quantum_backreaction import QuantumBackreactionNode
from qpump.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from qpump.nodes.five_tetrahedral_cavity import FiveTetrahedralCavityNode
from qpump.nodes.optical_phase_step import OpticalPhaseStepNode
from qpump.nodes.radial_propagation import RadialPropagationNode

NODE_REGISTRY: Dict[str, Type[Node]] = {
    "CavityResonatorNode": CavityResonatorNode,
    "BoundaryStressIntegratorNode": BoundaryStressIntegratorNode,
    "GravitationalCurvatureNode": GravitationalCurvatureNode,
    "EffectiveMetricSourceNode": EffectiveMetricSourceNode,
    "PeristalticPumpNode": PeristalticPumpNode,
    "QuantumBackreactionNode": QuantumBackreactionNode,
    "BerryTorqueBridgeNode": BerryTorqueBridgeNode,
    "FiveTetrahedralCavityNode": FiveTetrahedralCavityNode,
    "OpticalPhaseStepNode": OpticalPhaseStepNode,
    "RadialPropagationNode": RadialPropagationNode,
}


def get_node_class(class_name: str) -> Type[Node]:
    """Retrieve node class from registry."""
    if class_name not in NODE_REGISTRY:
        raise KeyError(f"Node class '{class_name}' not found in registry.")
    return NODE_REGISTRY[class_name]
