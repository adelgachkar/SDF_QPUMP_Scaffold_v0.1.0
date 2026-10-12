"""qpump.nodes.effective_metric_source
======================================
Effective Metric Source Node (Layer 3 - Macroscopic Metric Emergence).
Perturbs Minkowski metric via boundary stress and evaluates MOND regime.
"""

from typing import Any, Dict, List
from src.nodes.base import PlaceholderNode


class EffectiveMetricSourceNode(PlaceholderNode):
    r"""Macroscopic Metric Generator Node.

    Formulas:
        g_μν = η_μν + (2 / k_eff) * Π^(∂)_μν
        Regime evaluation: Flat galactic rotation curves emerge when I_beam ≈ S_noise.
    """

    NODE_TYPE = "effective_metric_source"

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        stress_4x4 = inputs.get("stress_tensor_4x4")
        k_eff = float(inputs.get("effective_coupling_k", 2.0e11))
        r = float(inputs.get("radial_distance", 1.0))
        noise_floor = float(inputs.get("noise_floor_amplitude", 1.0e-10))

        # Default Minkowski metric η_μν = diag(-1, 1, 1, 1)
        eta = [
            [-1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

        # Perturbed metric g_μν
        g_mu_nu: List[List[float]] = [[0.0] * 4 for _ in range(4)]
        factor = 2.0 / k_eff if k_eff != 0 else 0.0

        for i in range(4):
            for j in range(4):
                pi_val = stress_4x4[i][j] if stress_4x4 else 0.0
                g_mu_nu[i][j] = eta[i][j] + factor * pi_val

        # Beam propagation decay: 1/r^2 (Placeholder)
        beam_intensity = 1.0 / (r**2) if r > 0 else 1.0
        is_mond_active = beam_intensity <= noise_floor

        # Effective acceleration
        a_eff = (1.0 / (r**2)) if not is_mond_active else (1.0 / r)

        return {
            "metric_g_mu_nu": g_mu_nu,
            "beam_intensity": beam_intensity,
            "effective_acceleration": a_eff,
            "is_mond_active": is_mond_active,
            "calibration_status": "CALIBRATION_PENDING_USER_INPUT",
        }
