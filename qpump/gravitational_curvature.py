from typing import Any, Dict

from qpump.nodes.base import BaseNode


class GravitationalCurvatureNode(BaseNode):
    """
    Computes induced curvature and an effective acceleration proxy from boundary stress dynamics.

    Expected outputs (required by tests):
      - ricci_scalar_proxy (float)
      - effective_acceleration (float, >= 0)
      - curvature_regime (str): one of
          ["strong_field_curvature", "perturbative_linear", "asymptotically_flat"]
    """

    def __init__(
        self,
        node_id: str = "gravitational_curvature",
        coupling_g: float = 1.0,
    ) -> None:
        super().__init__(node_id=node_id)
        self.coupling_g = float(coupling_g)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Inputs used by the test:
        # - net_thrust: float
        net_thrust = float(inputs.get("net_thrust", 0.0))

        # A simple deterministic proxy model:
        ricci_proxy = self.coupling_g * net_thrust
        abs_r = abs(ricci_proxy)

        # Regime classification required by test_curvature_pipeline.py
        if abs_r > 10.0:
            regime = "strong_field_curvature"
        elif abs_r > 1e-6:
            regime = "perturbative_linear"
        else:
            regime = "asymptotically_flat"

        # Keep extra outputs stable/useful for other tests or future nodes
        h_trace = 0.5 * ricci_proxy
        effective_acc = abs(net_thrust) * self.coupling_g  # always >= 0

        return {
            "ricci_scalar_proxy": ricci_proxy,
            "curvature_scalar_R": ricci_proxy,
            "metric_trace_perturbation": h_trace,
            "effective_acceleration": effective_acc,
            "is_locally_curved": abs_r > 1e-9,
            "curvature_regime": regime,
        }

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Tests expect execute(); BaseNode may already route execute->compute,
        # but we keep this explicit for safety.
        return self.compute(inputs)
