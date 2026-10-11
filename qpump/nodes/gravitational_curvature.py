from typing import Any, Dict

from qpump.nodes.base import BaseNode


class GravitationalCurvatureNode(BaseNode):
    def __init__(
        self,
        node_id: str = "gravitational_curvature",
        coupling_g: float = 1.0,
    ) -> None:
        super().__init__(node_id=node_id)
        self.coupling_g = float(coupling_g)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        net_thrust = float(inputs.get("net_thrust", 0.0))
        ricci_proxy = self.coupling_g * net_thrust
        abs_r = abs(ricci_proxy)

        if abs_r > 10.0:
            regime = "strong_field_curvature"
        elif abs_r > 1e-6:
            regime = "perturbative_linear"
        else:
            regime = "asymptotically_flat"

        h_trace = 0.5 * ricci_proxy
        effective_acc = abs(net_thrust) * self.coupling_g

        return {
            "ricci_scalar_proxy": ricci_proxy,
            "curvature_scalar_R": ricci_proxy,
            "metric_trace_perturbation": h_trace,
            "effective_acceleration": effective_acc,
            "is_locally_curved": abs_r > 1e-9,
            "curvature_regime": regime,
        }

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.compute(inputs)
