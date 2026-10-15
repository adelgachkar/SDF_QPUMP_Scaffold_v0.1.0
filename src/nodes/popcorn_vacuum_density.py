"""Popcorn Vacuum Density Node for SDF-QPUMP Framework."""
from dataclasses import dataclass
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
    def __init__(self, config: PopcornVacuumConfig | None = None):
        super().__init__()
        self.config = config or PopcornVacuumConfig()

    @staticmethod
    def compute_a0(h0_value: float) -> float:
        # H0 is given in km/s/Mpc -> convert to 1/s (SI units)
        h0_si = (h0_value * 1000.0) / (MPC_IN_KM * 1000.0)
        # a0 = c * H0 / (2 * pi) in m/s^2 (~ 1.04e-10 m/s^2)
        a0 = (C_LIGHT_M_S * h0_si) / (2.0 * np.pi)
        return float(a0)

    def compute(self, inputs: dict) -> dict:
        if not inputs or 'g_bar' not in inputs:
            raise ValueError("Input dictionary must contain 'g_bar' array.")

        g_bar = np.asarray(inputs['g_bar'], dtype=float)
        a0_early = self.compute_a0(self.config.H0_early)
        a0_local = self.compute_a0(self.config.H0_late)

        g_pop_early = np.sqrt(a0_early * g_bar)
        g_pop_local = np.sqrt(a0_local * g_bar)

        vacuum_nucleation_factor = np.sqrt(a0_local / np.maximum(g_bar, 1e-18)) * 0.5
        vacuum_nucleation_factor = np.where(g_bar > 1e-9, 0.2, vacuum_nucleation_factor)

        return {
            'a0_early': a0_early,
            'a0_local': a0_local,
            'g_pop_early': g_pop_early,
            'g_pop_local': g_pop_local,
            'vacuum_nucleation_factor': vacuum_nucleation_factor,
        }
