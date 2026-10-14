"""Peristaltic Pump node for SDF QPUMP."""
from __future__ import annotations
import numpy as np
from typing import Any, Dict, Optional
from .base import Node

class PeristalticPumpNode(Node):
    def __init__(
        self,
        node_id: Optional[str] = None,
        label: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(node_id=node_id, label=label, config=config, name=name, **kwargs)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        amp = inputs.get("drive_amplitude", inputs.get("drive_phase", 1.0))
        phi = inputs.get("berry_phase_shift", inputs.get("geometric_phase_shift", 0.0))
        freq = inputs.get("phase_frequency", inputs.get("pump_freq", 1e9))

        amp = float(amp)
        phi = float(phi)
        freq = float(freq)

        jet_power = amp * (1.0 + np.sin(phi))
        flux_vec = np.array([0.0, 0.0, jet_power * 1e-3], dtype=float)

        return {
            "jet_power": jet_power,
            "phase_flux_vector": flux_vec,
            "peristaltic_frequency": freq,
        }
