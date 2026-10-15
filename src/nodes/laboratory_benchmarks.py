"""
laboratory_benchmarks.py
-------------------------
Implements experimental laboratory constraints for modified gravity / 
fifth-force couplings from:
1. Eöt-Wash sub-millimeter torsion balance experiments.
2. Cold-atom interferometry (Cesium / Rubidium matter-wave limits).

Calculates Yukawa deviations alpha(lambda) and checks exclusion thresholds.
"""

from typing import Dict, Any
import numpy as np
from src.nodes.base import BaseNode


class LaboratoryBenchmarksNode(BaseNode):
    """
    Evaluates experimental exclusions on Yukawa fifth-force parameter space (alpha, lambda).
    """

    def __init__(self, node_id: str = "laboratory_benchmarks"):
        super().__init__(node_id=node_id)
        # Empirical upper bounds on alpha
        self.eotwash_limit_alpha = 1e-2  # Eöt-Wash bound around lambda ~ 50 um
        self.cold_atom_limit_alpha = 5e-2  # Cold atom bound around 10 um

    def yukawa_acceleration_ratio(self, r: float, alpha: float, lambd: float) -> float:
        """
        Computes the ratio of fifth-force acceleration to Newtonian acceleration:
        g_5 / g_N = alpha * (1 + r / lambda) * exp(-r / lambda)
        """
        if lambd <= 0.0 or r <= 0.0:
            return 0.0
        x = r / lambd
        return float(alpha * (1.0 + x) * np.exp(-x))

    def evaluate_exclusion(self, alpha: float, lambd: float) -> Dict[str, Any]:
        """
        Determines whether a candidate (alpha, lambda) configuration is ruled out
        by laboratory experiments.
        """
        is_eotwash_excluded = False
        is_cold_atom_excluded = False

        # Eöt-Wash sensitivity domain: 40 um to 10 mm
        if 4e-5 <= lambd <= 1e-2:
            if alpha > self.eotwash_limit_alpha:
                is_eotwash_excluded = True

        # Cold-atom interferometry sensitivity domain: 1 um to 100 um
        if 1e-6 <= lambd <= 1e-4:
            if alpha > self.cold_atom_limit_alpha:
                is_cold_atom_excluded = True

        status = "COMPLIANT"
        if is_eotwash_excluded or is_cold_atom_excluded:
            status = "EXCLUDED_BY_LABORATORY"

        return {
            "alpha": alpha,
            "lambda_m": lambd,
            "eotwash_excluded": is_eotwash_excluded,
            "cold_atom_excluded": is_cold_atom_excluded,
            "experimental_status": status
        }

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard BaseNode execution contract.
        """
        alpha = float(inputs.get("alpha", 1e-3))
        lambd = float(inputs.get("screening_length", 5e-5))

        eval_result = self.evaluate_exclusion(alpha=alpha, lambd=lambd)
        ratio_at_char_dist = self.yukawa_acceleration_ratio(r=lambd, alpha=alpha, lambd=lambd)

        return {
            "benchmark_eval": eval_result,
            "yukawa_force_ratio_at_screening_radius": ratio_at_char_dist,
            "node_status": "SUCCESS"
        }
