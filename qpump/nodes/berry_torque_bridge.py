"""Berry-phase and torque bridge node for the Q-PUMP scaffold."""

import math
from typing import Any, Dict, List

from .base import BaseNode


class BerryTorqueBridgeNode(BaseNode):
    @property
    def required_inputs(self) -> List[str]:
        return ["screened_phase", "alpha_target", "angular_deficit_rad"]

    @property
    def outputs(self) -> List[str]:
        return [
            "alpha_locked",
            "gap_residual",
            "torque_correction",
            "berry_phase_shift",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        screened = float(inputs["screened_phase"])
        target = float(inputs["alpha_target"])
        deficit = float(inputs["angular_deficit_rad"])

        if not all(math.isfinite(x) for x in (screened, target, deficit)):
            raise ValueError("Berry bridge inputs must be finite numbers.")

        gap_residual = target - screened
        torque_correction = gap_residual * (deficit / 0.12839)
        alpha_locked = screened + torque_correction
        berry_phase_shift = 1.9025 + 0.1 * torque_correction

        return {
            "alpha_locked": alpha_locked,
            "gap_residual": gap_residual,
            "torque_correction": torque_correction,
            "berry_phase_shift": berry_phase_shift,
        }
