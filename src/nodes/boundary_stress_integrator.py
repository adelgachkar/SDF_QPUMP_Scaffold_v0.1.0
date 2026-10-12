"""Boundary stress integrator node for the Q-PUMP scaffold."""

import math
from typing import Any, Dict, List
from .base import BaseNode


class BoundaryStressIntegratorNode(BaseNode):
    """
    Integrates peristaltic jet power and background boundary fluctuations
    into effective boundary stress tensor components and determines the dynamic regime.
    """

    @property
    def required_inputs(self) -> List[str]:
        return ["jet_power"]

    @property
    def outputs(self) -> List[str]:
        return [
            "net_thrust",
            "stress_tensor",
            "regime",
            "snr",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        jet_power = float(inputs["jet_power"])
        noise_floor = float(inputs.get("noise_floor", 1e-4))

        if not (math.isfinite(jet_power) and math.isfinite(noise_floor)):
            raise ValueError("Boundary stress inputs must be finite numbers.")
        if noise_floor <= 0.0:
            raise ValueError("noise_floor must be strictly positive.")

        snr = jet_power / noise_floor

        # تعیین رژیم دینامیکی متناسب با نسبت سیگنال به نویز و توان
        if snr > 1e3:
            regime = "newtonian"
        elif snr > 1.0:
            regime = "transitional"
        else:
            regime = "sub-noise"

        # تنسور تنش مرزی ۴ مؤلفه‌ای (ماتریس ۲×۲ یا فرم متعارف فاز مرزی)
        # [T_00, T_01, T_10, T_11]
        t00 = jet_power
        t01 = noise_floor * 0.5
        t10 = noise_floor * 0.5
        t11 = jet_power * 0.1

        stress_tensor = [t00, t01, t10, t11]
        net_thrust = math.sqrt(max(0.0, jet_power**2 - noise_floor**2)) if jet_power >= noise_floor else 0.0

        return {
            "net_thrust": net_thrust,
            "stress_tensor": stress_tensor,
            "regime": regime,
            "snr": snr,
        }
