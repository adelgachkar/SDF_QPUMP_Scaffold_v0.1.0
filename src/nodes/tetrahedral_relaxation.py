"""
Tetrahedral Cluster Stress Dynamic Relaxation Node
Part of the SDF-QPUMP Computational Scaffold.

Models the non-equilibrium relaxation dynamics of geometric frustration stress
induced by the 5-tetrahedral dimensional gap resolution.
"""

import math
from typing import Dict, Any, List
from .base import Node


class TetrahedralRelaxationNode(Node):
    """
    Simulates time-dependent relaxation of frustration stress toward the geometric
    attractor state dictated by FiveTetrahedralUnionNode.
    """

    def __init__(
        self,
        node_id: str = "tetrahedral_relaxation",
        label: str = "Tetrahedral Dynamic Relaxation",
        config: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(node_id=node_id, label=label, config=config, **kwargs)
        cfg = self.config or {}
        # Relaxation rate Gamma = 1 / tau (default 0.1 rad/step)
        self.gamma = float(cfg.get("relaxation_rate", 0.1))
        # Default step size for propagation
        self.dt = float(cfg.get("dt", 0.05))
        # Persistent state for dynamic tracking
        self._current_stress: float = 0.0
        self._is_initialized: bool = False

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes dynamic relaxation from target static stress and drive inputs.

        Expected inputs:
            - frustration_stress: Target equilibrium stress (from FiveTetrahedralUnionNode)
            - dt: (Optional) Step size override
            - drive_perturbation: (Optional) Exogenous driving amplitude (e.g. from cavity)
            - n_steps: (Optional) Multi-step internal propagation steps (default: 1)
        """
        if "frustration_stress" not in inputs:
            raise ValueError(f"[{self.node_id}] Missing required input 'frustration_stress'.")

        target_stress = float(inputs["frustration_stress"])
        dt = float(inputs.get("dt", self.dt))
        drive = float(inputs.get("drive_perturbation", 0.0))
        n_steps = int(inputs.get("n_steps", 1))

        if dt <= 0.0:
            raise ValueError(f"[{self.node_id}] Step size 'dt' must be strictly positive.")

        # Initialize to target stress if first invocation
        if not self._is_initialized:
            self._current_stress = float(inputs.get("initial_stress", target_stress))
            self._is_initialized = True

        stress_trace: List[float] = [self._current_stress]

        # Analytical step-wise integration: dS/dt = -Gamma*(S - S_target) + drive
        decay_factor = math.exp(-self.gamma * dt)
        for _ in range(n_steps):
            delta = self._current_stress - target_stress
            # Analytical evolution with constant drive across dt
            if self.gamma > 1e-12:
                driven_equilibrium = target_stress + (drive / self.gamma)
                self._current_stress = (
                    driven_equilibrium + (self._current_stress - driven_equilibrium) * decay_factor
                )
            else:
                self._current_stress += drive * dt

            stress_trace.append(self._current_stress)

        residual_frustration = abs(self._current_stress - target_stress)
        equilibrium_ratio = 1.0 - (residual_frustration / (abs(target_stress) + 1e-12))

        return {
            "dynamic_stress": float(self._current_stress),
            "target_stress": float(target_stress),
            "residual_frustration": float(residual_frustration),
            "equilibrium_ratio": float(max(0.0, min(1.0, equilibrium_ratio))),
            "relaxation_rate": float(self.gamma),
            "stress_trace": stress_trace,
        }
