from __future__ import annotations
import math
from typing import Any, Dict, Optional
from .base import Node

class BoundaryStressIntegratorNode(Node):
    def __init__(self, node_id: Optional[str] = None, name: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(node_id=name or node_id, name=name or node_id, **kwargs)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        jet_power = float(inputs.get("jet_power", 0.0))
        noise_floor = float(inputs.get("noise_floor", 1.0))
        trace = float(inputs.get("effective_metric_trace", 1.0))
        backreaction = float(inputs.get("quantum_backreaction_force", 0.0))

        snr = jet_power / noise_floor if noise_floor > 0 else float('inf')
        if jet_power > noise_floor:
            regime = "newtonian"
            thrust = jet_power * 0.1 * trace + backreaction
        else:
            regime = "sub-noise"
            thrust = 0.0

        tensor = [thrust, 0.0, 0.0, thrust * 0.5]
        return {
            "stress_regime": regime,
            "regime": regime,
            "stress_snr": snr,
            "snr": snr,
            "net_thrust_n": thrust,
            "net_thrust": thrust,
            "boundary_stress_tensor": tensor,
            "stress_tensor": tensor
        }
