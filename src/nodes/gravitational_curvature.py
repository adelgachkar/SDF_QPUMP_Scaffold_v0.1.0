"""
src/nodes/gravitational_curvature.py
Gravitational Curvature Node for SDF QPUMP Phase 3.
Transforms boundary stress tensor and net thrust into spacetime curvature proxies.
"""

import math
from typing import Any, Dict, List, Optional

try:
    from src.nodes.base import Node, BaseNode
except ModuleNotFoundError:
    try:
        from qpump.nodes.base import Node, BaseNode
    except ModuleNotFoundError:
        from .base import Node, BaseNode


class GravitationalCurvatureNode(Node):
    """
    Computes Ricci proxy, metric perturbations, and local curvature state.
    """

    def __init__(
        self,
        node_id: Optional[str] = None,
        name: Optional[str] = None,
        label: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        coupling_g: float = 1.0,
        **kwargs: Any,
    ) -> None:
        actual_id = node_id or name or kwargs.get("id", "gravitational_curvature")
        actual_label = label or name or actual_id
        super().__init__(node_id=actual_id, label=actual_label, config=config)
        self.name = actual_id
        self.coupling_g = float(self.config.get("coupling_g", coupling_g))

    @property
    def input_ports(self) -> List[str]:
        return ["stress_tensor", "net_thrust", "boundary_force", "stress_tensor_4x4"]

    @property
    def output_ports(self) -> List[str]:
        return [
            "ricci_scalar_proxy",
            "metric_trace_perturbation",
            "effective_acceleration",
            "curvature_regime",
            "is_locally_curved",
            "coupling_g",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        net_thrust = float(inputs.get("net_thrust", inputs.get("boundary_force", 0.0)))
        kappa = float(self.config.get("kappa_coupling", self.coupling_g))
        
        # Effective acceleration scaled by coupling_g / mass
        effective_mass = max(1e-12, float(self.config.get("effective_mass", 1.0)))
        effective_acceleration = float(net_thrust * self.coupling_g / effective_mass)

        # Trace calculation
        has_explicit_tensor = "stress_tensor" in inputs or "stress_tensor_4x4" in inputs
        if has_explicit_tensor:
            stress_tensor = inputs.get("stress_tensor", inputs.get("stress_tensor_4x4"))
            dim = len(stress_tensor)
            trace_t = sum(stress_tensor[i][i] for i in range(dim))
            ricci_scalar_proxy = float(kappa * trace_t)
        else:
            # Conservative field fallback: Ricci scalar mirrors thrust * coupling_g
            ricci_scalar_proxy = float(net_thrust * self.coupling_g)

        metric_trace_perturbation = float(0.5 * kappa * net_thrust)
        is_locally_curved = abs(ricci_scalar_proxy) > 1e-9

        if ricci_scalar_proxy > 1.0:
            regime = "strong_field_curvature"
        elif ricci_scalar_proxy > 1e-4:
            regime = "perturbative_linear"
        else:
            regime = "asymptotically_flat"

        return {
            "ricci_scalar_proxy": ricci_scalar_proxy,
            "metric_trace_perturbation": metric_trace_perturbation,
            "effective_acceleration": effective_acceleration,
            "curvature_regime": regime,
            "is_locally_curved": is_locally_curved,
            "coupling_g": self.coupling_g,
        }

    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for compute."""
        return self.compute(inputs)
