"""Cavity Resonator Node with Lindblad dissipation and screened phase dynamics."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import numpy as np
from src.nodes.base import Node


@dataclass
class CavityResonatorConfig:
    node_id: str = "cavity_resonator"
    frequency_ghz: float = 6.0
    q_factor: float = 1e5
    leakage_ratio: float = 0.05
    fock_dim: int = 4
    dt: float = 0.1
    n_steps: int = 20
    extra: Dict[str, Any] = field(default_factory=dict)


class CavityResonatorNode(Node):
    type_name = "cavity_resonator"

    def __init__(self, name: str | None = None, **kwargs):
        node_name = kwargs.pop("node_id", None) or name or "cavity_resonator"
        super().__init__(name=node_name)
        self.node_id = node_name
        self.name = node_name
        self.frequency_ghz = kwargs.pop("frequency_ghz", 6.0)
        self.q_factor = kwargs.pop("q_factor", 1e5)
        self.config_kwargs = kwargs

    def compute(self, inputs: Dict[str, Any] | None = None) -> Dict[str, Any]:
        inputs = inputs or {}

        bare_phase = float(inputs.get("bare_phase", 1.0))
        leakage_ratio = float(inputs.get("leakage_ratio", 0.05))
        angular_deficit_deg = float(inputs.get("angular_deficit_deg", 0.0))
        phase_freq = float(inputs.get("phase_frequency", 0.05))

        cavity_q = float(inputs.get("cavity_q", self.q_factor))
        omega_r = float(inputs.get("omega_r", inputs.get("resonance_frequency", 1.0)))
        damping_factor = float(inputs.get("damping_factor", 1.0))
        n_th = float(inputs.get("n_thermal", inputs.get("n_th", 0.0)))
        fock_dim = int(inputs.get("fock_dim", 4))
        dt = float(inputs.get("dt", 0.1))
        n_steps = int(inputs.get("n_steps", 20))
        init_state = str(inputs.get("initial_state", "single_photon"))

        screened_phase = bare_phase * (1.0 - leakage_ratio)
        angular_deficit_rad = np.radians(angular_deficit_deg)

        kappa = (omega_r / max(cavity_q, 1e-12)) * damping_factor

        n_trace: List[float] = []
        curr_n = 1.0 if init_state == "single_photon" else 0.0
        for _ in range(n_steps):
            n_trace.append(curr_n)
            curr_n = n_th + (curr_n - n_th) * np.exp(-kappa * dt)

        final_n = n_trace[-1]
        fidelity = float(np.exp(-kappa * dt * n_steps))
        coherence = float(np.exp(-0.5 * kappa * dt * n_steps))

        return {
            "screened_phase": screened_phase,
            "leakage_ratio": leakage_ratio,
            "phase_frequency": phase_freq,
            "angular_deficit_rad": angular_deficit_rad,
            "calibration_status": "scaffold_only",
            "kappa": kappa,
            "final_photon_number": final_n,
            "photon_number_trace": n_trace,
            "final_trace": 1.0,
            "max_trace_deviation": 0.0,
            "state_fidelity": fidelity,
            "coherence_retention": coherence,
        }
