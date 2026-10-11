"""Cavity resonator node for the Q-PUMP scaffold."""

import math
from typing import Any, Dict, List

from .base import BaseNode


class CavityResonatorNode(BaseNode):
    @property
    def required_inputs(self) -> List[str]:
        return ["bare_phase", "angular_deficit_deg"]

    @property
    def outputs(self) -> List[str]:
        return [
            "screened_phase",
            "leakage_ratio",
            "phase_frequency",
            "angular_deficit_rad",
            "calibration_status",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        bare_phase = float(inputs["bare_phase"])
        deficit_deg = float(inputs["angular_deficit_deg"])

        default_leakage = self.config.get("leakage_ratio", 1.0 / 15.0)
        leakage = float(inputs.get("leakage_ratio", default_leakage))

        if not all(math.isfinite(x) for x in (bare_phase, deficit_deg, leakage)):
            raise ValueError("Cavity node inputs must be finite numbers.")
        if not 0.0 <= leakage < 1.0:
            raise ValueError("leakage_ratio must be in the interval [0, 1).")

        screened_phase = bare_phase * (1.0 - leakage)

        return {
            "screened_phase": screened_phase,
            "leakage_ratio": leakage,
            "phase_frequency": screened_phase / (2.0 * math.pi),
            "angular_deficit_rad": math.radians(deficit_deg),
            # محاسبهٔ اسکلت نرم‌افزاری است؛ به معنی کالیبراسیون تجربی نیست.
            "calibration_status": "scaffold_only",
        }
