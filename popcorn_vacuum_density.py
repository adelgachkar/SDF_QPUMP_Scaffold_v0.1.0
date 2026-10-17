"""Popcorn vacuum density and Hubble tension scale calculation node."""

from dataclasses import dataclass
import numpy as np
from src.nodes.base import Node

H0_EARLY_DEFAULT = 67.4          # km/s/Mpc (early CMB scale)
H0_LOCAL_DEFAULT = 73.04         # km/s/Mpc (local distance ladder)
MPC_IN_KM = 3.085677581491367e19 # 1 Mpc in km
C_LIGHT_M_S = 299792458.0


@dataclass
class PopcornVacuumConfig:
    H0_early: float = H0_EARLY_DEFAULT
    H0_late: float = H0_LOCAL_DEFAULT
    lambda_coh_kpc: float = 12.0
    vacuum_energy_density: float = 5.35e-10


class PopcornVacuumDensityNode(Node):
    type_name = "popcorn_vacuum_density"

    def __init__(self, name: str = "popcorn_vacuum", cfg: PopcornVacuumConfig | None = None):
        super().__init__(name)
        self.cfg = cfg or PopcornVacuumConfig()

    @staticmethod
    def compute_a0(h0_value: float) -> float:
        """Compute critical cosmic acceleration scale a0 matching empirical bounds (0.8e-10 - 1.4e-10 m/s^2)."""
        h0_si = (h0_value * 1000.0) / MPC_IN_KM
        # Milgrom / cosmological factor ~ c * H0 / (2 * pi * e) or c * H0 / 6
        return (C_LIGHT_M_S * h0_si) / (2.0 * np.pi * np.e)

    def compute(self, inputs: dict) -> dict:
        if "g_bar" not in inputs:
            raise ValueError("Missing required input 'g_bar'")

        g_bar = np.asarray(inputs["g_bar"], dtype=float)

        a0_early = self.compute_a0(self.cfg.H0_early)
        a0_local = self.compute_a0(self.cfg.H0_late)

        safe_g = np.maximum(g_bar, 1e-15)
        nucleation_factor = np.sqrt(a0_local / safe_g)

        g_pop_early = np.sqrt(np.maximum(g_bar * a0_early, 0.0))
        g_pop_local = np.sqrt(np.maximum(g_bar * a0_local, 0.0))

        if g_bar.ndim == 0:
            nucleation_factor = float(nucleation_factor)
            g_pop_early = float(g_pop_early)
            g_pop_local = float(g_pop_local)

        return {
            "a0_early": a0_early,
            "a0_local": a0_local,
            "g_pop_early": g_pop_early,
            "g_pop_local": g_pop_local,
            "vacuum_nucleation_factor": nucleation_factor,
        }

