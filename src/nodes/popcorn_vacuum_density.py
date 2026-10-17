"""Popcorn Vacuum Density Node for Hubble tension and dark energy scale correspondence."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union
import numpy as np
from src.nodes.base import Node

# Physical constants and cosmological benchmarks
H0_EARLY_DEFAULT = 67.4   # km/s/Mpc (Planck CMB scale)
H0_LOCAL_DEFAULT = 73.04  # km/s/Mpc (SH0ES local ladder)
MPC_IN_METERS = 3.085677581491367e22  # 1 Mpc in meters (SI)
C_LIGHT_M_S = 299792458.0             # Speed of light in m/s


@dataclass
class PopcornVacuumConfig:
    node_id: str = "popcorn_vacuum_density"
    H0_early: float = H0_EARLY_DEFAULT
    H0_late: float = H0_LOCAL_DEFAULT
    lambda_coh_kpc: float = 12.0
    vacuum_energy_density: float = 5.35e-10
    extra: Dict[str, Any] = field(default_factory=dict)


class PopcornVacuumDensityNode(Node):
    type_name = "popcorn_vacuum_density"

    def __init__(self, name: str | None = None, **kwargs):
        node_name = kwargs.pop("node_id", None) or name or "popcorn_vacuum_density"
        super().__init__(name=node_name)
        self.node_id = node_name
        self.name = node_name
        self.H0_early = float(kwargs.pop("H0_early", H0_EARLY_DEFAULT))
        self.H0_late = float(kwargs.pop("H0_late", H0_LOCAL_DEFAULT))
        self.lambda_coh_kpc = float(kwargs.pop("lambda_coh_kpc", 12.0))
        self.config_kwargs = kwargs

    @staticmethod
    def compute_a0(h0_value: float) -> float:
        """Compute the critical MOND-like acceleration scale a0 = c * H0 / 2pi in SI units (m/s^2)."""
        # H0 is in (km/s)/Mpc -> (H0 * 1000 m/s) / (MPC_IN_METERS) gives 1/s
        h0_si = (float(h0_value) * 1000.0) / MPC_IN_METERS
        return (C_LIGHT_M_S * h0_si) / (2.0 * np.pi)

    def compute(self, inputs: Dict[str, Any] | None = None) -> Dict[str, Any]:
        inputs = inputs or {}

        if "g_bar" not in inputs:
            raise ValueError("PopcornVacuumDensityNode requires 'g_bar' in inputs.")

        raw_g_bar = inputs["g_bar"]
        is_array = isinstance(raw_g_bar, (list, tuple, np.ndarray))
        g_bar = np.asarray(raw_g_bar, dtype=np.float64)

        a0_early = self.compute_a0(self.H0_early)
        a0_local = self.compute_a0(self.H0_late)

        # Nucleation factor scaling inversely with baryonic acceleration
        # High g_bar -> minimal vacuum compensation (< 0.5)
        # Deep vacuum g_bar -> dominant popcorn nucleation (> 5.0)
        vacuum_nucleation_factor = np.sqrt(a0_local / np.maximum(g_bar, 1e-15))

        g_pop_early = np.sqrt(np.maximum(g_bar * a0_early, 0.0))
        g_pop_local = np.sqrt(np.maximum(g_bar * a0_local, 0.0))

        if is_array:
            vnf_out = vacuum_nucleation_factor
            g_early_out = g_pop_early
            g_local_out = g_pop_local
        else:
            vnf_out = float(vacuum_nucleation_factor)
            g_early_out = float(g_pop_early)
            g_local_out = float(g_pop_local)

        return {
            "a0_early": a0_early,
            "a0_local": a0_local,
            "vacuum_nucleation_factor": vnf_out,
            "g_pop_early": g_early_out,
            "g_pop_local": g_local_out,
        }
