"""
Z-Axis Filter & Queue Node for Q-PUMP Pipeline.
Propagates, filters, and queues emergent cavity jet flux along the longitudinal Z-axis
based on boundary impedance and logistic beam stabilization.
"""

from typing import Any, Dict, List, Optional
import numpy as np

from qpump.nodes.base import Node


class ZAxisFilterQueueNode(Node):
    """
    Filters and queues the directional flux emitted along the Z-axis.

    Inputs:
        - screened_phase (float or list/np.ndarray): Phase or state vector from cavity.
        - intensity (float or list/np.ndarray): Input flux intensity.
        - z_steps (list or np.ndarray, optional): Spatial propagation points along z.
        - r_wall (float, optional): Cavity wall reflectivity (default 0.9).
        - alpha_growth (float, optional): Logistic growth rate (default 0.5).
        - queue_capacity (int, optional): Maximum capacity of the output queue.

    Outputs:
        - filtered_modes: Final stabilized mode amplitudes.
        - snr_profile: Signal-to-noise ratio along z-propagation steps.
        - z_queue_state: Buffered and ordered mode states.
        - effective_axial_flux: Integrated axial flux reaching the queue output.
    """

    def __init__(
        self,
        node_id: str = "z_axis_filter_queue",
        label: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(node_id=node_id, label=label, config=config)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        intensity_in = inputs.get("intensity", inputs.get("jet_flux", 1.0))
        phase_in = inputs.get("screened_phase", 0.0)

        # Config or input parameters
        r_wall = float(inputs.get("r_wall", self.config.get("r_wall", 0.9)))
        alpha = float(inputs.get("alpha_growth", self.config.get("alpha_growth", 0.5)))
        queue_cap = int(inputs.get("queue_capacity", self.config.get("queue_capacity", 16)))

        # Boundary pressure factor from VLT boundary interaction: 1 / (1 - r_wall^2)
        clamped_r = min(max(r_wall, 0.0), 0.999)
        resonance_gain = 1.0 / (1.0 - (clamped_r ** 2))

        # Spatial discretization along Z
        z_steps = inputs.get("z_steps", None)
        if z_steps is None:
            z_arr = np.linspace(0.0, 5.0, 50)
        else:
            z_arr = np.asarray(z_steps, dtype=float)

        # Base amplitude array
        if np.isscalar(intensity_in):
            psi_0 = np.array([float(intensity_in)], dtype=float)
        else:
            psi_0 = np.asarray(intensity_in, dtype=float).flatten()

        if psi_0.size == 0:
            psi_0 = np.array([1.0], dtype=float)

        # Longitudinal propagation along Z: logistic saturation + boundary impedance gain
        # dpsi / dz = alpha * psi * (1 - psi / (K * psi_0))
        psi_current = np.copy(psi_0)
        snr_history: List[float] = []

        dz = (z_arr[-1] - z_arr[0]) / max(len(z_arr) - 1, 1) if len(z_arr) > 1 else 0.1

        for _ in z_arr:
            saturation_cap = np.maximum(psi_0 * resonance_gain, 1e-6)
            dpsi = alpha * psi_current * (1.0 - (psi_current / saturation_cap)) * dz
            psi_current = np.maximum(psi_current + dpsi, 0.0)

            # Calculate SNR profile
            mean_val = float(np.mean(psi_current))
            noise_std = float(np.std(psi_current))
            snr = (mean_val / (noise_std + 1e-9)) if noise_std > 0 else 50.0
            snr_history.append(float(snr))

        filtered_modes = psi_current.tolist()

        # Phase modulation adjustment
        if isinstance(phase_in, (int, float)):
            effective_phase = float(phase_in)
        else:
            effective_phase = float(np.mean(phase_in))

        # Build priority queue buffer ordered by amplitude
        queue_items = sorted(
            [
                {"mode_idx": i, "amplitude": float(val), "phase": effective_phase}
                for i, val in enumerate(filtered_modes)
            ],
            key=lambda item: item["amplitude"],
            reverse=True,
        )
        z_queue_state = queue_items[:queue_cap]

        effective_axial_flux = float(np.sum(filtered_modes))

        return {
            "filtered_modes": filtered_modes,
            "snr_profile": snr_history,
            "z_queue_state": z_queue_state,
            "effective_axial_flux": effective_axial_flux,
            "resonance_gain": float(resonance_gain),
        }
