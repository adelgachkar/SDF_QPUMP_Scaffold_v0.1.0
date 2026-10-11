"""
Radial Propagation Engine Node
Step 13 in the physical-computational framework:
Propagates phase-stepped quantum packets along the radial direction r_hat,
modeling spherical divergence, geometric attenuation, and radial flux density.
"""

from typing import Any, Dict, List
import numpy as np

from qpump.nodes.base import Node


class RadialPropagationNode(Node):
    """
    Executes radial transport along r_hat:
      r_new = r_old + delta_r
      A_new = A_old * (r_old / r_new)^alpha_div * exp(-gamma_loss * delta_r)
      phi_new = (phi_old + k_radial * delta_r) % (2 * pi)
      J_r = (A_new ** 2) * k_radial (radial probability/wave flux)
    """

    def __init__(
        self,
        node_id: str = "radial_propagation",
        delta_r: float = 0.1,
        k_radial: float = 1.0,
        alpha_div: float = 0.5,
        gamma_loss: float = 0.02,
        r_min: float = 0.05,
    ):
        super().__init__(node_id=node_id)
        self.delta_r = float(delta_r)
        self.k_radial = float(k_radial)
        self.alpha_div = float(alpha_div)
        self.gamma_loss = float(gamma_loss)
        self.r_min = float(r_min)

    def propagate_packet(self, packet: Dict[str, Any], delta_r_override: float = None) -> Dict[str, Any]:
        dr = self.delta_r if delta_r_override is None else float(delta_r_override)

        if "r" in packet:
            r_current = max(self.r_min, float(packet["r"]))
        elif all(k in packet for k in ("x", "y", "z")):
            x, y, z = float(packet["x"]), float(packet["y"]), float(packet["z"])
            r_current = max(self.r_min, float(np.sqrt(x**2 + y**2 + z**2)))
        else:
            r_current = 1.0

        r_new = r_current + dr

        amp_in = float(packet.get("amplitude", 1.0))
        phase_in = float(packet.get("phase", 0.0))

        # Geometric divergence and absorption attenuation
        geom_factor = (r_current / r_new) ** self.alpha_div
        loss_factor = np.exp(-self.gamma_loss * dr)
        amp_out = amp_in * geom_factor * loss_factor

        # Radial wavevector phase evolution
        dphi_r = self.k_radial * dr
        phase_out = (phase_in + dphi_r) % (2.0 * np.pi)

        # Complex state psi and radial flux current J_r
        psi_out = amp_out * np.exp(1j * phase_out)
        j_radial = (amp_out ** 2) * self.k_radial

        out_packet = dict(packet)
        out_packet["r_initial"] = r_current
        out_packet["r"] = float(r_new)
        out_packet["delta_r"] = dr
        out_packet["amplitude"] = float(amp_out)
        out_packet["phase"] = float(phase_out)
        out_packet["psi_real"] = float(psi_out.real)
        out_packet["psi_imag"] = float(psi_out.imag)
        out_packet["radial_flux_jr"] = float(j_radial)
        out_packet["radial_propagated"] = True

        return out_packet

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raw_packets = inputs.get(
            "stepped_packets",
            inputs.get("queue", inputs.get("packets", None)),
        )
        dr_mod = inputs.get("delta_r", None)

        results: List[Dict[str, Any]] = []

        if raw_packets is not None:
            if isinstance(raw_packets, list):
                for pkt in raw_packets:
                    if isinstance(pkt, dict):
                        results.append(self.propagate_packet(pkt, delta_r_override=dr_mod))
            elif isinstance(raw_packets, dict):
                results.append(self.propagate_packet(raw_packets, delta_r_override=dr_mod))
        elif "packet" in inputs and isinstance(inputs["packet"], dict):
            results.append(self.propagate_packet(inputs["packet"], delta_r_override=dr_mod))
        else:
            default_pkt = {"amplitude": 1.0, "phase": 0.0, "r": 1.0}
            results.append(self.propagate_packet(default_pkt, delta_r_override=dr_mod))

        total_flux = sum(p["radial_flux_jr"] for p in results) if results else 0.0
        mean_r = (sum(p["r"] for p in results) / len(results)) if results else 0.0

        return {
            "propagated_packets": results,
            "packet_count": len(results),
            "total_radial_flux": float(total_flux),
            "mean_radius": float(mean_r),
            "status": "radial_propagation_complete",
        }
