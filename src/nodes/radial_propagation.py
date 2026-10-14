"""
Step 13: Radial Propagation Node.
Simulates outward wavefront propagation and geometric attenuation.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List
from src.nodes.base import Node


class RadialPropagationNode(Node):
    def __init__(
        self,
        node_id: str = "radial_propagation_01",
        delta_r: float = 0.1,
        k_radial: float = 1.0,
        alpha_div: float = 0.5,
        gamma_loss: float = 0.0,
        r_min: float = 0.1,
        name: str | None = None,
    ):
        super().__init__(node_id=node_id, name=name)
        self.delta_r = float(delta_r)
        self.k_radial = float(k_radial)
        self.alpha_div = float(alpha_div)
        self.gamma_loss = float(gamma_loss)
        self.r_min = float(r_min)

    def _propagate_single(self, pkt: Dict[str, Any]) -> Dict[str, Any]:
        p = dict(pkt)
        r = float(p.get("r", p.get("radius", self.r_min)))
        r_curr = max(r, self.r_min)
        amp = float(p.get("amplitude", 1.0))
        phase = float(p.get("phase", 0.0))

        r_next = r_curr + self.delta_r
        geom = (r_curr / r_next) ** self.alpha_div
        loss = math.exp(-self.gamma_loss * self.delta_r)
        amp_next = amp * geom * loss
        phase_next = (phase + self.k_radial * self.delta_r) % (2.0 * math.pi)

        p["r"] = r_next
        p["radius"] = r_next
        p["amplitude"] = amp_next
        p["phase"] = phase_next
        p["radial_propagated"] = True
        return p

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Handle queue input or piped list from optical step (queue or stepped_packets)
        packet_list = None
        if "queue" in inputs and isinstance(inputs["queue"], list):
            packet_list = inputs["queue"]
        elif "stepped_packets" in inputs and isinstance(inputs["stepped_packets"], list):
            packet_list = inputs["stepped_packets"]

        if packet_list is not None:
            processed = [self._propagate_single(pkt) for pkt in packet_list]
            total_flux = sum(float(p.get("amplitude", 0.0)) ** 2 for p in processed)
            return {
                "queue": processed,
                "propagated_packets": processed,
                "packet_count": len(processed),
                "total_radial_flux": total_flux,
                "status": "radial_propagation_complete"
            }

        # Handle single packet
        pkt = inputs.get("packet", inputs)
        propagated = self._propagate_single(pkt)
        amp = float(propagated.get("amplitude", 0.0))
        total_flux = amp ** 2
        return {
            "r": propagated.get("r"),
            "radius": propagated.get("radius"),
            "amplitude": propagated.get("amplitude"),
            "phase": propagated.get("phase"),
            "packet": propagated,
            "propagated_packets": [propagated],
            "packet_count": 1,
            "total_radial_flux": total_flux,
            "status": "radial_propagation_complete"
        }
