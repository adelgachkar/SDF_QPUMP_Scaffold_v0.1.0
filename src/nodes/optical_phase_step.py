"""
Step 12: Optical Phase Stepper Node.
Applies discrete phase advancement and dispersion evolution.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List
from src.nodes.base import Node


class OpticalPhaseStepNode(Node):
    def __init__(
        self,
        node_id: str = "optical_phase_step_01",
        k0: float = 1.0,
        n_eff_base: float = 1.5,
        dz_step: float = 0.1,
        omega: float = 1.0,
        dt_step: float = 0.01,
        name: str | None = None,
    ):
        super().__init__(node_id=node_id, name=name)
        self.k0 = float(k0)
        self.n_eff_base = float(n_eff_base)
        self.dz_step = float(dz_step)
        self.omega = float(omega)
        self.dt_step = float(dt_step)

    def compute_phase_step(self, permittivity_mod: float = 0.0) -> float:
        # delta_phi = (k0 * (n_eff_base + mod) * dz) + (omega * dt)
        n_eff = self.n_eff_base + float(permittivity_mod)
        return (self.k0 * n_eff * self.dz_step) + (self.omega * self.dt_step)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        permittivity_mod = float(inputs.get("permittivity_mod", 0.0))
        dphi = self.compute_phase_step(permittivity_mod)

        # Handle multiple packets from queue
        if "queue" in inputs:
            packets = inputs["queue"]
            processed: List[Dict[str, Any]] = []
            for pkt in packets:
                p = dict(pkt)
                phase_val = float(p.get("phase", 0.0))
                p["phase"] = (phase_val + dphi) % (2.0 * math.pi)
                p["optical_stepped"] = True
                p["delta_phi"] = dphi
                processed.append(p)
            return {
                "queue": processed,
                "stepped_packets": processed,
                "packet_count": len(processed),
                "delta_phi": dphi,
                "delta_phi_applied": dphi,
                "status": "ready_for_radial_propagation"
            }

        # Handle single packet either inside 'packet' or flat inputs
        pkt = dict(inputs.get("packet", inputs))
        phase_in = float(pkt.get("phase", pkt.get("bare_phase", 0.0)))
        amp = float(pkt.get("amplitude", 1.0))
        new_phase = (phase_in + dphi) % (2.0 * math.pi)

        out_pkt = dict(pkt)
        out_pkt["phase"] = new_phase
        out_pkt["accumulated_phase"] = new_phase
        out_pkt["amplitude"] = amp
        out_pkt["delta_phi"] = dphi
        out_pkt["optical_stepped"] = True

        return {
            "phase": new_phase,
            "accumulated_phase": new_phase,
            "amplitude": amp,
            "delta_phi": dphi,
            "delta_phi_applied": dphi,
            "packet": out_pkt,
            "stepped_packets": [out_pkt],
            "packet_count": 1,
            "status": "ready_for_radial_propagation"
        }
