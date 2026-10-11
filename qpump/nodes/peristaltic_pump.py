"""Peristaltic phase-pump node for the Q-PUMP scaffold."""

import math
from typing import Any, Dict, List

from .base import BaseNode


class PeristalticPumpNode(BaseNode):
    @property
    def required_inputs(self) -> List[str]:
        return ["drive_amplitude", "berry_phase_shift", "phase_frequency"]

    @property
    def outputs(self) -> List[str]:
        return [
            "jet_power",
            "phase_flux_vector",
            "peristaltic_frequency",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        drive = float(inputs["drive_amplitude"])
        berry_shift = float(inputs["berry_phase_shift"])
        phase_frequency = float(inputs["phase_frequency"])

        if not all(math.isfinite(x) for x in (drive, berry_shift, phase_frequency)):
            raise ValueError("Peristaltic pump inputs must be finite numbers.")
        if drive < 0.0:
            raise ValueError("drive_amplitude must be non-negative.")

        jet_power = 0.931314 * drive * math.sin(berry_shift / 2.0) ** 2
        phase_flux_vector = [
            0.0,
            0.0,
            jet_power * phase_frequency * 0.05,
        ]

        return {
            "jet_power": jet_power,
            "phase_flux_vector": phase_flux_vector,
            "peristaltic_frequency": phase_frequency * 0.5,
        }
