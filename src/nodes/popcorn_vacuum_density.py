"""
Popcorn Vacuum Density Node for SDF-QPUMP Cosmology
Implements nucleation threshold and Hubble tension scaling.
"""
from dataclasses import dataclass
from typing import Dict, Any, Union
import numpy as np

from src.nodes.base import BaseNode

H0_EARLY_DEFAULT = 67.4
H0_LOCAL_DEFAULT = 73.04
MPC_IN_KM = 3.085677581491367e19
C_LIGHT_M_S = 299792458.0


@dataclass
class PopcornVacuumConfig:
    H0_early: float = H0_EARLY_DEFAULT
    H0_late: float = H0_LOCAL_DEFAULT
    lambda_coh_kpc: float = 12.0
    vacuum_energy_density: float = 5.35e-10


class PopcornVacuumDensityNode(BaseNode):
    def __init__(
        self,
        node_id: str = "popcorn_vacuum_density",
        label: str = "Popcorn Vacuum Density",
        config: Union[Dict[str, Any], PopcornVacuumConfig] = None,
        **kwargs: Any,
    ):
        super().__init__(node_id=node_id, label=label, config=config or {}, **kwargs)
        if isinstance(config, PopcornVacuumConfig):
            self.cfg = config
        else:
            c = config or {}
            self.cfg = PopcornVacuumConfig(
                H0_early=float(c.get("H0_early", H0_EARLY_DEFAULT)),
                H0_late=float(c.get("H0_late", H0_LOCAL_DEFAULT)),
                lambda_coh_kpc=float(c.get("lambda_coh_kpc", 12.0)),
                vacuum_energy_density=float(c.get("vacuum_energy_density", 5.35e-10)),
            )

    @staticmethod
    def compute_a0(h0_value: float) -> float:
        """Convert H0 (km/s/Mpc) directly to critical acceleration a0 (m/s^2)."""
        h0_si = float(h0_value) / MPC_IN_KM
        return (C_LIGHT_M_S * h0_si) / (2.0 * np.pi)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if "g_bar" not in inputs:
            raise ValueError("PopcornVacuumDensityNode requires 'g_bar' in inputs.")

        g_bar = np.asarray(inputs["g_bar"], dtype=float)
        a0_early = self.compute_a0(self.cfg.H0_early)
        a0_local = self.compute_a0(self.cfg.H0_late)

        vacuum_nucleation_factor = np.sqrt(a0_local / np.maximum(g_bar, 1e-15))
        g_pop_early = np.sqrt(np.maximum(g_bar * a0_early, 0.0))
        g_pop_local = np.sqrt(np.maximum(g_bar * a0_local, 0.0))

        return {
            "a0_early": float(a0_early),
            "a0_local": float(a0_local),
            "g_pop_early": g_pop_early.tolist() if g_pop_early.ndim > 0 else float(g_pop_early),
            "g_pop_local": g_pop_local.tolist() if g_pop_local.ndim > 0 else float(g_pop_local),
            "vacuum_nucleation_factor": (
                vacuum_nucleation_factor.tolist()
                if vacuum_nucleation_factor.ndim > 0
                else float(vacuum_nucleation_factor)
            ),
        }
