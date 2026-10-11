"""
Optical Phase Step Node
Step 12 in the physical-computational framework:
Applies optical phase evolution (Δphi_optical) to filtered packets
propagating through the effective cavity medium.
"""

from typing import Any, Dict, List
import numpy as np

from qpump.nodes.base import Node


class OpticalPhaseStepNode(Node):
    """
    Computes optical phase step evolution:
        phi_out = (phi_in + delta_phi) % (2 * pi)
        psi_out = A * exp(1j * phi_out)
    Where delta_phi incorporates propagation step (k * dz), frequency shift (omega * dt),
    and effective permittivity modulation.
    """

    def __init__(
        self,
        node_id: str = "optical_phase_step",
        k0: float = 1.0,
        n_eff_base: float = 1.0,
        dz_step: float = 0.1,
        omega: float = 1.0,
        dt_step: float = 0.05,
    ):
        super().__init__(node_id=node_id)
        self.k0 = float(k0)
        self.n_eff_base = float(n_eff_base)
        self.dz_step = float(dz_step)
        self.omega = float(omega)
        self.dt_step = float(dt_step)

    def compute_phase_step(self, n_eff_mod: float = 0.0) -> float:
        """
        Calculate delta_phi = k0 * (n_eff_base + n_eff_mod) * dz + omega * dt
        """
        n_eff = self.n_eff_base + n_eff_mod
        delta_phi = (self.k0 * n_eff * self.dz_step) + (self.omega * self.dt_step)
        return float(delta_phi)

    def process_packet(self, packet: Dict[str, Any], n_eff_mod: float = 0.0) -> Dict[str, Any]:
        """
        Applies optical phase advancement to a single packet.
        """
        delta_phi = self.compute_phase_step(n_eff_mod=n_eff_mod)
        initial_phase = float(packet.get("phase", 0.0))
        amplitude = float(packet.get("amplitude", packet.get("capacity", 1.0)))

        updated_phase = (initial_phase + delta_phi) % (2.0 * np.pi)
        complex_psi = amplitude * np.exp(1j * updated_phase)

        out_packet = dict(packet)
        out_packet["initial_phase"] = initial_phase
        out_packet["delta_phi"] = delta_phi
        out_packet["phase"] = updated_phase
        out_packet["amplitude"] = amplitude
        out_packet["psi_real"] = float(complex_psi.real)
        out_packet["psi_imag"] = float(complex_psi.imag)
        out_packet["optical_stepped"] = True
        return out_packet

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consumes either:
        - 'queue': list of packet dictionaries from ZAxisFilterQueueNode
        - 'packets': direct list of packets
        - 'packet': single packet
        """
        n_eff_mod = float(inputs.get("permittivity_mod", inputs.get("n_eff_mod", 0.0)))
        raw_queue = inputs.get("queue", inputs.get("packets", None))

        stepped_packets: List[Dict[str, Any]] = []

        if raw_queue is not None:
            if isinstance(raw_queue, list):
                for pkt in raw_queue:
                    if isinstance(pkt, dict):
                        stepped_packets.append(self.process_packet(pkt, n_eff_mod=n_eff_mod))
            elif isinstance(raw_queue, dict):
                stepped_packets.append(self.process_packet(raw_queue, n_eff_mod=n_eff_mod))
        elif "packet" in inputs and isinstance(inputs["packet"], dict):
            stepped_packets.append(self.process_packet(inputs["packet"], n_eff_mod=n_eff_mod))
        else:
            # Fallback direct phase field transformation
            phase = float(inputs.get("phase", 0.0))
            amp = float(inputs.get("amplitude", 1.0))
            single_pkt = {"phase": phase, "amplitude": amp}
            stepped_packets.append(self.process_packet(single_pkt, n_eff_mod=n_eff_mod))

        total_accumulated_phase = sum(p["phase"] for p in stepped_packets) if stepped_packets else 0.0

        return {
            "stepped_packets": stepped_packets,
            "packet_count": len(stepped_packets),
            "delta_phi_applied": self.compute_phase_step(n_eff_mod=n_eff_mod),
            "mean_phase": (total_accumulated_phase / len(stepped_packets)) if stepped_packets else 0.0,
            "status": "ready_for_radial_propagation",
        }
