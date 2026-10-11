from typing import Any, Dict
import math
from qpump.nodes.base import BaseNode


class QuantumBackreactionNode(BaseNode):
    def __init__(
        self,
        node_id: str = "quantum_backreaction",
        damping_rate: float = 0.05,
    ) -> None:
        super().__init__(node_id=node_id)
        self.damping_rate = float(damping_rate)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        ricci = float(inputs.get("ricci_scalar_proxy", 0.0))
        power = float(inputs.get("jet_power", 0.0))
        shift = float(inputs.get("berry_phase_shift", 0.0))

        damping = 1.0 / (1.0 + self.damping_rate * abs(ricci) + 0.01 * abs(power))
        divergence = abs(ricci * power * 1e-4)

        if damping > 0.5:
            status = "subcritical_stable"
        else:
            status = "supercritical_turbulent"

        return {
            "damping_factor": float(damping),
            "conservation_divergence": float(divergence),
            "stability_status": status,
            "effective_backreaction": float(damping * power),
        }

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.compute(inputs)
